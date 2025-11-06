import logging
import time

from django.core.paginator import Paginator
from django.db.models import F

from django.contrib.auth import get_user_model
from django.http import JsonResponse

# from socket_app.consumers import send_progress
from utils.handle_push_fotification import send_push_notification

UserModel = get_user_model()
from django.utils.timezone import now
from celery import shared_task
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction
import traceback
from utils.logs import user_bulk_upload_activity
from adminv2.models import DataEnrichmentDataLogsDailyAnalytics, UserActivityLog
#utils
from utils.handle_tasks_utils import (
    UploadCSVDATA,UploadCSVEmailDATA,
    saveCsvFileDataToCSV, saveCsvFileEmailDataToCSV,
    endatosaveCsvFileDataToCSV,
    api_fixNumberTypesData,

    fixNumberTypesData_V2,
    handleReversedCredits_v3, handleReversedCreditsEmail_v3,
    UploadCSVFirstLastName,
    endatoHandleReversedCredits_v1,
    UploadendatoCSVDATA,
    util_handleCreditsAnalytics,
    util_handleCreditsAnalyticsBulkApi,
    util_count_invalid_data,
    # helper_CsvFileDataWavix,
    )
from utils.handle_dnctcpa_split import API_DNCTCPA_SPLIT
from utils.handle_django import UpdateBulkAPIDetailInfo, UpdateCSVDetailInfo,updateProcessedRows,updateProcessedRowsv2, updateEmailProcessedRows
from utils.utils import returnCleanDNCType
from utils.is_number_inmodels import isNumberFoundInModels, isNumberFoundInModels_2, returnPhoneRequiredData
from utils.handle_emailing import email_SendAfterCSVSuccessfull, email_SendAfterCSVFailed, sendWelcomeEmail
from utils.handle_mailerlite import SendMailerLiteNotification
from utils.handle_number_info import handleWavixBulkApi_v1,returnNumberData_v3, returnNumberData_v5,returnNumberDncData_v3, handleDNCBULKAPI_v3,returnNumberData_v4,Endato_CheckNumberDataThroughDatabase, returnEmailData_v3,returnNumberData_v6
from utils._base import format_dnctype,returnCleanPhone_Or_None, returnCleanCarrierName
from utils.handle_saving_data import saveUserCheckedDataIntoLogsTable,saveEndatoData,saveUserCheckedDataIntoEndatoLogsTable, saveUserEmailCheckedDataIntoLogsTable
from utils.handle_cron_tasks import (
    autoClean_RawCsvFiles,
    autoClean_CsvFileData,
    autoClean_InvalidNumberDataLogs,
    autoClean_DNCDataLogs,
    autoClean_TelynxDataLogs,
    autoClean_SignalwireDataLogs,
    autoClean_NetNumberingDataLogs,
    autoClean_APIData,
    autoClean_UserDataLogs,
    autoClean_CeleryTaskResults,
    autoClean_CustomSiteLogs,
    autoClean_LogFile,
    autoClean_CeleryLogFile,
    autoClean_CeleryBeatLogFile,
    autoClean_MediaFiles, autoClean_testusers, refresh_team_tokens, renew_subscriptions_credits,
    renew_custom_subscriptions_credits, cancel_custom_subscriptions,ssl_expiry_alerts

)

from utils.handle_site_settings_tasks import autoCheck_ServiceTest
#models
from api.models import APIBULK, APIData
from core.models import CsvFileData, CsvFile,CheckEndatoApi,EndatoApiResponse,EndatoCsvFileData
from dashboard.models import UserProfile
from datastorage.models import (
    UserDataLogs0,
    UserDataLogs1,
    UserDataLogs2,
    UserDataLogs3,
    UserDataLogs4,
    UserDataLogs5,
    UserDataLogs6,
    UserDataLogs7,
    UserDataLogs8,
    UserDataLogs9,

    WavixRequestTracker
)

from django.utils import timezone
from datetime import timedelta

from django.core.cache import cache
from site_settings.models import ApiPriorities
from celery import shared_task
import logging
from django.utils import timezone
from django.db.models import F
from concurrent.futures import ThreadPoolExecutor
import random
from utils.handle_EndatoApi import API_Endato

from core.models import EndatoApiResponse, EndatoBULK
from utils.handle_EndatoApi import getBulkEnrichedData, getEnrichedData

logger = logging.getLogger(__name__)

"""
    new celery method - april 24
    - method to handle to auto service alerts
    - this method is mainly build for calling it through periodic tasks base on user service status settings
"""
@shared_task
def celery_handleAutoServiceAlert(**kwargs):
    try:
        res_ = autoCheck_ServiceTest(service_uid=str(kwargs['uid']))
        return str(res_)
    except Exception as e:
        return f"{e}"


@shared_task 
def celery_handleFailedFile(file_uid):
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
        logs = {}
        csvfiledata = CsvFileData.objects.filter(csvfile=csvfile).delete()
        logs['file_uid'] = file_uid
        logs['csvfiledata'] = csvfiledata[0]
        uploaded_at = csvfile.uploaded_at
        user = csvfile.user
        logs['UserDataLogs0'] = UserDataLogs0.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs1'] = UserDataLogs1.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs2'] = UserDataLogs2.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs3'] = UserDataLogs3.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs4'] = UserDataLogs4.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs5'] = UserDataLogs5.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs6'] = UserDataLogs6.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs7'] = UserDataLogs7.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs8'] = UserDataLogs8.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        logs['UserDataLogs9'] = UserDataLogs9.objects.filter(user=user, timestamp=uploaded_at).count()[0]
        return logs
    except:
        return {'file_uid': file_uid, 'message':'failed to clear the file data from tables'}



#updated in aug 23 - no more modifications needed
@shared_task 
def celery_loadCSVFileDatatoUserDataLogs_vN(file_uid,checkprrows=False):
    saveUserCheckedDataIntoLogsTable(file_uid,checkprrows)
    return None


@shared_task
def celery_loadCSVFileEmailDatatoUserDataLogs_vN(file_uid,checkprrows=False):
    saveUserEmailCheckedDataIntoLogsTable(file_uid,checkprrows)
    return None


#updated in aug 23 - no more modifications needed
@shared_task 
def celery_loadCSVFileDatatoUserDataLogsEndato_vN(file_uid,DjModel,checkprrows=False):
    saveUserCheckedDataIntoEndatoLogsTable(file_uid,DjModel,checkprrows)
    return None
"""
    - used in allauth after confirmation email
    - modified july 2023 
    - no more modification needed
"""
@shared_task 
def celery_SendEmailsAfterConfirmingEmail(user_email, user_username):
    #for mailerlite notification 
    try:
        SendMailerLiteNotification(email=user_email, username=user_username, account_status="Active", paid_user='NO')
    except:pass

    #send welcome email
    try:
        sendWelcomeEmail(email_send_to=user_email, allow_cc=True)
    except: pass
    return None


"""
    - handling upload file and it's methods 
    - modified in aug 2023 
    -  more modification needed
"""


logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True,
             retry_kwargs={'max_retries': 5})
