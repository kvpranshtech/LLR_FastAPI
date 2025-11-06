import logging
import os
import requests
from django.conf import settings
from core.models import EndatoApiResponse,CsvFileData,EndatoCsvFileData
import json

# Set up logging
os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
logger = logging.getLogger('wavix_logger')
handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'endato.log'))
formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def API_Endato(id, first_name, last_name, phone):
    returnDict = {
        'number': phone,
        'first_name': 'invalid',
        'last_name':  'n/a',
        'age':  'n/a',
        'addresses':  'n/a',
        'phones':  'us',
        'emails':'n/a',
        'identityScore':'n/a'
    }

    try:
        url = 'https://devapi.endato.com/Contact/Enrich'
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'galaxy-ap-name': settings.GALAXY_AP_NAME,
            'galaxy-ap-password': settings.GALAXY_AP_PASSWORD,
            'galaxy-search-type': 'DevAPIContactEnrich',
        }
        data = {
            "FirstName": first_name,
            "LastName": last_name,
            "Phone": phone,
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_dict = response.json()

            try:
                current_request = EndatoApiResponse.objects.get(id=id)
                current_request.response_dict = response_dict
                current_request.save()
                
                try:
                        person_data = response_dict.get('person', {})
                        
                        returnDict['first_name'] = person_data.get('name', {}).get('firstName', 'n/a')
                        
                        returnDict['last_name'] = person_data.get('name', {}).get('lastName', 'n/a')
                        
                        returnDict['age'] = person_data.get('age', 'n/a')

                        addresses = person_data.get('addresses', [])
                        if addresses:
                            latest_address = addresses[0]  
                            formatted_address = (
                                f"Street: {latest_address.get('street', '')}, "
                                f"City: {latest_address.get('city', '')}, "
                                f"State: {latest_address.get('state', '')}, "
                                f"ZIP: {latest_address.get('zip', '')}, "
                                f"First Reported: {latest_address.get('firstReportedDate', '')}, "
                                f"Last Reported: {latest_address.get('lastReportedDate', '')}"
                            )
                            
                            returnDict['addresses'] = formatted_address

                        phones = person_data.get('phones', [])
                        formatted_phones = ', '.join([
                            f"{phone.get('number', '')} ({phone.get('type', '')})"
                            for phone in phones
                        ])
                        if formatted_phones:
                            
                            returnDict['phones'] = formatted_phones

                        emails = person_data.get('emails', [])
                        formatted_emails = ', '.join([
                            email.get('email', '').replace('mailto:', '') for email in emails
                        ])
                        if emails:
                            
                            returnDict['emails'] = formatted_emails

                        
                        returnDict['identityScore'] = str(response_dict.get('identityScore', 'n/a'))
                        
                        return returnDict
                    
                except Exception as e:
                    logger.error(f"Error updating Phone Number {phone}: {str(e)}")

                
            except EndatoApiResponse.DoesNotExist:
                logger.warning(f"No EndatoApiResponse found with id {id}.")
            except Exception as e:
                logger.error(f"Error updating EndatoApiResponse with id {id}: {str(e)}")
            return None
        else:
            logger.error(f"Failed to enrich contact {first_name} {last_name} with phone {phone}. Status Code: {response.status_code}")
            return None
    
    except Exception as e:
        logger.error(f"Error sending request for {first_name} {last_name} with phone {phone}: {str(e)}")
        return None












def getEnrichedData(data):
    try:
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'galaxy-ap-name': '5c1b35ac7ee245a9a3a692e0305e2677',  
            'galaxy-ap-password': '3b243440beba437aafdc4a08dce0300b',  
            'galaxy-search-type': 'DevAPIContactEnrich'
        }
    
        response = requests.post('https://devapi.endato.com/Contact/Enrich',
                                 headers=headers,
                                 data=json.dumps(data))



        response_dict = response.json()

        response_data = {'first_name':'',
                         'last_name':'',
                         'addresses':'',
                         'phones':'',
                         'emails':'',
                         'identityscore':''
                         }

        person_data = response_dict.get('person', {})

        first_name = person_data.get('name', {}).get('firstName', 'n/a')
        response_data['first_name'] = first_name

        last_name = person_data.get('name', {}).get('lastName', 'n/a')
        response_data['last_name'] = last_name

        age = person_data.get('age', 'n/a')
        response_data['age'] = age

        addresses = person_data.get('addresses', [])
        if addresses:
            latest_address = addresses[0]
            formatted_address = (
                f"Street: {latest_address.get('street', '')}, "
                f"City: {latest_address.get('city', '')}, "
                f"State: {latest_address.get('state', '')}, "
                f"ZIP: {latest_address.get('zip', '')}, "
                f"First Reported: {latest_address.get('firstReportedDate', '')}, "
                f"Last Reported: {latest_address.get('lastReportedDate', '')}"
            )
            response_data['addresses'] = formatted_address
        else:
            response_data['addresses'] = 'n/a'

        phones = person_data.get('phones', [])
        formatted_phones = ', '.join([f"{phone.get('number', '')} ({phone.get('type', '')})" for phone in phones])
        if formatted_phones:
            response_data['phones'] = formatted_phones
        else:
            response_data['phones'] = 'n/a'

        emails = person_data.get('emails', [])
        formatted_emails = ', '.join([email.get('email', '').replace('mailto:', '') for email in emails])
        if formatted_emails:
            response_data['emails'] = formatted_emails
        else:
            response_data['emails'] = 'n/a'

        identityScore = str(response_dict.get('identityScore', 'n/a'))
        response_data['identityscore'] = identityScore

        return response_data

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return {"isError": True, "errorMessage": str(e)}






