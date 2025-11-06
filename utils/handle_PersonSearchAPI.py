import logging
import os
import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from core.models import EndatoApiResponse
from utils.handle_emailing import email_BaseMethod
from utils.handle_logs import create_log_
from utils.utils_helpers import get_proxy_settings


os.makedirs(os.path.join(settings.BASE_DIR, '_custom_logs'), exist_ok=True)
logger = logging.getLogger('personSearch_logger')
handler = logging.FileHandler(os.path.join(settings.BASE_DIR, '_custom_logs', 'endato.log'))
formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

import requests
from django.conf import settings
import json



def API_PersonSearch(phone):
    logger.info(f'Phone: {phone} Server: PersonSearch Proxy')
    
    returnDict = {
        'number': phone,
        'first_name': 'n/a',
        'last_name': 'n/a',
        'age': 'n/a',
        'addresses': 'n/a',
        'phones': 'n/a',
        'emails': 'n/a',
    }
    
    try:
        # Get proxy settings
        proxy_domain, proxy_token, server_ip = get_proxy_settings()
        
        # Call proxy server
        url = f"{proxy_domain}/person-search-proxy/"
        headers = {
            "X-Server-IP": server_ip,
            "Authorization": f"Bearer {proxy_token}",
            "Content-Type": "application/json",
        }
        payload = {"phone": phone}
        
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        
        if response.status_code == 400:
            return returnDict

        response.raise_for_status()  
        data = response.json()
        


        for person in data.get("persons", []):
            returnDict['first_name'] = person.get("name", {}).get("firstName", "")
            returnDict['last_name'] = person.get("name", {}).get("lastName", "")
            returnDict['age'] = person.get("age", "")
            returnDict['emails'] = [email.get("emailAddress") for email in person.get("emailAddresses", [])]
            returnDict['phones'] = [phone.get("phoneNumber") for phone in person.get("phoneNumbers", [])]
            returnDict['addresses'] = [address.get("fullAddress") for address in person.get("addresses", [])]
        
        return returnDict
    except requests.RequestException as e:
        logger.error(f"PersonSearch proxy request failed: {e}")
        create_log_(
            log_type='person_search',
            message=f"PersonSearch proxy failed for {phone}",
            metadata={'phone_number': phone},
            exception_message=str(e)
        )
        return {"error": "Failed to fetch data from the API"}
    except Exception as e:
        logger.error(f"PersonSearch error: {e}")
        create_log_(
            log_type='person_search',
            message=f"PersonSearch error for {phone}",
            metadata={'phone_number': phone},
            exception_message=str(e)
        )
        return returnDict


def ServiceTest_PersonSearch(clean_phone):
    logger.info(f'Phone: {clean_phone} Server: Person Search API')

    try:
        response = API_PersonSearch(clean_phone)

        if "error" in response:
            create_log_(
                log_type='person_search',
                message=f"Person Search API failed for {clean_phone}",
                metadata={'phone_number': clean_phone},
                exception_message=response["error"]
            )
            return False


        # Log successful response
        logger.info(f"Person Search API Response for {clean_phone}: {response}")
        return True
    except Exception as e:
        create_log_(
            log_type='person_search',
            message=f"Person Search API wasn't able to serve request for {clean_phone}",
            metadata={'phone_number': clean_phone},
            exception_message=str(e)
        )
        return False


import time

def ServiceTest_EmailService():
    test_email = "kirtan.pranshtech@gmail.com"
    subject = "LLR Email Service Test"
    html_message = "<p>This is a test email to verify Email Service status in LLR.</p>"

    try:
        # email_BaseMethod(subject=subject, email_send_to=test_email, html_message=html_message)

        message = EmailMultiAlternatives(
           subject=subject,
           from_email='no-reply@landlineremover.com',
           to=[test_email],)
        message.attach_alternative(html_message, "text/html")
        message.send()

        logger.info(f"Email service test email sent successfully to {test_email}")
        return True

    except Exception as e:
        logger.error(f"Email service test failed: {str(e)}")
        create_log_(
            log_type='email service',
            message=f"Email Service test failed for {test_email}",
            metadata={'email': test_email},
            exception_message=str(e)
        )
        return False