def celery_HandleUpload(self, data, use_split=False, device_tokens=None):
    file_uid = data['file_uid']
    email = data['email']
    filename = data['filename']
    download_file_url = data['download_file_url']
    up = UserProfile.objects.get(user=UserModel.objects.get(email=email))

    # added on 09/09/2024
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
    except CsvFile.DoesNotExist:
        logger.error(f"CSV file with UID {file_uid} not found.")
        return None

    if self.request.retries >= self.max_retries:
        csvfile.is_failed = True
        csvfile.completed_at = timezone.now()  # Set completion time on failure
        csvfile.duration = csvfile.completed_at - csvfile.uploaded_at
        csvfile.save()

        try:
            logs = {}

            csvfile = CsvFile.objects.get(uid=file_uid)
            csvfile.is_failed = True
            csvfile.save()

            try:
                up = UserProfile.objects.get(user=UserModel.objects.get(email=email))
                logs['credits_before_failed'] = up.credits
                up.credits = F('credits') + csvfile.total_rows_charged
                up.save()

                if up.email_notifications:
                    email_SendAfterCSVFailed_res = email_SendAfterCSVFailed(email, filename, allow_cc=False)

                try:
                    celery_handleFailedFile.delay(file_uid)
                except Exception as e:
                    logger.error(f"Error queuing failed file task: {str(e)}")

                logs['credits_after_failed'] = up.credits
                logs['total_rows_charged'] = csvfile.total_rows_charged
                if up.email_notifications:
                    logs['email_SendAfterCSVFailed'] = email_SendAfterCSVFailed_res

                return logs
            except UserProfile.DoesNotExist:
                logger.error(f"UserProfile for email {email} not found.")
        except Exception as e:
            logger.error(f"Error processing failure: {str(e)}")
        return None

    if self.request.retries < 1:
        try:
            UploadCSVDATA(file_uid)
        except Exception as e:
            logger.error(f"Error uploading CSV data for {file_uid}: {str(e)}")
            raise

    try:
        records = CsvFileData.objects.filter(csvfile__uid=file_uid)
        current_priority = ApiPriorities.objects.first()
        wavix_batch_checks = False
        check_personsearch_api = False
        # if current_priority and current_priority.api_first_priority == ApiPriorities.APITYPE_FIRST_PRIORITY.WAVIX and current_priority.wavix_bulk_check_api:
        #     wavix_batch_checks = True

        check_in_personsearch = CheckEndatoApi.objects.filter(csvfile=csvfile,check_with_endato=True).first()
        if check_in_personsearch:    
                check_personsearch_api = True
    
        paginator = Paginator(records, 2000)

        for page in range(1, paginator.num_pages + 1):
            new_objs = []
            objects_list = paginator.page(page).object_list

            input_numbers_list = [str(ob.phonenumber).strip() for ob in objects_list if
                                  ob.phonenumber != 'invalid_data']
            dnc_datas = handleDNCBULKAPI_v3(input_numbers_list)
            if wavix_batch_checks:
                handleWavixBulkApi_v1(input_numbers_list,file_uid)
            
            def GetTypeData(row):
                clean_phone = row.phonenumber
                if clean_phone == 'invalid_data':
                    row.line_type = 'invalid'
                    row.dnc_type = 'invalid'
                    row.number_checked_from_db = False
                else:
                    try:
                        if check_personsearch_api:
                            personsearch_data =  returnNumberData_v6(row.phonenumber)
                            if personsearch_data.get('first_name') == 'n/a' and personsearch_data.get('last_name')== 'n/a' and personsearch_data.get('age') == 'n/a' and personsearch_data.get('addresses') == 'n/a' and personsearch_data.get('phones') == 'n/a' and personsearch_data.get('emails')  == 'n/a':
                                row.endato_invalid_flag = True   
                                row.is_processed_through_endato = True
                                row.data_enrichment_checked_from_db = personsearch_data.get('found_in_db',False)
                            else:
                                row.first_name = personsearch_data.get('first_name', '')
                                row.last_name = personsearch_data.get('last_name', '')
                                row.age = personsearch_data.get('age')
                                row.addresses = personsearch_data.get('addresses')
                                row.phones = personsearch_data.get('phones')
                                row.emails = personsearch_data.get('emails')
                                row.data_enrichment_checked_from_db = personsearch_data.get('found_in_db',False)
                                # row.identityScore = personsearch_data.get('identityScore')
                                row.is_processed_through_endato = True
                                
                        phone_data = returnNumberData_v3(clean_phone,shuffle=False)
                        line_type = phone_data.get('line_type', 'invalid')
                        if line_type == 'invalid':
                            row.line_type = 'invalid'
                            row.dnc_type = 'invalid'
                            row.number_checked_from_db = phone_data.get('found_from_db',False)
                        else:
                            row.line_type = line_type
                            row.dnc_type = dnc_datas.get(clean_phone, 'n/a')
                            row.carrier_name = phone_data.get('carrier_name', 'n/a')
                            row.city = phone_data.get('city', 'n/a')
                            row.state = phone_data.get('state', 'n/a')
                            row.country = phone_data.get('country', 'n/a')
                            row.number_checked_from_db = phone_data.get('found_from_db',False)
                    except Exception as e:
                        logger.error(f"Error processing row {row.id} {row.phonenumber}: {str(e)}")
                        logger.error(traceback.format_exc())
                        row.line_type = 'invalid'
                        row.dnc_type = 'invalid'
                        row.number_checked_from_db = False
                
                if check_personsearch_api:
                    row.is_processed_through_endato = True
                row.is_processed = True
                new_objs.append(row)


            with ThreadPoolExecutor(max_workers=7) as executor:
                executor.map(GetTypeData, objects_list)
            
            if check_personsearch_api:
                CsvFileData.objects.bulk_update(new_objs,
                                            ['line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country','is_processed','first_name', 'last_name', 'age', 'addresses', 'phones', 'emails','endato_invalid_flag','is_processed_through_endato','data_enrichment_checked_from_db','number_checked_from_db'])
            else:
                CsvFileData.objects.bulk_update(new_objs,
                                            ['line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country','is_processed','number_checked_from_db'])
            logger.info(f"Updated processed rows in DB: {csvfile.processed_rows}")

    except Exception as e:
        logger.error(f"Error during CSV processing: {str(e)}")
        raise


    try:
        # if wavix_batch_checks:
        #     try:
        #         helper_CsvFileDataWavix(file_uid)
        #     except Exception as e:
        #         print(f"Error during WAVIX batch processing: {str(e)}")
        fixNumberTypesData_V2_count = fixNumberTypesData_V2(file_uid)
        UpdateCSVDetailInfo_res = UpdateCSVDetailInfo(file_uid)
        updateProcessedRowsRecords = updateProcessedRows(file_uid)
    

        # check_in_endato = CheckEndatoApi.objects.filter(csvfile=csvfile,check_with_endato=True).first()
        # if check_in_endato:
        #     check_in_endato.status = CheckEndatoApi.RequestStatus.PROCESSING
        #     check_in_endato.save()
        #     try:
        #         UploadCSVFirstLastName(file_uid)
        #     except Exception as e:
        #         error_details = traceback.format_exc()
        #         logger.error(f"Error uploading CSV data for {file_uid}: {error_details}")
        #         raise

        #     try:
        #         records = EndatoApiResponse.objects.filter(csvfile__uid=file_uid).order_by('id')  
        #         paginator = Paginator(records, 900)
        #         for page in range(1, paginator.num_pages + 1):
        #             new_objs_two = []
        #             objects_list = paginator.page(page).object_list

        #             def GetTypeData(row):
        #                 apidata = returnNumberData_v6(row.phone_number,row.id,row.first_name,row.last_name)
        #                 csvfile_data = CsvFileData.objects.filter(csvfile=row.csvfile, phonenumber=row.phone_number).first()
        #                 if apidata['first_name'] == 'n/a' and apidata['last_name'] == 'n/a' and apidata['age'] == 'n/a' and apidata['addresses'] == 'n/a' and apidata['phones'] == 'n/a' and apidata['emails']  == 'n/a' and apidata['identityScore'] == 'n/a' :
        #                     csvfile_data.endato_invalid_flag = True   
        #                     csvfile_data.is_processed_through_endato = True  
        #                 else:   
        #                     csvfile_data.first_name = apidata['first_name']
        #                     csvfile_data.last_name = apidata['last_name']
        #                     csvfile_data.age = apidata['age']
        #                     csvfile_data.addresses = apidata['addresses']
        #                     csvfile_data.phones = apidata['phones']
        #                     csvfile_data.emails = apidata['emails']
        #                     csvfile_data.identityScore = apidata['identityScore']
        #                     csvfile_data.is_processed_through_endato = True
                
        #                 new_objs_two.append(csvfile_data)
                            
                            
        #             with ThreadPoolExecutor(max_workers=7) as executor:
        #                 executor.map(GetTypeData, objects_list)
                    
        #             CsvFileData.objects.bulk_update(new_objs_two,
        #                                     ['first_name', 'last_name', 'age', 'addresses', 'phones', 'emails','identityScore','endato_invalid_flag','is_processed_through_endato'])
                    
        #         check_in_endato.status = CheckEndatoApi.RequestStatus.COMPLETED
        #         check_in_endato.save()
        #     except Exception as e:
        #         error_details = traceback.format_exc()
        #         logger.error(f"Error handling pagination for {file_uid}: {error_details}")
        #         raise


        
        if check_personsearch_api:
            saveCsvFileDataToCSV_res = saveCsvFileDataToCSV(file_uid,True,False)
        else:
            saveCsvFileDataToCSV_res = saveCsvFileDataToCSV(file_uid,False,False)

        csvfile.is_complete = True
        csvfile.completed_at = timezone.now()  
        csvfile.duration = csvfile.completed_at - csvfile.uploaded_at  
        csvfile.save()


        if device_tokens:
            for token in device_tokens:
                send_push_notification(
                    token=token,
                    title="File processed successfully",
                    body=f"Your file '{csvfile.csvfile_name}' has finished processing.",
                    notification_type="csv_file",
                    file_id=csvfile.uid
                )

        if up.email_notifications:
            email_SendAfterCSVSuccessfull_res = email_SendAfterCSVSuccessfull(email, filename, download_file_url, allow_cc=False)

        
        # up = UserProfile.objects.get(user=csvfile.user)
        # if csvfile.is_complete:
        #     user_bulk_upload_activity(
        #         user=csvfile.user,
        #         description=f"Credits After Duplicates",
        #         actions=UserActivityLog.ActionType.BULKUPLOAD,
        #         amount=0,
        #         prev_credits=up.credits + csvfile.total_rows_charged,
        #         remaining_credits= up.credits ,
        #         earned_credits=0
        #     )
         
        #email_SendAfterCSVSuccessfull_res = email_SendAfterCSVSuccessfull(email, filename, download_file_url ,allow_cc=False)
        try:
            up = UserProfile.objects.get(user=UserModel.objects.get(email=email))
        except Exception as e:
            logger.info(f"USER PROFILE NOT FOUND {e}")
        

        handleReversedCredits_v3_res = handleReversedCredits_v3(file_uid)

        update_invalid_data_counts =  util_count_invalid_data(file_uid)
        
        up = UserProfile.objects.get(user=csvfile.user)
        # if csvfile.is_complete:
        #     user_bulk_upload_activity(
        #         user=csvfile.user,
        #         description=f"Credits After Duplicates",
        #         actions=UserActivityLog.ActionType.BULKUPLOAD,
        #         amount=0,
        #         prev_credits=up.credits + csvfile.total_rows_charged,
        #         remaining_credits= up.credits ,
        #         earned_credits=0
        #     )
        
        if check_personsearch_api:
            DjModel = CsvFileData
            handleReverseCredits_endato_checks = endatoHandleReversedCredits_v1(DjModel,file_uid)
        else:
            handleReverseCredits_endato_checks = ''
    
        try:
            celery_loadCSVFileDatatoUserDataLogs_vN.delay(file_uid)
            if check_personsearch_api:
                DjModel = "CsvFileData"
                celery_loadCSVFileDatatoUserDataLogsEndato_vN.delay(file_uid,DjModel)
        except Exception as e:
            logger.error(f"Error queuing CSV data logs task: {str(e)}")

        

        
        try:
            util_handleCreditsAnalytics(file_uid,CsvFileData)
        except Exception as e:
            logger.error(f"Error updating credits analytics:{str(e)}")

        logs = {
            'file_uid': file_uid,
            'fixNumberTypesData_V2': fixNumberTypesData_V2_count,
            'UpdateCSVDetailInfo': UpdateCSVDetailInfo_res,
            'updateProcessedRowsRecords': updateProcessedRowsRecords,
            'saveCsvFileDataToCSV_res': saveCsvFileDataToCSV_res,
            # 'email_SendAfterCSVSuccessfull': email_SendAfterCSVSuccessfull_res,
            'handleReversedCredits_v3': handleReversedCredits_v3_res,
            'handleReverseCredits_endato_checks':handleReverseCredits_endato_checks,
            'update_invalid_data_counts':update_invalid_data_counts,
        }

        if up.email_notifications:
            logs['email_SendAfterCSVSuccessfull'] = email_SendAfterCSVSuccessfull_res

        return logs
    
        
        
    
        
    except Exception as e:
        logger.error(f"Error completing the CSV process: {str(e)}")
        raise