logger = logging.getLogger(__name__)
def getBulkEnrichedData(data):
    logger.info(f"Data: {data}")

    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'galaxy-ap-name': '5c1b35ac7ee245a9a3a692e0305e2677',  
        'galaxy-ap-password': '3b243440beba437aafdc4a08dce0300b',  
        'galaxy-search-type': 'DevAPIContactEnrich'
    }

    enriched_data = []

    for item in data:
        logger.info(f"Sending item: {json.dumps(item)}")  

        response = requests.post('https://devapi.endato.com/Contact/Enrich',
                                 headers=headers,
                                 data=json.dumps(item))  

        logger.info(f"Response: {response.status_code} - {response.text}")

        if response.status_code != 200:
            logger.error(f"Error: {response.status_code} - {response.text}")
            enriched_data.append({"error": f"Error: {response.status_code} - {response.text}"})
            continue

        response_dict = response.json()
        logger.info(f"response_dict: {response_dict}")

        response_data = {
            'first_name': '',
            'last_name': '',
            'addresses': '',
            'phones': '',
            'emails': '',
            'identityscore': '',
            'age': 'n/a'
        }

        person_data = response_dict.get('person', {})

        first_name = person_data.get('name', {}).get('firstName', 'n/a')
        response_data['first_name'] = first_name

        last_name = person_data.get('name', {}).get('lastName', 'n/a')
        response_data['last_name'] = last_name

        age = person_data.get('age', 'n/a')
        response_data['age'] = age

        addresses = person_data.get('addresses', [])
        if addresses:
            latest_address = addresses[0]
            formatted_address = (
                f"Street: {latest_address.get('street', '')}, "
                f"City: {latest_address.get('city', '')}, "
                f"State: {latest_address.get('state', '')}, "
                f"ZIP: {latest_address.get('zip', '')}, "
                f"First Reported: {latest_address.get('firstReportedDate', '')}, "
                f"Last Reported: {latest_address.get('lastReportedDate', '')}"
            )
            response_data['addresses'] = formatted_address
        else:
            response_data['addresses'] = 'n/a'

        phones = person_data.get('phones', [])
        formatted_phones = ', '.join([f"{phone.get('number', '')} ({phone.get('type', '')})" for phone in phones])
        response_data['phones'] = formatted_phones if formatted_phones else 'n/a'

        emails = person_data.get('emails', [])
        formatted_emails = ', '.join([email.get('email', '').replace('mailto:', '') for email in emails])
        response_data['emails'] = formatted_emails if formatted_emails else 'n/a'

        identityScore = str(response_dict.get('identityScore', 'n/a'))
        response_data['identityscore'] = identityScore

        enriched_data.append(response_data)

        logger.info(f"Enriched Data: {response_data}")

    return enriched_data