"""
    - added custom logs in sep 23
    - no more modification needed
"""
import logging
import os
from django.conf import settings
os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
# Configure method1 logger
signalwire_logger = logging.getLogger('signalwire_logger')
signalwire_handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'signalwire.log'))
signalwire_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
signalwire_handler.setFormatter(signalwire_formatter)
signalwire_logger.addHandler(signalwire_handler)
signalwire_logger.setLevel(logging.INFO)
from utils.utils_helpers import get_proxy_settings


import json
from requests import request as SEND_REQUEST
from django.conf import settings

from utils.handle_logs import create_log_


# def API_Singalwire(phone_clean):
#     data = None
#     returnDict = {
#         'number': phone_clean,
#         'line_type': 'invalid',
#         'line_type_original':  '',
#         'carrier_name':  'n/a',
#         'city':  'n/a',
#         'state':  'n/a',
#         'country':  'n/a',
#         'data':  ''
#     }

#     if phone_clean.startswith(("800", "888", "877", "866", "855", "844", "833")):
#         returnDict['line_type_original'] = 'toll_free'
#         returnDict['line_type'] = 'toll_free'
#         return returnDict

#     if len(phone_clean) == 10 and (phone_clean.startswith("1") or phone_clean.startswith("0")):
#         returnDict['line_type_original'] = 'starts_with_1_or_0'
#         returnDict['line_type'] = 'invalid'
#         return returnDict

#     url = f"https://digual.signalwire.com/api/relay/rest/lookup/phone_number/+1{phone_clean}?include=carrier"

#     payload = {}
#     headers = {'Authorization': f'Basic {settings.SIGNALWIRE_AUTH_TOKEN}'}

#     for i in range(1, 2):
#         signalwire_logger.info(f'Phone: {phone_clean} Retry: {i}')

#         try:
#             response = SEND_REQUEST("GET", url, headers=headers, data=payload, timeout=30)
#             data = json.loads(response.text)
            
#             carrier_dict = data.get('carrier', {})
#             returnDict['line_type_original'] = str(carrier_dict.get('linetype', 'none')).lower()
#             if returnDict['line_type_original'] == '':
#                 returnDict['line_type'] = 'unknown'
#             elif returnDict['line_type_original'] == 'none':
#                 returnDict['line_type'] = 'invalid'
#             elif returnDict['line_type_original'] == 'wireless':
#                 returnDict['line_type'] = 'mobile'
#             else:
#                 returnDict['line_type'] = returnDict['line_type_original']

#             carrier_name = carrier_dict.get('lec', '')
#             if carrier_name is None or carrier_name == '':
#                 carrier_name = 'n/a'
#             else:
#                 carrier_name = carrier_name.lower()
                    
#             city = carrier_dict.get('city', '')
#             if city is None or city == '':
#                 city = 'n/a'
#             else:
#                 city = city.lower()
                    
#             state = carrier_dict.get('state', '')
#             if state is None or state == '':
#                 state = 'n/a'
#             else:
#                 state = state.lower()
            
#             country = data.get('country_code', '')
#             if country is None or country == '':
#                 country = 'us'
#             else:
#                 country = country.lower()
            
#             if carrier_name.endswith(state):
#                 carrier_name = carrier_name[:-2]
                    
#             returnDict['carrier_name'] = carrier_name.strip()
#             returnDict['city'] = city.strip()
#             returnDict['state'] = state
#             returnDict['country'] = country.strip()
#             break
#         except:
#             create_log_(log_type='signalwire', 
#                 message=f"Signalwire API wasn't able to serve request for {phone_clean}", 
#                 metadata={'phone_number': phone_clean}, 
#             )
#             continue

#     return returnDict



#new method mar 24 - build only for service test purpose
# def ServiceTest_SignalwireAPI(clean_phone):
#     signalwire_logger.info(f'Phone: {clean_phone} Retry: 0')

#     headers = {'Authorization': f'Basic {settings.SIGNALWIRE_AUTH_TOKEN}'}

