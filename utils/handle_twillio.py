import logging
import os
from django.conf import settings
import requests

os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
# Configure method1 logger
twillio_logger = logging.getLogger('twillio_logger')
twillio_handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'twillio.log'))
twillio_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
twillio_handler.setFormatter(twillio_formatter)
twillio_logger.addHandler(twillio_handler)
twillio_logger.setLevel(logging.INFO)



"""
    - new script in oct 23
"""

from requests import request as SEND_REQUEST

from django.conf import settings
from utils._data_netnumbering import city_state_data
from utils._base import get_state
from random import choice as random_choice 
from utils.handle_logs import create_log_


WAVIX_APPID = settings.WAVIX_APPID

def get_city_state(area_code):
    state, city_list = city_state_data.get(area_code, ("n/a", ["n/a"]))
    random_city = random_choice(city_list)
    return str(random_city).lower(), get_state(str(state).lower()).strip()


def API_Twillio(phone_clean):
    twillio_logger.info(f'Phone: {phone_clean} Server')

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

    url = f"https://lookups.twilio.com/v2/PhoneNumbers/{phone_clean}?Fields=line_type_intelligence"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Basic QUMzNjllNzg4ZmJkMzRmOTJjZjZlZWNhYzhkODJkNzk3YzplYzI5NDE2ZmU0MGY4NGNiYTgxNTQ2NmNlNDFjZDY5MA=='
    }

    for i in range(1, 3):
        twillio_logger.info(f'twilio API Request - Phone: {phone_clean}, Retry: {i}')
        try:
            response = SEND_REQUEST("GET", url, headers=headers, timeout=60)

            if response.headers.get('Content-Type', '').startswith('application/json'):
                data = response.json()
            else:
                twillio_logger.warning(f"Unexpected content type for {phone_clean}: {response.headers.get('Content-Type')}")
                continue

            line_info = data.get('line_type_intelligence', {})
            returnDict['carrier_name'] = str(line_info.get('carrier_name', 'unknown')).strip().lower()
            returnDict['city'], returnDict['state'] = get_city_state(phone_clean[:3])
            returnDict['line_type'] = str(line_info.get('type', 'unknown')).strip().lower()

            break

        except requests.exceptions.ConnectionError as e:
            twillio_logger.error(f"Connection error for {phone_clean}, Retry: {i}. Error: {str(e)}")
            return returnDict

        except Exception as e:
            twillio_logger.error(f"twilio API failed for {phone_clean}, Retry: {i}. Error: {str(e)}")
            create_log_(
                log_type='twilio API',
                message=f"twilio API wasn't able to serve request for {phone_clean}",
                metadata={'phone_number': phone_clean},
                exception_message=str(e)
            )
            continue

    return returnDict