# from api.models import CsvFileEmail, CsvFileDataEmail
# @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True,
#              retry_kwargs={'max_retries': 5})
# def celery_HandleUploadEmail(self, data, use_split=False):
#     file_uid = data['file_uid']
#     email = data['email']
#     filename = data['filename']
#     download_file_url = data['download_file_url']

#     # added on 09/09/2024
#     try:
#         csvfile = CsvFileEmail.objects.get(uid=file_uid)
#     except CsvFileEmail.DoesNotExist:
#         logger.error(f"CSV file with UID {file_uid} not found.")
#         return None

#     if self.request.retries >= self.max_retries:
#         csvfile.is_failed = True
#         csvfile.completed_at = timezone.now()  # Set completion time on failure
#         csvfile.duration = csvfile.completed_at - csvfile.uploaded_at
#         csvfile.save()

#         try:
#             logs = {}

#             csvfile = CsvFileEmail.objects.get(uid=file_uid)
#             csvfile.is_failed = True
#             csvfile.save()

#             try:
#                 up = UserProfile.objects.get(user=UserModel.objects.get(email=email))
#                 logs['credits_before_failed'] = up.email_credits
#                 up.email_credits = F('email_credits') + csvfile.total_rows_charged
#                 up.save()
#                 email_SendAfterCSVFailed_res = email_SendAfterCSVFailed(email, filename, allow_cc=False)
#                 try:
#                     celery_handleFailedFile.delay(file_uid)
#                 except Exception as e:
#                     logger.error(f"Error queuing failed file task: {str(e)}")
#                 print("------------------>",up.email_credits)
#                 logs['credits_after_failed'] = up.email_credits
#                 logs['total_rows_charged'] = csvfile.total_rows_charged
#                 logs['email_SendAfterCSVFailed'] = email_SendAfterCSVFailed_res
#                 return logs
#             except UserProfile.DoesNotExist:
#                 logger.error(f"UserProfile for email {email} not found.")
#         except Exception as e:
#             logger.error(f"Error processing failure: {str(e)}")
#         return None

#     if self.request.retries < 1:
#         try:
#             UploadCSVEmailDATA(file_uid)
#         except Exception as e:
#             logger.error(f"Error uploading CSV data for {file_uid}: {str(e)}")
#             raise

#     try:
#         records = CsvFileDataEmail.objects.filter(csvfile__uid=file_uid)
#         paginator = Paginator(records, 900)


#         print()
#         for page in range(1, paginator.num_pages + 1):

#             objects_list = paginator.page(page).object_list
#             email_list = [str(ob.email).strip() for ob in objects_list if ob.email]

