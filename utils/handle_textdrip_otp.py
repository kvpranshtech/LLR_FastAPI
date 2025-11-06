# import requests

# def send_phone_otp(input_value, token):
#     """
#     Sends an email OTP using the TextDrip API.

#     Args:
#         input_value (str): The input value (e.g., phone number).
#         input_type (str): The type of input (e.g., "mobile").
#         token (str): The authorization token.

#     Returns:
#         dict: The API response as a dictionary.
#     """
#     url = 'https://api.textdrip.com/api/v1/email-otp'
#     headers = {
#         'Authorization': f'Bearer {token}',
#         'Accept': 'application/json',
#         'Content-Type': 'application/json'
#     }
#     payload = {
#         "input": input_value,
#         "input_type": 'mobile',
#         "platform": "LLR"
#     }

#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         print(input_value, type(input_value), payload)
#         print(response.json())
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         # Log the error or handle it as needed
#         return {"error": str(e)}


# def verify_mobile_otp(api_url, token, mobile_number, otp):
#     """
#     Verifies an OTP using the TextDrip API.

#     Args:
#         api_url (str): The API endpoint.
#         token (str): The authorization token.
#         mobile_number (str): The mobile number associated with the OTP.
#         otp (str): The OTP to verify.

#     Returns:
#         dict: The API response as a dictionary or an error message.
#     """
#     headers = {
#         'Authorization': f'Bearer {token}',
#         'Accept': 'application/json',
#         'Content-Type': 'application/json',
#     }
#     payload = {
#         'input': mobile_number,
#         'input_type': 'mobile',
#         'otp': otp,
#     }
#     try:
#         response = requests.post(api_url, headers=headers, json=payload)
#         print(payload)
#         response.raise_for_status()  # Raise an exception for HTTP errors
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         return {"error": str(e)}



import requests
from django.conf import settings
from utils.utils_helpers import get_proxy_settings


def send_phone_otp(input_value):
    proxy_domain, proxy_token, server_ip = get_proxy_settings()
    url = f"{proxy_domain}/textdrip/otp/send/"   
    headers = {
        "X-Server-IP": server_ip,
        'Authorization': f'Bearer {proxy_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        "input": input_value,
        "input_type": "mobile",
        "platform": "LLR"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json() 
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def verify_mobile_otp(mobile_number, otp):
    """
    Verifies OTP through Proxy server (instead of Textdrip directly).
    NOTE: `api_url` param is still kept for backward compatibility.
    """
    proxy_domain, proxy_token, server_ip = get_proxy_settings()
    url = f"{proxy_domain}/textdrip/otp/verify/"   
    headers = {
        "X-Server-IP": server_ip,
        'Authorization': f'Bearer {proxy_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    payload = {
        "input": mobile_number,
        "input_type": "mobile",
        "otp": otp,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
