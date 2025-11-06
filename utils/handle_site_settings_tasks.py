from django.utils import timezone
from django.db.models import Count, Q, Sum
from collections import defaultdict
from django.db.models.functions import TruncMonth

import json
from datetime import timedelta, date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from site_settings.models import ServicesStatus, ServicesStatusLogs
from dashboard.models import UserProfile
from django.contrib.auth import get_user_model

from utils.handle_PersonSearchAPI import ServiceTest_PersonSearch, ServiceTest_EmailService

UserModel = get_user_model()


from utils.handle_alerts import send_AlertOnTelegram, send_AlertOnEmail

from utils.handle_signalwire import ServiceTest_SignalwireAPI
from utils.handle_netnumbering import ServiceTest_NN_BostonServer, ServiceTest_NN_ChicagoServer, \
    ServiceTest_NN_OhioServer, ServiceTest_NN_VirginiaServer
from utils.handle_wavix import ServiceTest_Wavix_Server
from utils.handle_mailcheck import MailCheckApi
from utils.handle_dnctcpa import ServiceTest_DNC_SingleAPI
from utils.handle_dnctcpa_split import API_DNCTCPA_SPLIT
from utils.handle_mailerlite import SendMailerLiteNotification
from utils.handle_internal_apis import ServiceTest_LLRCheckSingleNumber_API, ServiceTest_LLRCheckRemainingCredits_API

from dashboard.models import Payment
from core.models import CsvFile
from api.models import APIData
from datastorage.models import NetNumberingDataLogs0, NetNumberingDataLogs3
from utils._base import returnDjModels



def util_ReturnServiceObj_Result(service_type):
    test_number = "7202728631"
    test_email = "vishal@textdrip.com"
    test_numbers_list = ["8152528560", "3033062439", "3106586602", "7205124901", "2468351191", "7202728631"]

    if service_type == ServicesStatus.SERVICE_TYPE.SIGNALWIRE:
        res_ = ServiceTest_SignalwireAPI(test_number)
    
    elif service_type == ServicesStatus.SERVICE_TYPE.NETNUMBERING_BOSTON:
        res_ = ServiceTest_NN_BostonServer(test_number)

    elif service_type == ServicesStatus.SERVICE_TYPE.NETNUMBERING_CHICAGO:
        res_ = ServiceTest_NN_ChicagoServer(test_number)

    elif service_type == ServicesStatus.SERVICE_TYPE.MAILCHECK:
        res_ = MailCheckApi(test_email)

    elif service_type == ServicesStatus.SERVICE_TYPE.DNCTCPA_SIGNLE:
        res_ = ServiceTest_DNC_SingleAPI(test_number)

    elif service_type == ServicesStatus.SERVICE_TYPE.DNCTCPA_BULK:
        res_ = API_DNCTCPA_SPLIT().serviceTest_DNCTCPA_BULK(test_numbers_list)

    elif service_type == ServicesStatus.SERVICE_TYPE.MAILERLITE:
        res_ = SendMailerLiteNotification(email=test_email, username='servicetest', account_status="Inactive", paid_user='NO', end_date=timezone.now())
    
    elif service_type == ServicesStatus.SERVICE_TYPE.LLR_CHECK_NUMBER:
        test_apikey = UserProfile.objects.values('api_key').get(user__email=test_email)['api_key']
        res_ = ServiceTest_LLRCheckSingleNumber_API(test_apikey, test_number)

    elif service_type == ServicesStatus.SERVICE_TYPE.LLR_CHECK_REMAINING_CREDITS:
        test_apikey = UserProfile.objects.values('api_key').get(user__email=test_email)['api_key']
        res_ = ServiceTest_LLRCheckRemainingCredits_API(test_apikey)

    elif service_type == ServicesStatus.SERVICE_TYPE.WAVIX:
        res_ = ServiceTest_Wavix_Server(test_number)

    elif service_type == ServicesStatus.SERVICE_TYPE.PERSON_SEARCH:
        res_ = ServiceTest_PersonSearch(test_number)

    elif service_type == ServicesStatus.SERVICE_TYPE.EMAIL_SERVICE:
        res_ = ServiceTest_EmailService()

    elif service_type == ServicesStatus.SERVICE_TYPE.NETNUMBERING_OHIO:
        res_ = ServiceTest_NN_OhioServer(test_number)

    elif service_type == ServicesStatus.SERVICE_TYPE.NETNUMBERING_VIRGINIA:
        res_ = ServiceTest_NN_VirginiaServer(test_number)

    else:
        res_ = False

    return res_



def autoCheck_ServiceTest(service_obj=None, service_uid=None):
    if service_uid:
        service_obj = ServicesStatus.objects.get(uid=service_uid)

    service_type = service_obj.service_type
    res_ = util_ReturnServiceObj_Result(service_type)
    print("obj", service_obj, " res", res_)

    ServicesStatusLogs.objects.create(service=service_obj, status=res_)

    give_a_alert = True 
    alert_message = ""

    if service_obj.service_status and res_:
        print("1-------------")
        give_a_alert = True
        service_obj.consecutive_failures_attempts = 0

    elif not service_obj.service_status and res_:
        #print("just back to service")
        alert_message = f"LLR-ServiceAlert | {service_obj.title} is up and running."
        print("2---" , alert_message)
        service_obj.consecutive_failures_attempts = 0
        service_obj.service_status = True 
        
    else:
        #print("service is false")
        alert_message = f"LLR-ServiceAlert | {service_obj.title} was unable to serve request | Failed Attempts {service_obj.consecutive_failures_attempts}/{service_obj.allow_consecutive_failures}"
        print("3---" , alert_message)

        service_obj.consecutive_failures_attempts = service_obj.consecutive_failures_attempts + 1
        service_obj.service_status = False 

        if service_obj.consecutive_failures_attempts >= service_obj.allow_consecutive_failures:
            alert_message = f"LLR-ServiceAlert | {service_obj.title} was unable to serve request | Developer needs to check it"
            print("4---" , alert_message)

            service_obj.allow_tracking = False 
    
   
    if give_a_alert:
        if service_obj.alert_on_telegram:
            print(f"send telegram alert {alert_message}--", alert_message)
            send_AlertOnTelegram(alert_message)
        elif service_obj.alert_on_email:
            #print("send email alert", alert_message)
            send_AlertOnEmail(email_="vishal@textdrip.com", subject_='LLR-ServiceAlert', message_=alert_message)
            # send_AlertOnEmail(email_="kirtan.pranshtech@gmail.com", subject_='LLR-ServiceAlert', message_=alert_message)

    service_obj.last_checked = timezone.now()
    service_obj.save()

    return res_