#             # print(f"{email_list}====================================>>>>>>")
#             def ProcessEmail(row):
#                 clean_email = row.email
#                 if not clean_email:
#                     row.is_processed = True
#                     row.email_format = False
#                     row.domain_exists = False
#                     row.mx_record = False
#                 else:
#                     try:
                        
#                         existing_record = CsvFileDataEmail.objects.filter(
#                             email=clean_email,
#                             csvfile__user=row.csvfile.user
#                             # csvfile__uploaded_by=row.csvfile.uploaded_by
#                         ).last()
#                         # print("==================>",clean_email)

#                         if existing_record:
#                             row.is_duplicate = True
#                             row.email_format = existing_record.email_format
#                             row.mx_record = existing_record.mx_record
#                             row.domain_exists = existing_record.domain_exists
#                             row.disposable_email = existing_record.disposable_email
#                             row.role_account = existing_record.role_account
#                             row.common_typo = existing_record.common_typo
#                             row.spf_record = existing_record.spf_record
#                             row.dkim_record = existing_record.dkim_record
#                             row.dmarc_record = existing_record.dmarc_record
#                             row.new_domain = existing_record.new_domain
#                             row.valid_tld = existing_record.valid_tld
#                             row.is_spam = existing_record.is_spam
#                             row.feee_domain = existing_record.feee_domain

#                             try:
#                                 # Get the user who uploaded the CSV file
#                                 user = row.csvfile.user
#                                 user_profile = UserProfile.objects.get(user=user)
                                
#                                 # Reverse credits for the duplicate (e.g., adding 1 credit back)
#                                 user_profile.credits = F('credits') + 1  # Adjust this logic if needed
#                                 user_profile.save()

#                                 row.csvfile.total_rows_duplicates += 1
#                                 row.csvfile.total_rows_charged -= 1  # Adjust the total credits if necessary
#                                 # row.csvfile.save()

#                                 logger.info(f"Total Rows Duplicates {row.csvfile.total_rows_duplicates}")
#                                 logger.info(f"Total Rows Charged {row.csvfile.total_rows_charged}")
#                                 logger.info(f"Reversed credits for user {user.email}, current credits: {user_profile.credits}")

#                             except UserProfile.DoesNotExist:
#                                 logger.error(f"UserProfile not found for user {row.csvfile.user.email}")
#                             except Exception as e:
#                                 logger.error(f"Error during credits reversal for user {row.csvfile.user.email}: {str(e)}")
#                         else:
#                             email_data = returnEmailData_v3(clean_email)  # Hypothetical function to process email
#                             print(f"=========================>{email_data}")
#                             print(f"=========================>{email_data.get('email_format')}")
#                             print(f"=========================>{email_data.get('results', {}).get('email_format', 'unknown')}")
#                             row.email_format = email_data.get('results', {}).get('email_format', 'unknown')
#                             if row.email_format == "valid":
#                                 row.email_format = True
#                             else:
#                                 row.email_format = False
#                             row.mx_record = email_data.get('results', {}).get('mx_record', False)
#                             if row.mx_record == "available":
#                                 row.mx_record = True
#                             else:
#                                 row.mx_record = False
#                             row.domain_exists = email_data.get('results', {}).get('domain_exists', False)
#                             row.disposable_email = email_data.get('results', {}).get('disposable_email', False)
#                             row.role_account = email_data.get('results', {}).get('role_account', False)
#                             row.common_typo = email_data.get('results', {}).get('common_typo', False)
#                             row.spf_record = email_data.get('results', {}).get('spf_record', False)
#                             row.dkim_record = email_data.get('results', {}).get('dkim_record', False)
#                             row.dmarc_record = email_data.get('results', {}).get('dmarc_record', False)
#                             row.new_domain = email_data.get('results', {}).get('new_domain', False)
#                             row.valid_tld = email_data.get('results', {}).get('valid_tld', False)
#                             row.is_spam = email_data.get('results', {}).get('is_spam', False)
#                             row.feee_domain = email_data.get('results', {}).get('free_domain', False)
#                     except Exception as e:
#                         logger.error(f"Error processing row {row.id}: {str(e)}")
#                         row.email_format = False
#                         row.domain_exists = False
#                         row.mx_record = False
#                 row.is_processed = True
#                 # row.save()
#             with ThreadPoolExecutor(max_workers=7) as executor:
#                 executor.map(ProcessEmail, objects_list)
#             print(f"{objects_list}====================>")
#             CsvFileDataEmail.objects.bulk_update(
#                 objects_list,
#                 [
#                     'is_processed', 'email_format', 'mx_record', 'domain_exists',
#                     'disposable_email', 'role_account', 'common_typo', 'spf_record',
#                     'dkim_record', 'dmarc_record', 'new_domain', 'valid_tld',
#                     'is_spam', 'feee_domain', 'is_duplicate'
#                 ]
#             )
#             logger.info(f"Updated processed rows in DB: {csvfile.processed_rows}")

#     except Exception as e:
#         logger.error(f"Error during CSV processing: {str(e)}")
#         raise

#     csvfile.is_complete = True
#     csvfile.completed_at = timezone.now()  # Set completion time on success
#     csvfile.duration = csvfile.completed_at - csvfile.uploaded_at  # Calculate duration
#     csvfile.save()

#     # Additional steps
#     try:
#         # fixNumberTypesData_V2_count = fixNumberTypesData_V2(file_uid)
#         # UpdateCSVDetailInfo_res = UpdateCSVDetailInfo(file_uid)
#         updateProcessedRowsRecords = updateEmailProcessedRows(file_uid)

#         saveCsvFileDataToCSV_res = saveCsvFileEmailDataToCSV(file_uid)

#         email_SendAfterCSVSuccessfull_res = email_SendAfterCSVSuccessfull(email, filename, download_file_url,
#                                                                           allow_cc=False)
#         # handleReversedCredits_v3_res = handleReversedCreditsEmail_v3(file_uid)

#         try:
#             celery_loadCSVFileEmailDatatoUserDataLogs_vN.delay(file_uid)
#         except Exception as e:
#             logger.error(f"Error queuing CSV data logs task: {str(e)}")

#         logs = {
#             'file_uid': file_uid,
#             # 'fixNumberTypesData_V2': fixNumberTypesData_V2_count,
#             # 'UpdateCSVDetailInfo': UpdateCSVDetailInfo_res,
#             'updateProcessedRowsRecords': updateProcessedRowsRecords,
#             'saveCsvFileDataToCSV_res': saveCsvFileDataToCSV_res,
#             'email_SendAfterCSVSuccessfull': email_SendAfterCSVSuccessfull_res,
#             # 'handleReversedCredits_v3': handleReversedCredits_v3_res,
#         }
#         return logs
#     except Exception as e:
#         logger.error(f"Error completing the CSV process: {str(e)}")
#         raise

from api.models import CsvFileEmail, CsvFileDataEmail
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True,
             retry_kwargs={'max_retries': 5})
