"""
    - no more modification needed
"""

from requests import request as SEND_REQUEST
import json
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

from utils._base import get_state

def API_TELNYX(phone_clean):
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

    url = f"https://api.telnyx.com/v2/number_lookup/+1{phone_clean}?type=carrier" 

    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {settings.TELYNX_AUTH_TOKEN}'
    }
    
    for i in range(3):
        try:
            response = SEND_REQUEST("GET", url, headers=headers, data=payload, timeout=30)
            data = json.loads(response.text)
            data = data.get('data', {})
            carrier_dict = data.get('carrier', {})
            portability_dict = data.get('portability', {})

            returnDict['line_type_original'] = str(portability_dict.get('line_type', 'none')).lower()
            if returnDict['line_type_original'] == '':
                returnDict['line_type'] = 'invalid'
            elif returnDict['line_type_original'] == 'none':
                returnDict['line_type'] = 'invalid'
            elif returnDict['line_type_original'] == 'fixed line':
                returnDict['line_type'] = 'landline'
            else:
                returnDict['line_type'] = returnDict['line_type_original']


            carrier_name = carrier_dict.get('name', '')
            if carrier_name is None or carrier_name == '':
                carrier_name = 'n/a'
            else:
                carrier_name = carrier_name.lower()

            city = portability_dict.get('city', '')
            if city is None or city == '':
                city = 'n/a'
            else:
                city = city.lower().replace('city','').strip()

            state = portability_dict.get('state', '')
            if state is None or state == '':
                state = 'n/a'
            else:
                state = get_state(state.lower()).strip()

            country = data.get('country_code', '')
            if country is None or country == '':
                country = 'us'
            else:
                country = country.lower().strip()

            carrier_name = carrier_name.strip()
            if carrier_name.endswith(state):
                carrier_name = carrier_name.replace(f"- {state}", '')
            if carrier_name.endswith('-'):
                carrier_name = carrier_name[:-1]

            returnDict['carrier_name'] = carrier_name.strip()
            if returnDict['carrier_name'] == 't':
                returnDict['carrier_name'] = 't-mobile usa'
                
            returnDict['city'] = city.strip()
            returnDict['state'] = state
            returnDict['country'] = country.strip()

            break
        except:
            logger.warning(f"Telynx API wasn't able to serve request on {phone_clean}")
            continue

    return returnDict

