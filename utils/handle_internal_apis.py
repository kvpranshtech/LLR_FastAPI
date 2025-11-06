from requests import request as SEND_REQUEST
import json

from utils.handle_logs import create_log_


def ServiceTest_LLRCheckSingleNumber_API(apikey, clean_phone):
    try:
        url = f"https://landlineremover.com/api/check-number?apikey={apikey}&number={clean_phone}"
        response = SEND_REQUEST("GET", url, timeout=60)
        #data = json.loads(response.text)
        response.raise_for_status()
        return True 
    except Exception as e:
        create_log_(log_type='llr_check_number', 
                message=f"LLR Internal Single Check Number API wasn't able to serve request", 
                metadata={'phone_number': clean_phone}, exception_message=str(e)
            )
    return False




def ServiceTest_LLRCheckRemainingCredits_API(apikey):
    try:
        url = f"https://landlineremover.com/api/check-credits?apikey={apikey}"
        response = SEND_REQUEST("GET", url, timeout=60)
        # data = json.loads(response.text)
        # print(data)
        response.raise_for_status()
        return True 
    except Exception as e:
        create_log_(log_type='llr_check_credits', 
                message=f"LLR Internal Check Credits API wasn't able to serve request", 
                exception_message=str(e)
            )
    return False