def celery_HandleUploadEmail(self, data, use_split=False, device_tokens=None):
    file_uid = data['file_uid']
    email = data['email']
    filename = data['filename']
    download_file_url = data['download_file_url']
    up = UserProfile.objects.get(user=UserModel.objects.get(email=email))

    # added on 09/09/2024
    try:
        csvfile = CsvFileEmail.objects.get(uid=file_uid)
    except CsvFileEmail.DoesNotExist:
        logger.error(f"CSV file with UID {file_uid} not found.")
        return None

    if self.request.retries >= self.max_retries:
        csvfile.is_failed = True
        csvfile.completed_at = timezone.now()  # Set completion time on failure
        csvfile.duration = csvfile.completed_at - csvfile.uploaded_at
        csvfile.save()

        try:
            logs = {}

            csvfile = CsvFileEmail.objects.get(uid=file_uid)
            csvfile.is_failed = True
            csvfile.save()

            try:
                up = UserProfile.objects.get(user=UserModel.objects.get(email=email))
                logs['credits_before_failed'] = up.email_credits
                up.email_credits = F('email_credits') + csvfile.total_rows_charged
                up.save()
                if up.email_notifications:
                    email_SendAfterCSVFailed_res = email_SendAfterCSVFailed(email, filename, allow_cc=False)

                try:
                    celery_handleFailedFile.delay(file_uid)
                except Exception as e:
                    logger.error(f"Error queuing failed file task: {str(e)}")

                print("------------------>",up.email_credits)
                logs['credits_after_failed'] = up.email_credits
                logs['total_rows_charged'] = csvfile.total_rows_charged

                if up.email_notifications:
                    logs['email_SendAfterCSVFailed'] = email_SendAfterCSVFailed_res

                return logs
            except UserProfile.DoesNotExist:
                logger.error(f"UserProfile for email {email} not found.")
        except Exception as e:
            logger.error(f"Error processing failure: {str(e)}")
        return None

    if self.request.retries < 1:
        try:
            # UploadCSVEmailDATA(file_uid, email)
            # duplicates_data = UploadCSVEmailDATA(file_uid, email)
            csvfile.total_rows_duplicates = UploadCSVEmailDATA(file_uid, email)
            csvfile.save()
            # print(f"===============**********==========************>", UploadCSVEmailDATA(file_uid, email))
            # print(f"===============8888888888==========888888888888>{csvfile.total_rows_duplicates} {duplicates_data}")
        except Exception as e:
            logger.error(f"Error uploading CSV data for {file_uid}: {str(e)}")
            raise

    try:
        records = CsvFileDataEmail.objects.filter(csvfile__uid=file_uid)
        paginator = Paginator(records, 900)
        print(f"===============**********==========************>{csvfile.total_rows_duplicates}")

        print()
        for page in range(1, paginator.num_pages + 1):
            # new_objs = []
            # objects_list = paginator.page(page).object_list
            # input_numbers_list = [str(ob.phonenumber).strip() for ob in objects_list if ob.phonenumber != 'invalid_data']
            # dnc_datas = handleDNCBULKAPI_v3(input_numbers_list)
            #
            # def GetTypeData(row):
            #     clean_phone = row.phonenumber
            #     if clean_phone == 'invalid_data':
            #         row.line_type = 'invalid'
            #         row.dnc_type = 'invalid'
            #     else:
            #         try:
            #             phone_data = returnNumberData_v3(clean_phone, shuffle=False)
            #             line_type = phone_data.get('line_type', 'invalid')
            #             if line_type == 'invalid':
            #                 row.line_type = 'invalid'
            #                 row.dnc_type = 'invalid'
            #             else:
            #                 row.line_type = line_type
            #                 row.dnc_type = dnc_datas[clean_phone]
            #                 row.carrier_name = phone_data.get('carrier_name', 'n/a')
            #                 row.city = phone_data.get('city', 'n/a')
            #                 row.state = phone_data.get('state', 'n/a')
            #                 row.country = phone_data.get('country', 'n/a')
            #         except Exception as e:
            #             logger.error(f"Error processing row {row.id}: {str(e)}")
            #             row.line_type = 'invalid'
            #             row.dnc_type = 'invalid'
            #     row.is_processed = True
            #     row.save()
            #     new_objs.append(row)

            objects_list = paginator.page(page).object_list
            email_list = [str(ob.email).strip() for ob in objects_list if ob.email]
            print(f"==============-********-------//////===========************>{csvfile.total_rows_duplicates}")
            # print(f"{email_list}====================================>>>>>>")
            def ProcessEmail(row):
                clean_email = row.email
                if not clean_email:
                    row.is_processed = True
                    row.email_format = False
                    row.domain_exists = False
                    row.mx_record = False
                else:
                    try:
                        print("==================>",clean_email)
                        email_data = returnEmailData_v3(clean_email)  # Hypothetical function to process email
                        print(f"=========================>{email_data}")
                        print(f"=========================>{email_data.get('email_format')}")
                        print(f"=========================>{email_data.get('results', {}).get('email_format', 'unknown')}")
                        row.email_format = email_data.get('results', {}).get('email_format', 'unknown')
                        if row.email_format == "valid":
                            row.email_format = True
                        else:
                            row.email_format = False
                        row.mx_record = email_data.get('results', {}).get('mx_record', False)
                        if row.mx_record == "available":
                            row.mx_record = True
                        else:
                            row.mx_record = False
                        row.domain_exists = email_data.get('results', {}).get('domain_exists', False)
                        row.disposable_email = email_data.get('results', {}).get('disposable_email', False)
                        row.role_account = email_data.get('results', {}).get('role_account', False)
                        row.common_typo = email_data.get('results', {}).get('common_typo', False)
                        row.spf_record = email_data.get('results', {}).get('spf_record', False)
                        row.dkim_record = email_data.get('results', {}).get('dkim_record', False)
                        row.dmarc_record = email_data.get('results', {}).get('dmarc_record', False)
                        row.new_domain = email_data.get('results', {}).get('new_domain', False)
                        row.valid_tld = email_data.get('results', {}).get('valid_tld', False)
                        row.is_spam = email_data.get('results', {}).get('is_spam', False)
                        row.feee_domain = email_data.get('results', {}).get('free_domain', False)
                    except Exception as e:
                        logger.error(f"Error processing row {row.id}: {str(e)}")
                        row.email_format = False
                        row.domain_exists = False
                        row.mx_record = False
                row.is_processed = True
                # row.save()
            with ThreadPoolExecutor(max_workers=7) as executor:
                executor.map(ProcessEmail, objects_list)
            # print(f"{objects_list}====================>")
            CsvFileDataEmail.objects.bulk_update(
                objects_list,
                [
                    'is_processed', 'email_format', 'mx_record', 'domain_exists',
                    'disposable_email', 'role_account', 'common_typo', 'spf_record',
                    'dkim_record', 'dmarc_record', 'new_domain', 'valid_tld',
                    'is_spam', 'feee_domain'
                ]
            )
            logger.info(f"Updated processed rows in DB: {csvfile.processed_rows}")

    except Exception as e:
        logger.error(f"Error during CSV processing: {str(e)}")
        raise

    csvfile.is_complete = True
    csvfile.completed_at = timezone.now()  # Set completion time on success
    csvfile.duration = csvfile.completed_at - csvfile.uploaded_at  # Calculate duration
    csvfile.save()

    # Additional steps
    try:
        # fixNumberTypesData_V2_count = fixNumberTypesData_V2(file_uid)
        # UpdateCSVDetailInfo_res = UpdateCSVDetailInfo(file_uid)
        updateProcessedRowsRecords = updateEmailProcessedRows(file_uid)

        saveCsvFileDataToCSV_res = saveCsvFileEmailDataToCSV(file_uid)

        if up.email_notifications:
            email_SendAfterCSVSuccessfull_res = email_SendAfterCSVSuccessfull(email, filename, download_file_url,
                                                                          allow_cc=False)
        # handleReversedCredits_v3_res = handleReversedCredits_v3(file_uid)

        # try:
        #     celery_loadCSVFileEmailDatatoUserDataLogs_vN.delay(file_uid)
        # except Exception as e:
        #     logger.error(f"Error queuing CSV data logs task: {str(e)}")

        logs = {
            'file_uid': file_uid,
            # 'fixNumberTypesData_V2': fixNumberTypesData_V2_count,
            # 'UpdateCSVDetailInfo': UpdateCSVDetailInfo_res,
            'updateProcessedRowsRecords': updateProcessedRowsRecords,
            'saveCsvFileDataToCSV_res': saveCsvFileDataToCSV_res,
            #'email_SendAfterCSVSuccessfull': email_SendAfterCSVSuccessfull_res,
            # 'handleReversedCredits_v3': handleReversedCredits_v3_res,
        }

        if up.email_notifications:
            logs['email_SendAfterCSVSuccessfull'] = email_SendAfterCSVSuccessfull_res

        if device_tokens:
            for token in device_tokens:
                send_push_notification(
                    token=token,
                    title="File processed successfully",
                    body=f"Your file '{csvfile.csvfile_name}' has finished processing.",
                    notification_type="csv_email_file",
                    file_id=csvfile.uid
                )

        return logs
    except Exception as e:
        logger.error(f"Error completing the CSV process: {str(e)}")
        raise


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True, retry_kwargs={'max_retries':5})
def celery_HandleBulkAPI(self, apibulk_resultid):
    if self.request.retries >= self.max_retries:
        try:
            apibulk_obj = APIBULK.objects.get(uid=apibulk_resultid)
            apibulk_obj.status = APIBULK.APICALL_STATUS.FAILED 
            apibulk_obj.is_charged = False
            apibulk_obj.total_rows_charged = 0
            apibulk_obj.save()
            up = UserProfile.objects.get(user=apibulk_obj.user)
            up.credits = F('credits') + apibulk_obj.total_rows_charged
            up.save()
            APIData.objects.filter(apibulk=apibulk_obj).delete()
        except:
            pass 
        return None
    
    try:
        records = APIData.objects.filter(apibulk__uid=apibulk_resultid).order_by('-id') #.filter(line_type__isnull=True)
        input_numbers_list = [str(ob.phonenumber).strip() for ob in records]

        dnc_datas = handleDNCBULKAPI_v3(input_numbers_list) 

        paginator = Paginator(records, 500)
        for page in range(1, paginator.num_pages+1):
            new_objs = []
            objects_list = paginator.page(page).object_list

            def GetTypeData(row):
                clean_phone = row.phonenumber
                phone_data = returnNumberData_v3(clean_phone, shuffle=False)
                logger.info(f"API NUMBERS {phone_data} ------------------------- ")
                line_type = phone_data.get('line_type', 'invalid')

                if line_type == 'invalid':
                    row.line_type = 'invalid'
                    row.dnc_type = 'invalid'
                    row.number_checked_from_db = phone_data.get('found_from_db',False)
                else:
                    row.line_type = line_type
                    row.dnc_type = dnc_datas[clean_phone]
                    row.carrier_name = phone_data.get('carrier_name', 'n/a')
                    row.city = phone_data.get('city', 'n/a')
                    row.state = phone_data.get('state', 'n/a')
                    row.country = phone_data.get('country', 'n/a')
                    row.number_checked_from_db = phone_data.get('found_from_db',False)
                new_objs.append(row)

            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(GetTypeData, objects_list)

            APIData.objects.bulk_update(new_objs, ['line_type','dnc_type', 'carrier_name', 'city', 'state', 'country','number_checked_from_db'])

    except:
        raise Exception()


    # fix the records if there is any missing data found
    api_fixNumberTypesData(apibulk_resultid)


    # update the api detail info
    try:
        UpdateBulkAPIDetailInfo(apibulk_resultid)
    except:
        pass
    
    try:
        util_handleCreditsAnalyticsBulkApi(apibulk_resultid)
    except:
        pass
    

    
    cache.delete(f'celery_task_{apibulk_resultid}')
    APIBULK.objects.filter(uid=apibulk_resultid).update(status=APIBULK.APICALL_STATUS.COMPLETED)



