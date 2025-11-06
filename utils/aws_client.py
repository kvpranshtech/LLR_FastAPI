import logging
import boto3
import requests
from django.conf import settings
from utils.utils_helpers import get_current_env,get_proxy_settings
logger = logging.getLogger(__name__)

def get_s3_client():
    proxy_domain, proxy_token, server_ip = get_proxy_settings()
    if not proxy_domain or not proxy_token:
        print("❌ Proxy settings not configured properly.")
        return None
    
    logger.info(f"🔑 Fetching S3 credentials from proxy for env: {get_current_env()}")
    logger.info(f"🌐 Proxy Domain: {proxy_domain}")
    logger.info(f"🔒 Proxy Token: {'*' * len(proxy_token)}")

    try:
        response = requests.post(
            f"{proxy_domain}/aws-s3-keys/?env={get_current_env()}",
            headers={
                 "X-Server-IP": server_ip,
                "Authorization": f"Bearer {proxy_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        logger.info(f"🔒 Data : {data} ================================================== ")

        aws_access_key = data.get("aws_access_key_id")
        aws_secret_key = data.get("aws_secret_access_key")
        aws_region = data.get("aws_region_name")

        if not aws_access_key or not aws_secret_key:
            raise ValueError("Proxy did not return valid AWS credentials")

        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )
    except Exception as e:
        print(f"❌ Error creating S3 client via proxy: {str(e)}")
        return None
