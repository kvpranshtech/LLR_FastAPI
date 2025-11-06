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
from core.models import CsvFile
from requests import request as SEND_REQUEST
import math
import json
from functools import reduce
from utils.handle_logs import create_log_
from django.core.paginator import Paginator
from utils.utils_helpers import get_proxy_settings
os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
wavix_logger = logging.getLogger('wavix_logger')
wavix_handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'wavix_bulk_validation.log'))
wavix_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
wavix_handler.setFormatter(wavix_formatter)
wavix_logger.addHandler(wavix_handler)
wavix_logger.setLevel(logging.INFO)

WAVIX_APPID = settings.WAVIX_APPID


class API_WAVIX_BULK:
    def __init__(self):
        # Get proxy settings
        proxy_domain, proxy_token, server_ip = get_proxy_settings()
        
        # Setup headers for proxy authentication
        self.headers = {
            "X-Server-IP": server_ip,
            "Authorization": f"Bearer {proxy_token}",
            "Content-Type": "application/json",
        }
        
        # Proxy endpoints
        self.batch_url = f"{proxy_domain}/wavix-bulk-submit-proxy/"
        self.poll_url = f"{proxy_domain}/wavix-bulk-poll-proxy/"
        
        self.TOLL_FREE_PREFIXES = ("800", "888", "877", "866", "855", "844", "833")
        self.return_dict = []
        
        wavix_logger.info("Using Wavix Proxy Server")

    def createSmallList(self, numbers,file_uid):
        paginator = Paginator(numbers, 900)
        for page in range(1, paginator.num_pages + 1):
            numbers_list = paginator.page(page).object_list
            token = self.submit_batch(numbers_list,file_uid)
            if token:
                batch_results = self.poll_results(token, file_uid)
                if batch_results:
                    wavix_logger.info(f"Batch processed successfully")
                else:
                    wavix_logger.warning(f"No results returned for batch")

        return self.return_dict

    def get_invalid_number_info(self, phone_clean):
        return True if len(phone_clean) == 11 and (phone_clean[1] == ("1") or phone_clean[1] == ("0")) else False
    
    def get_csv_object(self,file_uid):
        try:
            csvfile = CsvFile.objects.get(uid=file_uid)
            return csvfile
        except Exception as e:
            wavix_logger.error(f"CSV FILE OBJECT NOT FOUND WHILE UPATING BATCHES {e}")

    
    def submit_batch(self, numbers_list, file_uid):
        filtered_numbers = []  

        for number in numbers_list:
            if number.startswith(self.TOLL_FREE_PREFIXES):
                self.return_dict.append({
                    'number': number,
                    'line_type': 'toll_free',
                    'carrier_name': 'n/a',
                    'city': 'n/a',
                    'state': 'n/a',
                    'country': 'us',
                })
            elif self.get_invalid_number_info(number):
                self.return_dict.append({
                    'number': number,
                    'line_type_original': 'starts_with_1_or_0',
                    'line_type': 'invalid',
                    'carrier_name': 'n/a',
                    'city': 'n/a',
                    'state': 'n/a',
                    'country': 'us',
                })
            else:
                filtered_numbers.append(number) 

        try:
            # Send to proxy server
            payload = {"phone_numbers": filtered_numbers}
            response = requests.post(self.batch_url, headers=self.headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            data = response.json()
            token = data.get("request_uuid")

            WavixBatchRequest.objects.create(
                csvfile=self.get_csv_object(file_uid),
                requested_data=",".join(filtered_numbers),
                token=token,
                status=WavixBatchRequest.RequestStatus.STARTED
            )
            return token
        except Exception as e:
            create_log_(
                log_type='wavix_bulk',
                message=f"WAVIX BULK API wasn't able to serve request",
                exception_message=str(e)
            )


    def poll_results(self,token, file_uid,max_retries=5, retry_backoff=30):
        # Call proxy server for polling
        payload = {"token": token}

        batch_request = WavixBatchRequest.objects.filter(token=token, csvfile=self.get_csv_object(file_uid)).first()

        if batch_request:
            batch_request.status = WavixBatchRequest.RequestStatus.PROCESSING
            batch_request.save()
        
        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(self.poll_url, headers=self.headers, data=json.dumps(payload), timeout=120)
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
                            city, state = self.get_city_state(cleaned_number[:3])
                            line_type = str(item.get('number_type', 'unknown')).strip().lower()
                            
                            self.return_dict.append({
                            'number': cleaned_number,
                            'line_type': line_type,
                            'carrier_name': carrier_name,
                            'city': city,
                            'state': state,
                            'country': 'us',
                        })

                        except Exception as e:
                            print(f"Error processing record {item}: {e}")
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
            # time.sleep(retry_backoff)
        
        wavix_logger.error(f"Max retries reached for token {token}. Marking as failed.")
        if batch_request:
            batch_request.status = WavixBatchRequest.RequestStatus.FAILED
            batch_request.save()
        return None
    

    def get_city_state(self,area_code):
        state, city_list = city_state_data.get(area_code, ("n/a", ["n/a"]))
        random_city = random_choice(city_list)
        return str(random_city).lower(), get_state(str(state).lower()).strip()
                    

    