#new method mar 2024
@shared_task 
def celery_autoClean_RawCsvFiles():
    autoClean_RawCsvFiles()
    return None


#new method mar 2024
@shared_task 
def celery_autoClean_CsvFileData():
    autoClean_CsvFileData()
    return None


#new method mar 2024
@shared_task 
def celery_autoClean_InvalidNumberDataLogs():
    autoClean_InvalidNumberDataLogs()
    return None


#new method mar 2024
@shared_task 
def celery_autoClean_DNCDataLogs():
    autoClean_DNCDataLogs()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_TelynxDataLogs():
    autoClean_TelynxDataLogs()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_SignalwireDataLogs():
    autoClean_SignalwireDataLogs()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_NetNumberingDataLogs():
    autoClean_NetNumberingDataLogs()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_APIData():
    autoClean_APIData()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_UserDataLogs():
    autoClean_UserDataLogs()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_CeleryTaskResults():
    autoClean_CeleryTaskResults()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_CustomSiteLogs():
    autoClean_CustomSiteLogs()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_LogFile():
    autoClean_LogFile()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_CeleryLogFile():
    autoClean_CeleryLogFile()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_CeleryBeatLogFile():
    autoClean_CeleryBeatLogFile()
    return None

#new method mar 2024
@shared_task 
def celery_autoClean_MediaFiles():
    autoClean_MediaFiles()
    return None

@shared_task 
def celery_autoRenew_subscriptions_Credits():
    renew_subscriptions_credits()
    return None

@shared_task
def celery_autoRenew_Custom_subscriptions_Credits():
    renew_custom_subscriptions_credits()
    return None

@shared_task
def celery_autoCancel_custom_subscriptions():
    cancel_custom_subscriptions()
    return None




@shared_task
def celery_handleAutoTestServiceStatus(**kwargs):
    try:
        res_ = handleLeadsFileDistirbution_Bucket(kwargs['leadfile_uid'])
        return str(res_)
    except Exception as e:
        lead_file_obj = LeadsFile.objects.get(uid=kwargs['leadfile_uid'])
        lead_file_obj.under_use = True
        lead_file_obj.save()
        return f"Failed Exception Occured: {e}"






@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True,
             retry_kwargs={'max_retries': 5})
