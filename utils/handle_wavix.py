import logging
import os
from django.conf import settings
import requests

os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
# Configure method1 logger
wavix_logger = logging.getLogger('wavix_logger')
wavix_handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'wavix.log'))
wavix_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
wavix_handler.setFormatter(wavix_formatter)
wavix_logger.addHandler(wavix_handler)
wavix_logger.setLevel(logging.INFO)



"""
    - new script in oct 23
"""

from requests import request as SEND_REQUEST
import json
from django.conf import settings
from random import choice as random_choice 

from utils._base import get_state
from utils._data_netnumbering import city_state_data
from utils.handle_logs import create_log_
from utils.utils_helpers import get_proxy_settings


WAVIX_APPID = settings.WAVIX_APPID


def get_city_state(area_code):
    state, city_list = city_state_data.get(area_code, ("n/a", ["n/a"]))
    random_city = random_choice(city_list)
    return str(random_city).lower(), get_state(str(state).lower()).strip()


def API_Wavix(phone_clean):
    wavix_logger.info(f'Phone: {phone_clean} Server: Wavix Proxy')

    returnDict = {
        'number': phone_clean,
        'line_type': 'invalid',
        'carrier_name': 'n/a',
        'city': 'n/a',
        'state': 'n/a',
        'country': 'us',
    }

    if phone_clean.startswith(("800", "888", "877", "866", "855", "844", "833")):
        returnDict['line_type'] = 'toll_free'
        return returnDict

    if len(phone_clean) == 10 and (phone_clean.startswith("1") or phone_clean.startswith("0")):
        returnDict['line_type_original'] = 'starts_with_1_or_0'
        returnDict['line_type'] = 'invalid'
        return returnDict

    try:
        # Get proxy settings
        proxy_domain, proxy_token, server_ip = get_proxy_settings()
        
        # Call proxy server
        url = f"{proxy_domain}/wavix-proxy/"
        headers = {
            "X-Server-IP": server_ip,
            "Authorization": f"Bearer {proxy_token}",
            "Content-Type": "application/json",
        }
        payload = {"number": phone_clean}

        for i in range(1, 3):
            wavix_logger.info(f'Wavix Proxy Request - Phone: {phone_clean}, Retry: {i}')
            try:
                response = SEND_REQUEST("POST", url, headers=headers, data=json.dumps(payload), timeout=60)
                response.raise_for_status()

                if response.headers.get('Content-Type', '').startswith('application/json'):
                    data = response.json()
                else:
                    wavix_logger.warning(f"Unexpected content type for {phone_clean}: {response.headers.get('Content-Type')}")
                    continue

                returnDict['carrier_name'] = str(data.get('carrier_name', 'unknown')).strip().lower()
                returnDict['city'], returnDict['state'] = get_city_state(phone_clean[:3])
                returnDict['line_type'] = str(data.get('number_type', 'unknown')).strip().lower()

                break 

            except requests.exceptions.ConnectionError as e:
                wavix_logger.error(f"Connection error for {phone_clean}, Retry: {i}. Error: {str(e)}")
                return returnDict

            except Exception as e:
                wavix_logger.error(f"Wavix proxy failed for {phone_clean}, Retry: {i}. Error: {str(e)}")
                create_log_(
                    log_type='Wavix API',
                    message=f"Wavix proxy wasn't able to serve request for {phone_clean}",
                    metadata={'phone_number': phone_clean},
                    exception_message=str(e)
                )
                continue

    except Exception as e:
        wavix_logger.error(f"Error getting proxy settings: {str(e)}")
        create_log_(
            log_type='Wavix API',
            message=f"Failed to get proxy settings for {phone_clean}",
            metadata={'phone_number': phone_clean},
            exception_message=str(e)
        )

    return returnDict


def ServiceTest_Wavix_Server(clean_phone):
    wavix_logger.info(f'Phone: {clean_phone} Server: wavix')
    url = f"https://api.wavix.com/v1/validation?appid={WAVIX_APPID}&phone_number=1{clean_phone}&type=validation"
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }  
    try:
        response = SEND_REQUEST("GET", url, headers=headers, data=payload, timeout=30)
        
        response.raise_for_status()
        
        response_data = response.json()
        
        return True
    except Exception as e:
        create_log_(
            log_type='Wavix API', 
            message=f"Wavix Server wasn't able to serve request for {clean_phone}", 
            metadata={'phone_number': clean_phone}, 
            exception_message=str(e)
        )
        return False




