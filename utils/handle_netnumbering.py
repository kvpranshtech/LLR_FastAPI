import logging
import os
from django.conf import settings
os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
# Configure method1 logger
nn_logger = logging.getLogger('nn_logger')
nn_handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'nn.log'))
nn_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
nn_handler.setFormatter(nn_formatter)
nn_logger.addHandler(nn_handler)
nn_logger.setLevel(logging.INFO)
from utils.utils_helpers import get_proxy_settings

"""
    - new script in oct 23
"""

from requests import request as SEND_REQUEST
import json
from django.conf import settings
from random import choice as random_choice 

from utils._base import get_state
from utils._data_netnumbering import city_state_data, netnumbering_cic_data
from utils.handle_logs import create_log_


VPN_SERVER_NET_NUMBERING_TOKEN = settings.VPN_SERVER_NET_NUMBERING_TOKEN



def get_city_state(area_code):
    state, city_list = city_state_data.get(area_code, ("n/a", ["n/a"]))
    random_city = random_choice(city_list)
    return str(random_city).lower(), get_state(str(state).lower()).strip()

def get_linetype_carrier_name(cic):
    linetype, carrier_name = netnumbering_cic_data.get(cic, ("invalid", "n/a"))
    return str(linetype).lower(), str(carrier_name).lower()


# def API_NetNumbering(phone_clean):
#     nn_logger.info(f'Phone: {phone_clean} Server: Random')


#     returnDict = {
#         'number': phone_clean,
#         'line_type': 'invalid',
#         'carrier_name':  'n/a',
#         'city':  'n/a',
#         'state':  'n/a',
#         'country':  'us',
#     }

#     if phone_clean.startswith(("800", "888", "877", "866", "855", "844", "833")): 
#         returnDict['line_type'] = 'toll_free'
#         return returnDict

#     if len(phone_clean) == 10 and (phone_clean.startswith("1") or phone_clean.startswith("0")):
#         returnDict['line_type_original'] = 'starts_with_1_or_0'
#         returnDict['line_type'] = 'invalid'
#         return returnDict

#     try:
#         url = f"http://104.236.65.148:8000/virginia-ohio/?api_key={VPN_SERVER_NET_NUMBERING_TOKEN}&number={phone_clean}" 

#         payload = {}
#         headers = {
#             'Content-Type': 'application/json',
#             'Accept': 'application/json',
#         }
#         response = SEND_REQUEST("GET", url, headers=headers, data=payload, timeout=10).json()
#         returnDict['carrier_name'] = str(response.get('name', 'n/a')).strip().lower()
#         returnDict['city'], returnDict['state'] = get_city_state(phone_clean[:3])

#         cic = response.get('cic', None)
#         if cic:
#             cic = str(cic)[1:]
#             linetype, carrier_name = get_linetype_carrier_name(cic)
#             returnDict['line_type'] = linetype
#     except:
#         create_log_(log_type='Netnumbering API', 
#             message=f"Netnumbering API wasn't able to serve request on", 
#             metadata={'phone_number': phone_clean}, 
#         )

#     return returnDict 



def  ServiceTest_NN_BostonServer(clean_phone):
    nn_logger.info(f'Phone: {clean_phone} Server: Boston')

    url = f"http://104.236.65.148:8000/boston/?api_key={VPN_SERVER_NET_NUMBERING_TOKEN}&number={clean_phone}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    try:
        response = SEND_REQUEST("GET", url, headers=headers, data={}, timeout=30)
        response.raise_for_status()
        # data = response.json()
        return True
    except Exception as e:
        create_log_(log_type='nn_boston', 
                message=f"Netnumbering Boston Server wasn't able to serve request for {clean_phone}", 
                metadata={'phone_number': clean_phone}, exception_message=str(e)
            )
    return False 


def  ServiceTest_NN_ChicagoServer(clean_phone):
    nn_logger.info(f'Phone: {clean_phone} Server: Chicago')

    url = f"http://104.236.65.148:8000/chicago/?api_key={VPN_SERVER_NET_NUMBERING_TOKEN}&number={clean_phone}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    try:
        response = SEND_REQUEST("GET", url, headers=headers, data={}, timeout=30)
        response.raise_for_status()
        # data = response.json()
        return True
    except Exception as e:
        create_log_(log_type='nn_chicago', 
                message=f"Netnumbering Chicago Server wasn't able to serve request for {clean_phone}", 
                metadata={'phone_number': clean_phone}, exception_message=str(e)
            )
    return False 



def ServiceTest_NN_OhioServer(clean_phone):
    nn_logger.info(f'Phone: {clean_phone} Server: Ohio')

    url = f"http://104.236.65.148:8000/ohio/?api_key={VPN_SERVER_NET_NUMBERING_TOKEN}&number={clean_phone}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    try:
        response = SEND_REQUEST("GET", url, headers=headers, data={}, timeout=30)
        response.raise_for_status()
        # data = response.json()
        return True
    except Exception as e:
        create_log_(log_type='nn_ohio', 
                message=f"Netnumbering Ohio Server wasn't able to serve request for {clean_phone}", 
                metadata={'phone_number': clean_phone}, exception_message=str(e)
            )
    return False 


def ServiceTest_NN_VirginiaServer(clean_phone):
    nn_logger.info(f'Phone: {clean_phone} Server: Virginia')

    url = f"http://104.236.65.148:8000/virginia/?api_key={VPN_SERVER_NET_NUMBERING_TOKEN}&number={clean_phone}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    try:
        response = SEND_REQUEST("GET", url, headers=headers, data={}, timeout=30)
        response.raise_for_status()
        # data = response.json()
        return True
    except Exception as e:
        create_log_(
            log_type='nn_virginia',
                message=f"Netnumbering Virginia Server wasn't able to serve request for {clean_phone}", 
                metadata={'phone_number': clean_phone}, exception_message=str(e)
            )
    return False 








# NEW METHOD FOR CALL PROXY SERVER 


def API_NetNumbering(phone_clean):
    nn_logger.info(f'Phone: {phone_clean} Server: Proxy')

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
    
    print("Calling Netnumber Proxy Server...")
    try:
        proxy_domain, proxy_token, server_ip = get_proxy_settings()
        
        url = f"{proxy_domain}/netnumber-proxy/"  
        payload = {"number": phone_clean}
        headers = {
            "X-Server-IP": server_ip,
            "Authorization": f"Bearer {proxy_token}",
            "Content-Type": "application/json",
        }

        response = SEND_REQUEST("POST", url, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status()
        data = response.json() 
        

        returnDict['carrier_name'] = str(data.get('name', 'n/a')).strip().lower()
        returnDict['city'], returnDict['state'] = get_city_state(phone_clean[:3])

        cic = data.get('cic', None)
        if cic:
            cic = str(cic)[1:]
            linetype, carrier_name = get_linetype_carrier_name(cic)
            returnDict['line_type'] = linetype

    except Exception as e:
        create_log_(log_type='Netnumbering API', 
                    message=f"NetNumber proxy failed for {phone_clean}", 
                    metadata={'phone_number': phone_clean}, 
                    exception_message=str(e))

    return returnDict
