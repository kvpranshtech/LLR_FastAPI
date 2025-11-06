"""
    - modfied the code in feb 24
    - no more modification needed now
"""

from requests import request as SEND_REQUEST
import json
from django.conf import settings

from utils.handle_logs import create_log_

def MailCheckApi(email):
    is_valid_email = False
    try:
        url = "https://api.mailcheck.co/v1/singleEmail:check"
        payload = json.dumps({"email": email})
        headers = {
            'authorization': f'Bearer {settings.MAILCHECK_AUTH_TOKEN}',
            'content-type': 'application/json'
        }
        response = SEND_REQUEST("POST", url, headers=headers, data=payload, timeout=60)
        #print(response.text)
        data = json.loads(response.text)
        trust_rate = data['trustRate']
        if trust_rate >= 10:
            is_valid_email = True
            
    except Exception as e:
        create_log_(log_type='mailcheck', 
                message=f"MailCheck API wasn't able to serve request on", 
                metadata={'email': email}, 
                exception_message=str(e)
            )
         
    return is_valid_email