def celery_HandleUpload_Data_Enrichment(self, data, use_split=False):
    file_uid = data['file_uid']
    email = data['email']
    filename = data['filename']
    download_file_url = data['download_file_url']
    up = UserProfile.objects.get(user=UserModel.objects.get(email=email))

    # added on 09/09/2024
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
    except CsvFile.DoesNotExist:
        logger.error(f"CSV file with UID {file_uid} not found.")
        return None

    if self.request.retries >= self.max_retries:
        csvfile.is_failed = True
        csvfile.completed_at = timezone.now()
        csvfile.duration = csvfile.completed_at - csvfile.uploaded_at
        csvfile.save()

        try:
            logs = {}

            csvfile = CsvFile.objects.get(uid=file_uid)
            csvfile.is_failed = True
            csvfile.save()

            try:
                up = UserProfile.objects.get(user=UserModel.objects.get(email=email))
                logs['credits_before_failed'] = up.endato_credits
                up.endato_credits = F('endato_credits') + csvfile.total_rows_charged
                up.save()
                if up.email_notifications:
                    email_SendAfterCSVFailed_res = email_SendAfterCSVFailed(email, filename, allow_cc=False)

                try:
                    celery_handleFailedFile.delay(file_uid)
                except Exception as e:
                    logger.error(f"Error queuing failed file task: {str(e)}")

                logs['credits_after_failed'] = up.endato_credits
                logs['total_rows_charged'] = csvfile.total_rows_charged
                if up.email_notifications:
                    logs['email_SendAfterCSVFailed'] = email_SendAfterCSVFailed_res

                return logs
            except UserProfile.DoesNotExist:
                logger.error(f"UserProfile for email {email} not found.")
        except Exception as e:
            logger.error(f"Error processing failure: {str(e)}")
        return None

    if self.request.retries < 1:
        try:
            UploadendatoCSVDATA(file_uid)
        except Exception as e:
            logger.error(f"Error uploading CSV data for {file_uid}: {str(e)}")
            raise

    
    check_in_endato = CheckEndatoApi.objects.filter(csvfile=csvfile,check_with_endato=True).first()
    if check_in_endato:
            check_in_endato.status = CheckEndatoApi.RequestStatus.PROCESSING
            check_in_endato.save()
            # try:
            #     UploadCSVFirstLastName(file_uid)
            # except Exception as e:
            #     error_details = traceback.format_exc()
            #     logger.error(f"Error uploading CSV data for {file_uid}: {error_details}")
            #     raise

            try:
                records = EndatoCsvFileData.objects.filter(csvfile__uid=file_uid).order_by('id')  
                paginator = Paginator(records, 900)
                for page in range(1, paginator.num_pages + 1):
                    new_objs_two = []
                    objects_list = paginator.page(page).object_list

                    def GetTypeData(row):
                        clean_phone = row.phonenumber
                        if clean_phone == 'invalid_data':
                            row.is_processed_through_endato = True
                            row.data_enrichment_checked_from_db = False
                            row.endato_invalid_flag = True
                        else:
                            apidata = returnNumberData_v6(row.phonenumber)
                            try:
                                if apidata.get('first_name') == 'n/a' and apidata.get('last_name') == 'n/a' and apidata.get('age') == 'n/a' and apidata.get('addresses') == 'n/a' and apidata.get('phones') == 'n/a' and apidata.get('emails')  == 'n/a':
                                    row.endato_invalid_flag = True   
                                    row.is_processed_through_endato = True  
                                    row.data_enrichment_checked_from_db = apidata.get('found_in_db',False)
                                else:   
                                    row.first_name = apidata.get('first_name')
                                    row.last_name = apidata.get('last_name')
                                    row.age = apidata.get('age')
                                    row.addresses = apidata.get('addresses')
                                    row.phones = apidata.get('phones')
                                    row.emails = apidata.get('emails')
                                    # row.identityScore = apidata.get('identityScore')
                                    row.is_processed_through_endato = True
                                    row.data_enrichment_checked_from_db = apidata.get('found_in_db',False)
                            except Exception as e:
                                logger.info(f'ERROR UPATING ROW {e}')    
                    
                        new_objs_two.append(row)
                                
                        
                    with ThreadPoolExecutor(max_workers=7) as executor:
                        executor.map(GetTypeData, objects_list)
                    
                    logger.info(f"{new_objs_two} NEW OBJECT DATA ")
                    EndatoCsvFileData.objects.bulk_update(new_objs_two,
                                            ['first_name', 'last_name', 'age', 'addresses', 'phones', 'emails','endato_invalid_flag','is_processed_through_endato','data_enrichment_checked_from_db'])
                    
                check_in_endato.status = CheckEndatoApi.RequestStatus.COMPLETED
                check_in_endato.save()

            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Error handling pagination for {file_uid}: {error_details}")
                raise


    csvfile.is_complete = True
    csvfile.completed_at = timezone.now()  
    csvfile.duration = csvfile.completed_at - csvfile.uploaded_at  
    csvfile.save()

    try:
        updateProcessedRowsRecords = updateProcessedRowsv2(file_uid)
    
        endato_saveCsvFileDataToCSV = endatosaveCsvFileDataToCSV(file_uid,True,False)
        
        if up.email_notifications:
            email_SendAfterCSVSuccessfull_res = email_SendAfterCSVSuccessfull(email, filename, download_file_url,
                                                                          allow_cc=False)
        if check_in_endato:
            DjModel = EndatoCsvFileData
            handleReverseCredits_endato_checks = endatoHandleReversedCredits_v1(DjModel,file_uid)
        else:
            handleReverseCredits_endato_checks = ""

        try:
            if check_in_endato:
                DjModel = "EndatoCsvFileData"
                celery_loadCSVFileDatatoUserDataLogsEndato_vN.delay(file_uid,DjModel)
        except Exception as e:
            logger.error(f"Error queuing CSV data logs task: {str(e)}")

        logs = {
            'file_uid': file_uid,
            'endato_saveCsvFileDataToCSV':endato_saveCsvFileDataToCSV,
            #'email_SendAfterCSVSuccessfull': email_SendAfterCSVSuccessfull_res,
            'handleReverseCredits_endato_checks':handleReverseCredits_endato_checks,
            "updateProcessedRowsRecords":updateProcessedRowsRecords
        }

        if up.email_notifications:
            logs['email_SendAfterCSVSuccessfull'] = email_SendAfterCSVSuccessfull_res

        return logs
    except Exception as e:
        logger.error(f"Error completing the CSV process: {str(e)}")
        raise








@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True, retry_kwargs={'max_retries': 5})
def celery_HandleEndatoBulkAPI(self, apibulk_resultid):
    logger.info(f"Processing bulk job: {apibulk_resultid}")
    try:
        with transaction.atomic():
            apibulk_obj = EndatoBULK.objects.select_for_update().get(uid=apibulk_resultid)
            apibulk_obj.status = EndatoBULK.ENDATOCALL_STATUS.PROCESSING
            apibulk_obj.save()

            records = EndatoApiResponse.objects.filter(apibulk=apibulk_obj)
            input_data_list = [
                {
                    # "FirstName": record.first_name,
                    # "LastName": record.last_name,
                    "Phone": record.phone_number
                }
                for record in records
            ]

            enriched_data = getBulkEnrichedData(input_data_list)
            logger.info(f"Enriched Data: {enriched_data}")

            for record, enriched_item in zip(records, enriched_data):
                record.response_dict = enriched_item

            EndatoApiResponse.objects.bulk_update(records, fields=['response_dict'])

            apibulk_obj.status = EndatoBULK.ENDATOCALL_STATUS.COMPLETED
            apibulk_obj.is_charged = True
            apibulk_obj.total_rows_charged = len(enriched_data)
            apibulk_obj.save()

            user_profile = UserProfile.objects.get(user=apibulk_obj.user)
            user_profile.endato_credits -= len(enriched_data)
            user_profile.save()

    except Exception as e:
        logger.error(f"Error processing bulk job {apibulk_resultid}: {e}")
        if apibulk_obj.is_charged:
            logger.info(f"Reversing credits for failed job {apibulk_resultid}")
            apibulk_obj.status = EndatoBULK.ENDATOCALL_STATUS.FAILED
            apibulk_obj.save()

            user_profile = UserProfile.objects.get(user=apibulk_obj.user)
            user_profile.endato_credits = F('endato_credits') + apibulk_obj.total_rows_charged
            user_profile.save()

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        else:
            logger.error(f"Max retries reached for bulk job {apibulk_resultid}.")



