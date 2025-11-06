"""
    - modfied the code in july 2023
    - no more modification needed
"""
from requests import get as GetRequest
from dashboard.models import SignUpDomains

def validate_domain_existence(domain):
    #checking in database 
    domain_status = False

    try:
        domain_obj = SignUpDomains.objects.values('status').get(domain=domain)
        return domain_obj['status']
    except: 
        pass

    #getting domain status using requests
    try:
        response = GetRequest(f'http://{domain}', timeout=30)
        if str(response.status_code).startswith('2'):
            domain_status =  True
    except:
        pass

    # storing into database for next use 
    SignUpDomains.objects.get_or_create(domain=domain, defaults={"status":domain_status})
    return domain_status