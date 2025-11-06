import logging
import os
import requests
from django.conf import settings

os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
logger = logging.getLogger('melissa_logger')
handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'melissa.log'))
formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def API_Melissa(phone):
    returnDict = {
        'number': phone,
        'name_full': 'n/a',
        'email': 'n/a',
        'address': 'n/a',
        'city': 'n/a',
        'state': 'n/a',
        'zip': 'n/a',
    }

    url = 'https://personator.melissadata.net/v3/WEB/ContactVerify/doContactVerify'
    params = {
        'id': settings.MELISSA_API_KEY,
        'format': 'json',
        'act': 'Append',
        'cols': 'Salutation',
        'opt': 'SSNCascade:off;UsePreferredCity:off;Diacritics:auto;AdvancedAddressCorrection:on;'
               'LongAddressFormat:auto;CorrectSyntax:on;UpdateDomain:on;DatabaseLookup:on;'
               'StandardizeCasing:on;CorrectFirstName:on;StandardizeCompany:on;NameHint:Varying;'
               'GenderPopulation:Mixed;MiddleNameLogic:MiddleName;SalutationFormat:FirstLast;'
               'CentricHint:Auto;Append:Always;Demographics:Yes',
        'phone': phone,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    

        record = data['Records'][0]

        returnDict['name_full'] = record.get('NameFull', 'n/a')
        returnDict['email'] = record.get('EmailAddress', 'n/a')
        returnDict['address'] = record.get('AddressLine1', 'n/a')
        returnDict['city'] = record.get('City', 'n/a')
        returnDict['state'] = record.get('State', 'n/a')
        returnDict['zip'] = record.get('PostalCode', 'n/a')

        logger.info(f"MelissaAPI: Phone={phone}, Name={returnDict['name_full']}, City={returnDict['city']}")
        return returnDict

    except requests.RequestException as e:
        print(e)
        logger.error(f"Melissa API request failed for phone {phone}: {e}")
        return {"error": "Failed to fetch data from Melissa API"}