@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True, retry_kwargs={'max_retries': 5})
def celery_HandleTextdrip_Bulk_Number_Api(self, phone_numbers):
    try:
        valid_numbers = [num for num in phone_numbers if returnCleanPhone_Or_None(num)]
        valid_numbers_unique = list(set(valid_numbers))

        matched_records, cleaned_records = API_DNCTCPA_SPLIT().GetSmallList(valid_numbers_unique)
        dnc_api_records = {**matched_records, **cleaned_records}

        def GetTypeData(number):
            clean_number = returnCleanPhone_Or_None(number)
            if clean_number is None:
                return {
                    'Number': number,
                    'Status': False,
                    'LineType': 'n/a',
                    'DNCType': 'n/a',
                    'CarrierName': 'n/a',
                    'City': 'n/a',
                    'State': 'n/a',
                    'Country': 'n/a',
                }
            phone_data = returnNumberData_v5(clean_number)
            dnc_type = format_dnctype(dnc_api_records.get(clean_number, 'n/a'))
            return {
                'Number': clean_number,
                'Status': True,
                'LineType': phone_data.get('line_type', 'invalid'),
                'DNCType': dnc_type,
                'CarrierName': returnCleanCarrierName(phone_data.get('carrier_name', 'n/a')),
                'City': phone_data.get('city', 'n/a'),
                'State': phone_data.get('state', 'n/a'),
                'Country': phone_data.get('country', 'n/a'),
            }

        with ThreadPoolExecutor(max_workers=20) as executor:
            final_data = list(executor.map(GetTypeData, phone_numbers))

        return {"status": "success", "data": final_data}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def reset_daily_analytics():
    today = now().date()
    DataEnrichmentDataLogsDailyAnalytics.objects.filter(timestamp__date=today).update(total_records=0)



    
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_jitter=True, retry_kwargs={'max_retries': 5})
def celery_HandlePersonSearchBulkAPI(self, apibulk_resultid):
            apibulk_obj = EndatoBULK.objects.get(uid=apibulk_resultid)
            apibulk_obj.status = EndatoBULK.ENDATOCALL_STATUS.PROCESSING
            apibulk_obj.save()
           
            try:
                records = EndatoApiResponse.objects.filter(apibulk=apibulk_obj).order_by('id') 
                paginator = Paginator(records, 900)
                for page in range(1, paginator.num_pages + 1):
                    new_objs_two = []
                    objects_list = paginator.page(page).object_list

                    def GetTypeData(row):
                        apidata = returnNumberData_v6(row.phone_number)
                        
                        try:
                            if apidata.get('first_name') == 'n/a' and apidata.get('last_name') == 'n/a' and apidata.get('age') == 'n/a' and apidata.get('addresses') == 'n/a' and apidata.get('phones') == 'n/a' and apidata.get('emails')  == 'n/a':
                                row.endato_invalid_flag = True   
                                row.is_processed_through_endato = True  
                                row.data_enrichment_checked_from_db = apidata.get('found_in_db',False)
                            else:   
                                row.first_name = apidata.get('first_name')
                                row.last_name = apidata.get('last_name')
                                row.age = apidata.get('age')
                                row.addresses = apidata.get('addresses')
                                row.phones = apidata.get('phones')
                                row.emails = apidata.get('emails')
                                # row.identityScore = apidata.get('identityScore')
                                row.is_processed_through_endato = True
                                row.data_enrichment_checked_from_db =  apidata.get('found_in_db',False)
                        except Exception as e:
                            logger.info(f'ERROR UPATING ROW {e}')    
                
                        new_objs_two.append(row)
                            
                        
                    with ThreadPoolExecutor(max_workers=7) as executor:
                        executor.map(GetTypeData, objects_list)
                    
                    logger.info(f"{new_objs_two} NEW OBJECT DATA ")
                    EndatoApiResponse.objects.bulk_update(new_objs_two,
                                            ['first_name', 'last_name', 'age', 'addresses', 'phones', 'emails','endato_invalid_flag','is_processed_through_endato','data_enrichment_checked_from_db'])
                    
                
            except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"Error handling pagination for {apibulk_resultid}: {error_details}")
                raise


            apibulk_obj = EndatoBULK.objects.get(uid=apibulk_resultid)
            apibulk_obj.status = EndatoBULK.ENDATOCALL_STATUS.COMPLETED
            apibulk_obj.save()

@shared_task
def celery_autoclean_testusers():
    autoClean_testusers()
    return None

@shared_task
def celery_auto_change_team_token():
    refresh_team_tokens()
    return None

@shared_task
def celery_auto_renewal_ssl():
    ssl_expiry_alerts()
    return None


# @shared_task
# def test_progress_celery(user_id):
#     try:
#         print("---- test progress celery is called ----")
#         for i in range(0, 101, 5):
#             send_progress(1, '9989-55dsfsd-fsd5fd2g-dfg5df', i)
#             time.sleep(1)  # simulate work
#         return {"status": "done"}
#     except Exception as e:
#         print("Exception as e ----", e)
#
# def get_progress_info_for_file(instance):
#
#     try:
#         total_rows = max(int(instance.total_rows or 0), 1)  # Avoid division by zero
#         processed_rows = CsvFileData.objects.filter(csvfile=instance, is_processed=True).count()
#         endato_processed_rows = 0
#         progress = 0
#         file_type = "Number Lookup"
#
#         # Check for Endato usage (Data Enrichment)
#         if CheckEndatoApi.objects.filter(csvfile=instance).exists():
#             endato_check = CheckEndatoApi.objects.get(csvfile=instance)
#             if endato_check.check_with_endato:
#                 if endato_check.check_with_endato_only:
#                     file_type = "Data Enrichment Only"
#                     endato_processed_rows = EndatoCsvFileData.objects.filter(
#                         csvfile=instance, is_processed_through_endato=True
#                     ).count()
#                 else:
#                     file_type = "Both"
#                     endato_processed_rows = CsvFileData.objects.filter(
#                         csvfile=instance,
#                         is_processed=True,
#                         is_processed_through_endato=True
#                     ).count()
#                 progress = min(round((endato_processed_rows / total_rows) * 100, 2), 100) if total_rows > 0 else 0
#             else:
#                 progress = min(round((processed_rows / total_rows) * 100, 2), 100) if total_rows > 0 else 0
#         else:
#             progress = min(round((processed_rows / total_rows) * 100, 2), 100) if total_rows > 0 else 0
#
#         # Check for Wavix usage (Number Lookup)
#         if WavixRequestTracker.objects.filter(csvfile=instance).exists() and not endato_processed_rows:
#             file_type = "Number Lookup"
#             progress = min(round((processed_rows / total_rows) * 100, 2), 100) if total_rows > 0 else 0
#
#         # Override if complete
#         if instance.is_complete:
#             progress = 100
#             processed_rows = total_rows
#             endato_processed_rows = total_rows if endato_processed_rows else 0
#
#         progress_info = {
#             'progress': progress,
#             'processed_rows': processed_rows,
#             'total_rows': total_rows,
#             'endato_processed_rows': endato_processed_rows,
#             'is_complete': instance.is_complete,
#             'status': 'Complete' if instance.is_complete else 'Processing',
#             'file_type': file_type
#         }
#
#         return progress_info
#     except Exception as e:
#         return {
#             'progress': 0,
#             'processed_rows': 0,
#             'total_rows': 0,
#             'endato_processed_rows': 0,
#             'is_complete': False,
#             'status': 'Error',
#             'error': str(e)
#         }
#
# @shared_task
# def send_file_progress_updates(user_id):
#
#     try:
#         print(f"---- Sending progress updates for user {user_id} ----")
#
#         # Get all processing files for this user
#         processing_files = CsvFile.objects.filter(
#             user_id=user_id,
#             is_charged=True,
#             is_complete=False,  # Only files that are still processing
#             is_failed=False,
#             is_canceled=False
#
#         )
#
#         if not processing_files.exists():
#             print("No processing files found for user")
#             return {"status": "no_files"}
#
#         # Continue sending updates until all files are complete
#         while processing_files.exists():
#             for file_instance in processing_files:
#                 # Get current progress for this file
#                 progress_info = get_progress_info_for_file(file_instance)
#
#                 # Send progress update via WebSocket
#                 send_progress(
#                     user_id,
#                     str(file_instance.uid),
#                     progress_info['progress']
#                 )
#
#                 print(f"Sent progress for file {file_instance.uid}: {progress_info['progress']}%")
#
#             # Wait before next update
#             time.sleep(3)
#
#             # Refresh the list of processing files
#             processing_files = CsvFile.objects.filter(
#                 user_id=user_id,
#                 is_charged=True,
#                 is_complete=False,
#                 is_failed=False,
#                 is_canceled=False
#             )
#
#         print("All files completed processing")
#         return {"status": "completed"}
#
#     except Exception as e:
#         print(f"Exception in send_file_progress_updates: {e}")
#         return {"status": "error", "message": str(e)}