#     url = f"https://digual.signalwire.com/api/relay/rest/lookup/phone_number/+1{clean_phone}?include=carrier"
#     try:
#         response = SEND_REQUEST("GET", url, headers=headers, data={}, timeout=30)
#         response.raise_for_status()
#         data = json.loads(response.text)
#         if data['national_number'] == clean_phone:
#             return True
#         raise Exception("Triggered Custom Exception Due to Set Condition")
#     except Exception as e:
#         create_log_(log_type='signalwire', 
#                 message=f"Signalwire API wasn't able to serve request for {clean_phone}", 
#                 metadata={'phone_number': clean_phone}, exception_message=str(e)
#             )
#     return False 













def API_Singalwire(phone_clean):
    data = None
    returnDict = {
        'number': phone_clean,
        'line_type': 'invalid',
        'line_type_original':  '',
        'carrier_name':  'n/a',
        'city':  'n/a',
        'state':  'n/a',
        'country':  'n/a',
        'data':  ''
    }

    if phone_clean.startswith(("800", "888", "877", "866", "855", "844", "833")):
        returnDict['line_type_original'] = 'toll_free'
        returnDict['line_type'] = 'toll_free'
        return returnDict

    if len(phone_clean) == 10 and (phone_clean.startswith("1") or phone_clean.startswith("0")):
        returnDict['line_type_original'] = 'starts_with_1_or_0'
        returnDict['line_type'] = 'invalid'
        return returnDict

    proxy_domain, proxy_token, server_ip = get_proxy_settings()
    url = f"{proxy_domain}/signalwire-proxy/"
    headers = {
        "X-Server-IP": server_ip,
        "Authorization": f"Bearer {proxy_token}",
        "Content-Type": "application/json",
    }
    payload = {"number": phone_clean}

    for i in range(1, 2):
        signalwire_logger.info(f'Phone: {phone_clean} Retry: {i}')

        try:
            response = SEND_REQUEST("POST", url, headers=headers, data=json.dumps(payload), timeout=30)
            data = json.loads(response.text)
 
            carrier_dict = data.get('carrier', {})
            returnDict['line_type_original'] = str(carrier_dict.get('linetype', 'none')).lower()
            if returnDict['line_type_original'] == '':
                returnDict['line_type'] = 'unknown'
            elif returnDict['line_type_original'] == 'none':
                returnDict['line_type'] = 'invalid'
            elif returnDict['line_type_original'] == 'wireless':
                returnDict['line_type'] = 'mobile'
            else:
                returnDict['line_type'] = returnDict['line_type_original']

            carrier_name = carrier_dict.get('lec', '')
            if carrier_name is None or carrier_name == '':
                carrier_name = 'n/a'
            else:
                carrier_name = carrier_name.lower()
                        
            city = carrier_dict.get('city', '')
            if city is None or city == '':
                city = 'n/a'
            else:
                city = city.lower()
                    
            state = carrier_dict.get('state', '')
            if state is None or state == '':
                state = 'n/a'
            else:
                state = state.lower()
            
            country = data.get('country_code', '')
            if country is None or country == '':
                country = 'us'
            else:
                country = country.lower()
            
            if carrier_name.endswith(state):
                carrier_name = carrier_name[:-2]
                    
            returnDict['carrier_name'] = carrier_name.strip()
            returnDict['city'] = city.strip()
            returnDict['state'] = state
            returnDict['country'] = country.strip()
            break
        except:
            create_log_(log_type='signalwire', 
                message=f"Signalwire API wasn't able to serve request for {phone_clean}", 
                metadata={'phone_number': phone_clean}, 
            )
            continue

    return returnDict




def ServiceTest_SignalwireAPI(clean_phone):
    signalwire_logger.info(f'Phone: {clean_phone} Retry: 0')
    
    proxy_domain, proxy_token, server_ip = get_proxy_settings()
    url = f"{proxy_domain}/signalwire-proxy/"
    headers = {
        "X-Server-IP": server_ip,
        "Authorization": f"Bearer {proxy_token}",
        "Content-Type": "application/json",
    }
    payload = {"number": clean_phone}

    try:
        response = SEND_REQUEST("POST", url, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        data = json.loads(response.text)


        if data.get("national_number") == clean_phone:
            return True

        raise Exception("Triggered Custom Exception Due to Set Condition")

    except Exception as e:
        create_log_(
            log_type='signalwire',
            message=f"Signalwire API wasn't able to serve request for {clean_phone}",
            metadata={'phone_number': clean_phone},
            exception_message=str(e),
        )
    return False
