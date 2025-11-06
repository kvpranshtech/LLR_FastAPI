import logging
import os
from django.conf import settings

from utils.utils_helpers import get_proxy_settings

os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
# Configure method1 logger
dnctcpa_logger = logging.getLogger('dnctcpa_logger')
dnctcpa_handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'dnctcpa.log'))
dnctcpa_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
dnctcpa_handler.setFormatter(dnctcpa_formatter)
dnctcpa_logger.addHandler(dnctcpa_handler)
dnctcpa_logger.setLevel(logging.INFO)


"""
    - modified in march 24
    - no more modification need for now
"""


import json
from requests import request as SEND_REQUEST
from django.conf import settings

from utils.handle_logs import create_log_

import logging
logger = logging.getLogger(__name__)


def returnType(phone_clean, data):
    if 'match' in data.keys():
        dnc_type_ = str(data['match'][phone_clean]['type']).strip()
    else:
        dnc_type_ = 'clean'
    if not dnc_type_:
        dnc_type_ = 'Federal DNC'
    elif dnc_type_.startswith(','):
        dnc_type_ = dnc_type_.replace(',', '').strip()
    return dnc_type_



# def API_TcpaLitigatorlist(phone_clean):
#     headers = {'Authorization': f'Basic {settings.TCPADNC_AUTH_TOKEN}'}
#     phone_clean = str(phone_clean).strip()
#     returnDict = {
#         'phonenumber': phone_clean,
#         'dnc_type': 'unknown',
#         'api_data':  '',
#     }
#
#     for i in range(1, 3):
#         dnctcpa_logger.info(f'Phone: {phone_clean} Retry: {i} | Request make for API_TcpaLitigatorlist ')
#
#         try:
#             url = f'https://api.tcpalitigatorlist.com/scrub/phone/all/{phone_clean}'
#             response = SEND_REQUEST("GET", url, headers=headers, timeout=60)
#             data = json.loads(response.text)
#             returnDict['dnc_type'] = returnType(phone_clean, data)
#             break
#         except Exception as e:
#             create_log_(log_type='dnctcpa_single',
#                 message=f"DNCTCPA API wasn't able to serve request on",
#                 metadata={'phone_number': phone_clean},
#                 exception_message=str(e)
#             )
#             continue
#     return returnDict


# New method using Proxy srver.
def API_TcpaLitigatorlist(phone_clean):

    phone_clean = str(phone_clean).strip()
    returnDict = {
        'phonenumber': phone_clean,
        'dnc_type': 'unknown',
        'api_data':  '',
    }

    for i in range(1, 3):
        dnctcpa_logger.info(f'Phone: {phone_clean} Retry: {i} | Request make for API_TcpaLitigatorlist ')

        try:
            proxy_domain, proxy_token, server_ip = get_proxy_settings()
            print("---------- DNC single check proxy --------- ")
            url = f"{proxy_domain}/dnctcpa-single-proxy/"
            payload = {"number": phone_clean}
            headers = {
                "X-Server-IP": server_ip,
                "Authorization": f"Bearer {proxy_token}",
                "Content-Type": "application/json",
            }

            response = SEND_REQUEST("POST", url, headers=headers, data=json.dumps(payload), timeout=15)
            response.raise_for_status()
            data = response.json()
            print("--------- DNC single check proxy response --------- ", data)
            print(f"---- DNC ::::: {returnType(phone_clean, data)} ------")
            returnDict['dnc_type'] = returnType(phone_clean, data)
            break

        except Exception as e:
            create_log_(log_type='dnctcpa_single',
                    message=f"DNCTCPA API wasn't able to serve request on",
                    metadata={'phone_number': phone_clean},
                    exception_message=str(e)
                )
            continue
    return returnDict



#new method mar 24 - build only for service test purpose
def ServiceTest_DNC_SingleAPI(clean_phone):
    dnctcpa_logger.info(f'Phone: {clean_phone} | Request make for ServiceTest_DNC_SingleAPI ')

    headers = {'Authorization': f'Basic {settings.TCPADNC_AUTH_TOKEN}'}
    url = f'https://api.tcpalitigatorlist.com/scrub/phone/all/{clean_phone}'
    response = SEND_REQUEST("GET", url, headers=headers, timeout=30)
    #print(response.text)
    try:
        response = SEND_REQUEST("GET", url, headers=headers, timeout=30)
        response.raise_for_status()
        #data = json.loads(response.text)
        return True
    except Exception as e:
        create_log_(log_type='dnctcpa_single', 
                message=f"DNCTCPA Single API wasn't able to serve request for {clean_phone}", 
                metadata={'phone_number': clean_phone}, exception_message=str(e)
            )
    return False 


