"""
    - modified in march 24
    - no more modification need for now
"""

from requests import request as SEND_REQUEST
import json
from functools import reduce
from django.core.paginator import Paginator
from django.conf import settings

from utils.handle_logs import create_log_
from utils.handle_dnctcpa import dnctcpa_logger
from utils.utils_helpers import get_proxy_settings


class API_DNCTCPA_SPLIT:
    def __init__(self):
        # self.headers = {'Authorization': f'Basic {settings.TCPADNC_AUTH_TOKEN}'}
        # self.scrub_url = "https://api.tcpalitigatorlist.com/scrub/phones"
        # self.scrub_url_backup = "https://api101.tcpalitigatorlist.com/scrub/phones"
        # self.endpoints = [self.scrub_url, self.scrub_url_backup]

        # self.scrub_url = "https://api.tcpalitigatorlist.com/scrub/phones"
        # self.scrub_url_backup = "https://api101.tcpalitigatorlist.com/scrub/phones"
        self.endpoints = ["scrub_url", "scrub_url_backup"]

    #calling func
    def GetSmallList(self, numbers):
        full_matched_records = {}
        full_cleaned_records = {}
        paginator = Paginator(numbers, 2500)
        for page in range(1, paginator.num_pages+1):
            numbers_list = paginator.page(page).object_list
            matched_records, cleaned_records = self.getData(numbers_list)
            full_matched_records.update(matched_records)
            full_cleaned_records.update(cleaned_records)
        return full_matched_records, full_cleaned_records


    #helping func
    # def getData(self, numbers_list):
    #     for api_endpoint in self.endpoints:
    #         dnctcpa_logger.info(f'Request make for API_DNCTCPA_SPLIT for {api_endpoint}')
    #         try:
    #             payload = {'type': 'all', 'phones': json.dumps(numbers_list), 'small_list': 'true'}
    #             response = SEND_REQUEST("POST", api_endpoint, headers=self.headers, data=payload, timeout=600)
    #             results = response.json()
    #             try:
    #                 matched_records = results['match']
    #                 matched_records = list(mr for mr in matched_records.values())
    #                 matched_records = [{mr['phone_number']: mr['status']} for mr in matched_records]
    #                 matched_records = reduce(lambda a, b: {**a, **b}, matched_records)
    #             except:
    #                 matched_records = {}

    #             try:
    #                 cleaned_records = results['clean']
    #                 cleaned_records = list({mr: "clean"} for mr in cleaned_records.keys())
    #                 cleaned_records = reduce(lambda a, b: {**a, **b}, cleaned_records)
    #             except:
    #                 cleaned_records = {}
    #             return matched_records, cleaned_records
    #         except Exception as e:
    #             create_log_(log_type='dnctcpa_bulk', 
    #                 message=f"DNCTCPA BULK API wasn't able to serve request", 
    #                 exception_message=str(e)
    #             )

    #     exception_data = [{mr: 'UnKnown'} for mr in numbers_list]
    #     exception_data = reduce(lambda a, b: {**a, **b}, exception_data)
    #     return {}, exception_data

    
    def getData(self, numbers_list):
        for api_endpoint in self.endpoints:
            dnctcpa_logger.info(f"Request via Proxy for DNCTCPA {api_endpoint}")
            proxy_domain, proxy_token, server_ip = get_proxy_settings()
            try:
                url = f"{proxy_domain}/dnctcpa-proxy/"
                print(url,'=========================')
                payload = {
                    "numbers_list": numbers_list,
                    "api_endpoint": api_endpoint,
                }
                headers = {
                    "X-Server-IP": server_ip,
                    "Authorization": f"Bearer {proxy_token}",
                    "Content-Type": "application/json",
                }

                response = SEND_REQUEST(
                    "POST", url, headers=headers, data=json.dumps(payload), timeout=60
                )
                results = response.json()
                print(results,'======================*****************===')

                try:
                    matched_records = results.get("match", {})
                    matched_records = list(mr for mr in matched_records.values())
                    matched_records = [
                        {mr["phone_number"]: mr["status"]} for mr in matched_records
                    ]
                    matched_records = reduce(lambda a, b: {**a, **b}, matched_records)
                except:
                    matched_records = {}

                try:
                    cleaned_records = results.get("clean", {})
                    cleaned_records = [
                        {mr: "clean"} for mr in cleaned_records.keys()
                    ]
                    cleaned_records = reduce(lambda a, b: {**a, **b}, cleaned_records)
                except:
                    cleaned_records = {}

                return matched_records, cleaned_records

            except Exception as e:
                create_log_(
                    log_type="dnctcpa_bulk",
                    message="DNCTCPA Proxy API failed",
                    exception_message=str(e),
                )

        exception_data = [{mr: "UnKnown"} for mr in numbers_list]
        exception_data = reduce(lambda a, b: {**a, **b}, exception_data)
        return {}, exception_data


    # def serviceTest_DNCTCPA_BULK(self, numbers_list):
    #     for api_endpoint in self.endpoints:
    #         dnctcpa_logger.info(f'Request make for serviceTest_DNCTCPA_BULK for {api_endpoint}')
    #         payload = {'type': 'all', 'phones': json.dumps(numbers_list), 'small_list': 'true'}
    #         try:
    #             response = SEND_REQUEST("POST", api_endpoint, headers=self.headers, data=payload, timeout=60)
    #             response.raise_for_status()
    #             return True 
    #         except Exception as e:
    #             create_log_(log_type='dnctcpa_bulk', 
    #                 message=f"DNCTCPA BULK API wasn't able to serve request", 
    #                 exception_message=str(e)
    #             )
    #     return False
    
    def serviceTest_DNCTCPA_BULK(self, numbers_list):
        for api_endpoint in self.endpoints:
            dnctcpa_logger.info(f'Request make for serviceTest_DNCTCPA_BULK for {api_endpoint}')
            proxy_domain, proxy_token, server_ip = get_proxy_settings()

            url = f"{proxy_domain}/dnctcpa-proxy/"
            payload = {
                "numbers_list": numbers_list,
                "api_endpoint": api_endpoint
            }
            headers = {
                "X-Server-IP": server_ip,
                "Authorization": f"Bearer {proxy_token}",
                "Content-Type": "application/json",
            }

            try:
                response = SEND_REQUEST("POST", url, headers=headers, data=json.dumps(payload), timeout=60)
                response.raise_for_status()
                return True
            except Exception as e:
                create_log_(
                    log_type='dnctcpa_bulk',
                    message=f"DNCTCPA BULK API wasn't able to serve request",
                    exception_message=str(e)
                )
        return False
