import logging
import os
import time
import requests
from django.conf import settings
from datastorage.models import WavixBatchRequest
from utils._data_netnumbering import city_state_data
from utils._base import get_state
from random import choice as random_choice
from utils.handle_saving_data import saveWavixData,saveWavixDataV2
from django.utils.timezone import now
import math

os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
wavix_logger = logging.getLogger('wavix_logger')
wavix_handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'wavix_bulk_validation.log'))
wavix_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
wavix_handler.setFormatter(wavix_formatter)
wavix_logger.addHandler(wavix_handler)
wavix_logger.setLevel(logging.INFO)

WAVIX_APPID = settings.WAVIX_APPID
RESULT_POLL_INTERVAL = 30
TOLL_FREE_PREFIXES = ("800", "888", "877", "866", "855", "844", "833")

def get_phone_info(phone_number):
    """
    Returns a dictionary containing phone information.
    """
    return_dict = {
        'number': phone_number,
        'line_type': 'invalid',
        'carrier_name': 'n/a',
        'city': 'n/a',
        'state': 'n/a',
        'country': 'us',
    }

    return_dict['line_type'] = 'toll_free'
    saveWavixData(return_dict)
    return None

def SaveDataInWavixDB(phone_number, carrier_name, city, state, line_type):
    records_to_create = []

    return_dict = {
        'number': phone_number,
        'line_type': line_type,
        'carrier_name': carrier_name,
        'city': city,
        'state': state,
        'country': 'us',
    }
    
    records_to_create.append(return_dict)
    
    saveWavixDataV2(records_to_create)
    return None

def get_invalid_number_info(phone_clean):
    if len(phone_clean) == 10 and (phone_clean.startswith("1") or phone_clean.startswith("0")):
        return_dict = {
            'number': phone_clean,
            'line_type_original': 'starts_with_1_or_0',
            'line_type': 'invalid',
            'carrier_name': 'n/a',
            'city': 'n/a',
            'state': 'n/a',
            'country': 'us',
        }
        saveWavixData(return_dict)
        return True
    return False

def get_city_state(area_code):
    state, city_list = city_state_data.get(area_code, ("n/a", ["n/a"]))
    random_city = random_choice(city_list)
    return str(random_city).lower(), get_state(str(state).lower()).strip()

def submit_batch(phone_numbers, csvfile):
    url = f"https://api.wavix.com/v1/validation?appid={WAVIX_APPID}"
    headers = {'Content-Type': 'application/json'}
    toll_free_numbers = []
    non_toll_free_numbers = []
    invalid_numbers = []

    for number in phone_numbers:
        if number.startswith(TOLL_FREE_PREFIXES):
            toll_free_numbers.append(get_phone_info(number))
        elif get_invalid_number_info(number):
            invalid_numbers.append(number)
        else:
            non_toll_free_numbers.append(number)

    if toll_free_numbers:
        wavix_logger.info(f"Toll-free numbers identified and excluded from API call: {toll_free_numbers}")

    if not non_toll_free_numbers:
        wavix_logger.info("No non-toll-free numbers to process in this batch.")
        return None

    payload = {"phone_numbers": non_toll_free_numbers, "type": "analysis", "async": True}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        token = data.get("request_uuid")

        WavixBatchRequest.objects.create(
            csvfile=csvfile,
            requested_data=",".join(non_toll_free_numbers),
            token=token,
            status=WavixBatchRequest.RequestStatus.STARTED
        )

        return token
    except requests.exceptions.RequestException as e:
        wavix_logger.error(f"Error submitting batch: {str(e)}")
        return None



def poll_results(token, csvfile, tracker_object, max_retries=5, retry_backoff=RESULT_POLL_INTERVAL):
    """
    Poll the Wavix API for validation results, with retries until success or max retries are reached.
    """
    url = f"https://api.wavix.com/v1/validation/{token}?appid={WAVIX_APPID}"
    headers = {'Content-Type': 'application/json'}
    batch_request = WavixBatchRequest.objects.filter(token=token, csvfile=csvfile).first()

    if batch_request:
        batch_request.status = WavixBatchRequest.RequestStatus.PROCESSING
        batch_request.save()

    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success" and len(data.get("items", [])) > 0:
                wavix_logger.info(f"data recieved from wavix - {data.get('count','0')} - for {token}")
                if batch_request:
                    batch_request.status = WavixBatchRequest.RequestStatus.COMPLETED
                    batch_request.save()

                for item in data.get("items", []):
                    try:
                        carrier_name = str(item.get('carrier_name', 'unknown')).strip().lower()
                        phone_number = str(item.get('phone_number'))
                        cleaned_number = phone_number[2:]
                        city, state = get_city_state(cleaned_number[:3])
                        line_type = str(item.get('number_type', 'unknown')).strip().lower()

                        SaveDataInWavixDB(cleaned_number, carrier_name, city, state, line_type)
                    except Exception as e:
                        print(f"Error processing record {item}: {e}")


                total_numbers = int(tracker_object.proccessed_batches) + 1
                tracker_object.proccessed_batches = str(total_numbers)
                tracker_object.save()
                return True

            elif data.get("status") in ["failed", "false", False]:
                if batch_request:
                    batch_request.status = WavixBatchRequest.RequestStatus.FAILED
                    batch_request.save()
                wavix_logger.error(f"Validation failed for token {token}")
                return []

            wavix_logger.info(f"Intermediate status for token {token}: {data.get('status')}")
        except requests.exceptions.RequestException as e:
            wavix_logger.error(f"Error polling results for token {token}: {str(e)}")
        
        retries += 1
        time.sleep(retry_backoff)
    
    wavix_logger.error(f"Max retries reached for token {token}. Marking as failed.")
    if batch_request:
        batch_request.status = WavixBatchRequest.RequestStatus.FAILED
        batch_request.save()
    return None


def validate_phone_numbers(phone_numbers, csvfile,tracker_object):
    total_numbers = len(phone_numbers)
    wavix_logger.info(f"Starting validation for {total_numbers} phone numbers")

    # if total_numbers <= 1000:
    #     batch_size = total_numbers
    #     total_batches = 1
    # else:
    #     total_batches = min(10, total_numbers // 1000)  
    #     batch_size = max(1000, total_numbers // total_batches) 

    max_batch_size = 1000 

    total_batches = math.ceil(total_numbers / max_batch_size)  
    batch_size = math.ceil(total_numbers / total_batches)


    wavix_logger.info(f"Total batches: {total_batches}, Batch size: {batch_size}")
    tracker_object.number_of_batch = str(total_batches)
    tracker_object.save()

    for i in range(0, total_numbers, batch_size):
        batch = phone_numbers[i:i + batch_size]
        batch_index = i // batch_size + 1
        wavix_logger.info(f"Submitting batch {batch_index}, size: {len(batch)}")

        if not batch:
            wavix_logger.info(f"No numbers to process in batch {batch_index}. Skipping...")
            continue

        try:
            token = submit_batch(batch, csvfile)
            if token:
                batch_results = poll_results(token, csvfile, tracker_object)
                if batch_results:
                    wavix_logger.info(f"Batch {batch_index} processed successfully")
                else:
                    wavix_logger.warning(f"No results returned for batch {batch_index}")
            else:
                wavix_logger.error(f"Failed to submit batch {batch_index}")
        except Exception as e:
            wavix_logger.error(f"Error processing batch {batch_index}: {str(e)}")

    wavix_logger.info(f"Validation completed for {total_numbers} phone numbers")
    return None