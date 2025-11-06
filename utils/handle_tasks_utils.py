import logging

from django.core.paginator import Paginator
from django.db.models import F
from django.conf import settings
from django.core.mail import send_mail
from utils.logs import user_bulk_upload_activity, user_bulk_upload_activity_with_subscription, \
    exhaust_subscription_credit_log
from adminv2.models import UserActivityLog
from utils.aws_client import get_s3_client

from functools import reduce
from itertools import chain
import io
from django.http import HttpResponse

import pandas as pd 
import os 
from django.db.models import Q

from django.contrib.auth import get_user_model
UserModel = get_user_model()

#custom imports
from api.models import APIBULK, APIData
from core.models import CsvFileData, CsvFile, EndatoApiResponse, EndatoCsvFileData, CreditAnalytics, \
    TestUserCreditAnalytics, CheckEndatoApi
from mdrdata.models import DNCNumberData
from dashboard.models import UserProfile
# from datastorage.models import WavixRequestTracker
# from utils.handle_wavix_bulk_api import validate_phone_numbers
from utils.handle_dnctcpa_split import API_DNCTCPA_SPLIT
from utils.utils import returnCleanDNCType
from utils.is_number_inmodels import isNumberFoundInModels, isDncNumberFound, returnPhoneRequiredData
from utils._base import (
    required_data_fields_list, 
    required_data_fields_list_full, 
    csv_output_columns, 
    required_data_fields_list_no_phone,
    required_data_fields_list_full_two,
    endato_required_data_fields_list_full,
    endato_csv_output_columns,
    csvemaildata_model_required_fields, csv_output_email_columns,
    csv_output_columns_two,
    
    returnCleanCarrierName,
)

from utils.handle_number_info import returnNumberData_v3, returnNumberDncData_v3, handleUserDataLogsLookup_v3,endatoHandleUserDataLogsLookup_v3,returnNumberData_v5, handleUserDataLogsLookup_Email_v3
from django.core.files.storage import default_storage
import boto3
import pandas as pd
import boto3
from io import StringIO
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


def handleReversedCredits_v3(bulkfile_uid = None,checkprrows=False):
    try:
        csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
        if csvfile_obj.is_complete or checkprrows:
            current_user = csvfile_obj.user 
            credits_to_return = util_handleReversedCredits_v3(bulkfile_uid,checkprrows)
            csvfile_obj.total_rows_duplicates = credits_to_return
            csvfile_obj.save()
            up = UserProfile.objects.get(user=current_user)
            
            # Store old values for logging
            old_credits = up.credits
            old_subscriptions_credits = up.subscriptions_credits_number_checks
            old_subscriptions_offer_credits = up.subscriptions_offer_credits_number_checks
            
            # Store original credits_to_return for logging (will be modified in loop)
            total_credits_returned = credits_to_return

            # Determine which credit pool to refund based on what was originally deducted (3-tier reversal)
            # We need to reverse credits in the SAME order they were deducted
            
            # Priority 1: If subscription offer credits were used, refund to subscription offer credits
            if csvfile_obj.credits_deducted_from_subscription_offer > 0 and credits_to_return > 0:
                credits_to_refund_offer = min(credits_to_return, csvfile_obj.credits_deducted_from_subscription_offer)
                up.subscriptions_offer_credits_number_checks = F("subscriptions_offer_credits_number_checks") + credits_to_refund_offer
                credits_to_return -= credits_to_refund_offer
            
            # Priority 2: If subscription credits were used and credits still remain, refund to subscription credits
            if credits_to_return > 0 and csvfile_obj.credits_deducted_from_subscription > 0:
                credits_to_refund_subscription = min(credits_to_return, csvfile_obj.credits_deducted_from_subscription)
                up.subscriptions_credits_number_checks = F("subscriptions_credits_number_checks") + credits_to_refund_subscription
                credits_to_return -= credits_to_refund_subscription
            
            # Priority 3: If regular credits were used and credits still remain, refund to regular credits
            if credits_to_return > 0:
                up.credits = F('credits') + credits_to_return
                
            up.save()
            up.refresh_from_db()

            description = f"{total_credits_returned} Credits After Duplicates for csv file {csvfile_obj.csvfile_name} " if total_credits_returned > 0 else f"Credits After Duplicates for {csvfile_obj.csvfile_name}"

            try:
                # user_bulk_upload_activity(
                #     user=current_user,
                #     description=description,
                #     actions=UserActivityLog.ActionType.BULKUPLOAD,
                #     amount=0,
                #     prev_credits=old_credits,
                #     remaining_credits=up.credits,
                #     earned_credits=0
                # )

                user_bulk_upload_activity_with_subscription(
                    user=current_user,
                    description=description,
                    actions=UserActivityLog.ActionType.BULKUPLOAD,
                    prev_credits=old_credits,
                    remaining_credits=up.credits,
                    subscription_prev_credits=old_subscriptions_credits,
                    subscription_remaining_credits=up.subscriptions_credits_number_checks,
                    subscription_offer_prev_credits=old_subscriptions_offer_credits,
                    subscription_offer_remaining_credits=up.subscriptions_offer_credits_number_checks,
                )

            except Exception as e:
                print(f'ERROR CREATING LOGS FOR REVERSE CREDITS: {e}')

            try:
                if csvfile_obj.credits_deducted_from_subscription > 0 and up.subscriptions_credits_number_checks == 0:
                    exhaust_subscription_credit_log(
                        user=current_user,
                        actions=UserActivityLog.ActionType.BULKUPLOAD,
                        description=f"You have exhausted your subscription credits after performing a bulk upload for the CSV file '{csvfile_obj.csvfile_name}'. Credits will be renewed upon subscription renewal."
                    )
            except Exception as e:
                print(f'ERROR CREATING LOGS FOR EXHAUST SUBSCRIPTION CREDITS: {e}')
            
            return credits_to_return 
    except:
        pass
    return None


from api.models import CsvFileEmail, CsvFileDataEmail


def util_handleReversedCredits_Email_v3(bulkfile_uid=None, checkprrows=False):
    csvfile_obj = CsvFileEmail.objects.get(uid=bulkfile_uid)
    current_user = csvfile_obj.user

    if checkprrows:
        csvfile_emails_list = list(
            CsvFileDataEmail.objects.exclude(email='invalid_data')
            .filter(csvfile=csvfile_obj, is_processed=True)
            .values_list('email', flat=True)
            .order_by('email')
            .distinct('email')
        )
    else:
        csvfile_emails_list = list(
            CsvFileDataEmail.objects.exclude(email='invalid_data')
            .filter(csvfile=csvfile_obj)
            .values_list('email', flat=True)
            .order_by('email')
            .distinct('email')
        )

    paginator = Paginator(csvfile_emails_list, 1000)
    for page in range(1, paginator.num_pages + 1):
        emails_list = paginator.page(page).object_list
        userdatalogs_emails_list = handleUserDataLogsLookup_Email_v3(current_user, emails_list, csvfile_obj.uploaded_at)
        csvfile_emails_list = list(set(csvfile_emails_list) - set(userdatalogs_emails_list))

    paginator = Paginator(csvfile_emails_list, 1000)
    for page in range(1, paginator.num_pages + 1):
        emails_list = paginator.page(page).object_list
        api_qs_list = APIData.objects.filter(
            userprofile=current_user.profile, email__in=emails_list, timestamp__lt=csvfile_obj.uploaded_at
        ).values_list('email', flat=True)
        csvfile_emails_list = list(set(csvfile_emails_list) - set(api_qs_list))

    return csvfile_obj.total_rows_charged - len(csvfile_emails_list)


def handleReversedCreditsEmail_v3(bulkfile_uid = None,checkprrows=False):
    try:
        csvfile_obj = CsvFileEmail.objects.get(uid=bulkfile_uid)
        if csvfile_obj.is_complete or checkprrows:
            current_user = csvfile_obj.user
            credits_to_return = util_handleReversedCredits_Email_v3(bulkfile_uid,checkprrows)
            # csvfile_obj.total_rows_duplicates = credits_to_return
            csvfile_obj.save()
            up = UserProfile.objects.get(user=current_user)
            up.credits = F('credits') + credits_to_return
            up.save()
            return credits_to_return
    except:
        pass
    return None



def util_handleReversedCredits_Email_v3(bulkfile_uid=None, checkprrows=False):
    csvfile_obj = CsvFileEmail.objects.get(uid=bulkfile_uid)
    current_user = csvfile_obj.user

    if checkprrows:
        csvfile_emails_list = list(
            CsvFileDataEmail.objects.exclude(email='invalid_data')
            .filter(csvfile=csvfile_obj, is_processed=True)
            .values_list('email', flat=True)
            .order_by('email')
            .distinct('email')
        )
    else:
        csvfile_emails_list = list(
            CsvFileDataEmail.objects.exclude(email='invalid_data')
            .filter(csvfile=csvfile_obj)
            .values_list('email', flat=True)
            .order_by('email')
            .distinct('email')
        )

    paginator = Paginator(csvfile_emails_list, 1000)
    for page in range(1, paginator.num_pages + 1):
        emails_list = paginator.page(page).object_list
        userdatalogs_emails_list = handleUserDataLogsLookup_Email_v3(current_user, emails_list, csvfile_obj.uploaded_at)
        csvfile_emails_list = list(set(csvfile_emails_list) - set(userdatalogs_emails_list))

    paginator = Paginator(csvfile_emails_list, 1000)
    for page in range(1, paginator.num_pages + 1):
        emails_list = paginator.page(page).object_list
        api_qs_list = APIData.objects.filter(
            userprofile=current_user.profile, email__in=emails_list, timestamp__lt=csvfile_obj.uploaded_at
        ).values_list('email', flat=True)
        csvfile_emails_list = list(set(csvfile_emails_list) - set(api_qs_list))

    return csvfile_obj.total_rows_charged - len(csvfile_emails_list)



def util_handleReversedCredits_v3(bulkfile_uid = None,checkprrows=False):
    csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
    current_user = csvfile_obj.user 
    if checkprrows:
        csvfile_numbers_list = list(CsvFileData.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj,is_processed=True).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))
    else:
        csvfile_numbers_list = list(CsvFileData.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))

    paginator = Paginator(csvfile_numbers_list, 1000)
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        userdatalogs_numbers_list = handleUserDataLogsLookup_v3(current_user, numbers_list, csvfile_obj.uploaded_at)
        csvfile_numbers_list = list(set(csvfile_numbers_list) - set(userdatalogs_numbers_list))

    paginator = Paginator(csvfile_numbers_list, 1000)
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        api_qs_list = APIData.objects.filter(userprofile=current_user.profile, phonenumber__in=numbers_list, timestamp__lt=csvfile_obj.uploaded_at).values_list('phonenumber', flat=True)
        #api_qs_list = list(set(api_qs_list))
        csvfile_numbers_list = list(set(csvfile_numbers_list) - set(api_qs_list))

    return csvfile_obj.total_rows_charged - len(csvfile_numbers_list) 



def util_update_duplicate_rows_in_db(bulkfile_uid = None,checkprrows=False):
    csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
    current_user = csvfile_obj.user 
    if checkprrows:
        csvfile_numbers_list = list(CsvFileData.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj,is_processed=True).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))
    else:
        csvfile_numbers_list = list(CsvFileData.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))

    paginator = Paginator(csvfile_numbers_list, 1000)
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        userdatalogs_numbers_list = handleUserDataLogsLookup_v3(current_user, numbers_list, csvfile_obj.uploaded_at)
        duplicates = list(set(numbers_list) & set(userdatalogs_numbers_list))
        
        CsvFileData.objects.filter(phonenumber__in=duplicates, csvfile=csvfile_obj).update(is_duplicate=True)

    paginator = Paginator(csvfile_numbers_list, 1000)
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        api_qs_list = APIData.objects.filter(userprofile=current_user.profile, phonenumber__in=numbers_list, timestamp__lt=csvfile_obj.uploaded_at).values_list('phonenumber', flat=True)
        #api_qs_list = list(set(api_qs_list))
        duplicates = list(set(numbers_list) & set(api_qs_list))
        CsvFileData.objects.filter(phonenumber__in=duplicates, csvfile=csvfile_obj).update(is_duplicate=True)

    return None



# no in use - modified to v3
def handleReversedCredits_v2(bulkfile_uid = None):
    credits_to_return = 0

    csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
    current_user = csvfile_obj.user 

    number_list = list(CsvFileData.objects.filter(csvfile=csvfile_obj).values_list('phonenumber', flat=True))

    numbers_dict = {i:number_list.count(i) for i in number_list}
    credits_to_return += numbers_dict.get('invalid_data', 0)

    duplicate_count_in = [value for value in numbers_dict.values() if value > 1]
    credits_to_return += sum(_-1 for _ in duplicate_count_in)

    number_list = list(set([_ for _ in number_list if _!='invalid_data']))

    paginator = Paginator(number_list, 1000) 
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        userdatalogs_numbers_list = handleUserDataLogsLookup_v3(current_user, numbers_list)
        apidata_numbers_list = list(APIData.objects.filter(userprofile=current_user.profile, phonenumber__in=numbers_list).values_list('phonenumber', flat=True))
        apidata_numbers_list = list(set(apidata_numbers_list))
        merge_db_list = list(set(chain(userdatalogs_numbers_list, apidata_numbers_list)))
        credits_to_return += len(merge_db_list) #sum(f in merge_db_list for f in numbers_list)
    
    csvfile_obj.total_rows_duplicates = credits_to_return
    csvfile_obj.save()
    up = UserProfile.objects.get(user=current_user)
    up.credits = F('credits') + credits_to_return
    up.save()

    return None
    
#build in august 23
def fixNumberRowData_util(row):
    try:
        clean_phone = row.phonenumber
        phone_data = returnNumberData_v5(clean_phone, shuffle=False)
        line_type = phone_data.get('line_type', 'invalid')
        if line_type == 'invalid':
            row.line_type = 'invalid'
            row.dnc_type = 'invalid'
        else:
            row.line_type = line_type
            row.dnc_type = returnNumberDncData_v3(clean_phone)
            row.carrier_name = phone_data.get('carrier_name', 'n/a')
            row.city = phone_data.get('city', 'n/a')
            row.state = phone_data.get('state', 'n/a')
            row.country = phone_data.get('country', 'n/a')
        return row 
    except: 
        return None


#new method - used in celery task - celery_HandleUpload
def fixNumberTypesData_V2(file_uid,checkprrows=False):
    fix_objects = []
    
    if checkprrows:
        datas = CsvFileData.objects.exclude(phonenumber='invalid').filter(
            csvfile__uid=file_uid,
            is_processed=True
        ).filter(
            Q(line_type__isnull=True) | Q(line_type='')
        )
    else:
        datas = CsvFileData.objects.exclude(phonenumber='invalid').filter(
            csvfile__uid=file_uid
        ).filter(
            Q(line_type__isnull=True) | Q(line_type='')
        )
    
    for row in datas:
        try:
            clean_phone = row.phonenumber
            line_type = row.line_type 
            phone_data = returnNumberData_v5(clean_phone)
            line_type = phone_data.get('line_type', 'invalid')
            if line_type == 'invalid':
                row.line_type = 'invalid'
                row.dnc_type = 'invalid'
            else:
                row.line_type = line_type
                if not row.dnc_type or row.dnc_type == 'n/a' or row.dnc_type == '':
                    row.dnc_type = returnNumberDncData_v3(clean_phone)
                else:
                    row.dnc_type = row.dnc_type
                row.carrier_name = phone_data.get('carrier_name', 'n/a')
                row.city = phone_data.get('city', 'n/a')
                row.state = phone_data.get('state', 'n/a')
                row.country = phone_data.get('country', 'n/a')
            fix_objects.append(row)
        except: 
            pass
    
    if len(fix_objects) > 0:
        CsvFileData.objects.bulk_update(fix_objects, list(required_data_fields_list_no_phone))
    return len(fix_objects) 


def fixApiNumberTypesData_V2(apibulk_resultid):
    fix_objects = []
    datas = APIData.objects.filter(apibulk__uid=apibulk_resultid).order_by('-id').filter(line_type__isnull=True)
    for row in datas:
        try:
            row = fixNumberRowData_util(row)
            if row is not None:
                fix_objects.append(row)
        except: 
            pass
        
    if len(fix_objects) > 0:
        APIData.objects.bulk_update(fix_objects, list(required_data_fields_list_no_phone))
    return None 




#used in celery task - celery_HandleUpload - can be deleted after testing
def fixNumberTypesData(file_uid):
    fix_objects = []
    datas = CsvFileData.objects.filter(csvfile__uid=file_uid).exclude(phonenumber='invalid').filter(line_type__isnull=True)
    for row in datas:
        try:
            # print(row.phonenumber, row.line_type, row.dnc_type)
            clean_phone = row.phonenumber
            row.line_type = isNumberFoundInModels(clean_phone)
            row.dnc_type = returnCleanDNCType(isDncNumberFound(clean_phone)).lower()
            fix_objects.append(row)
        except: 
            pass
    
    if len(fix_objects) > 0:
        CsvFileData.objects.bulk_update(fix_objects, ['line_type','dnc_type'])
    return None 

#old- can be deleted after testing
def api_fixNumberTypesData(apibulk_resultid):
    fix_objects = []
    datas = APIData.objects.filter(apibulk__uid=apibulk_resultid).order_by('-id').filter(line_type__isnull=True)
    for row in datas:
        try:
            # print(row.phonenumber, row.line_type, row.dnc_type)
            clean_phone = row.phonenumber
            row.line_type = isNumberFoundInModels(clean_phone)
            row.dnc_type = returnCleanDNCType(isDncNumberFound(clean_phone)).lower()
            fix_objects.append(row)
        except: 
            pass
    if len(fix_objects) > 0:
        APIData.objects.bulk_update(fix_objects, ['line_type','dnc_type'])
    return None 



#not in use - used in celery task - celery_HandleUpload
def SendEmailToUser(email, filename, download_file_url, dashboard_url):
    subject = f"Notification: Your File ({filename}) is ready for download."
    message = f"""Thank you for using LandlineRemover.com \n 
    Here is link to download your file. {download_file_url} \n
    or You can check your files in your dashboard here. {dashboard_url}"""
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)


#not in use - used in celery task - celery_HandleUpload
def SendFailedEmailToUser(email, filename):
    subject = f"Notification: Your File ({filename}) has failed."
    message = f"""Thank you for using LandlineRemover.com \n 
    Your file is failed to process. Please Check your file again and reupload. \n 
    Your credits are reversed."""
    return send_mail(subject,message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)


from api.models import CsvFileEmail, CsvFileDataEmail
def saveCsvFileEmailDataToCSV(file_uid, checkprrows=False):
    try:
        # Fetch the CsvFile object
        csvfile = CsvFileEmail.objects.get(uid=file_uid)

        # Reading the CSV data from the file (NEW bucket first, OLD as fallback)
        file = default_storage.open(csvfile.csvfile.name, 'rb')
        user_df = pd.read_csv(file, encoding='latin-1', encoding_errors="ignore",
                              low_memory=True, on_bad_lines='skip',
                              skip_blank_lines=True, dtype=str)

        # Determine the queryset for csvfile data
        if checkprrows:
            # When filtering by processed rows
            csvfiledata = CsvFileDataEmail.objects.filter(
                csvfile__uid=file_uid, is_processed=True
            ).order_by('pk').values_list(*required_data_fields_list_full)
        else:
            # All rows
            csvfiledata = CsvFileDataEmail.objects.filter(
                csvfile__uid=file_uid
            ).order_by('pk').values_list(*required_data_fields_list_full)

        # Convert the query result into a DataFrame
        output_df = pd.DataFrame(csvfiledata)
        output_df = output_df.fillna('n/a')  # Handle missing values

        # Set proper column names
        output_df.columns = csv_output_columns

        # Concatenate user data (from CSV) and output data (from the database)
        new_df = pd.concat([user_df, output_df], axis=1, sort=False).reindex(user_df.index)
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]  # Remove duplicated columns

        # Apply custom cleaning for 'LLR_CarrierName'
        new_df['LLR_CarrierName'] = new_df['LLR_CarrierName'].apply(returnCleanCarrierName)

        # Initialize S3 client
        s3 =  get_s3_client()
        if not s3:
            raise RuntimeError("Failed to initialize S3 client from proxy")
        # Create an in-memory string buffer for the CSV data
        csv_buffer = StringIO()

        # Save the DataFrame to the buffer
        new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False, na_rep='N/A')

        # Define the S3 file path
        output_fp_s3 = f"csv_output_files/{file_uid}.csv"

        # Upload to S3 bucket
        uploaded = False
        s3_client = get_s3_client()
        if s3_client and settings.AWS_STORAGE_BUCKET_NAME:
            try:
                s3_client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=output_fp_s3, Body=csv_buffer.getvalue())
                uploaded = True
                print(f"✅ [CSV OUTPUT] Uploaded to S3 bucket: {output_fp_s3}")
            except Exception as e:
                print(f"❌ [ERROR] Failed to upload to S3: {str(e)}")
        
        if not uploaded:
            s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=output_fp_s3, Body=csv_buffer.getvalue())
            print(f"✅ [CSV OUTPUT] Uploaded to S3 bucket: {output_fp_s3}")

        # Cleanup
        csv_buffer.close()

        # Cleanup DataFrames
        output_df = None
        new_df = None
        user_df = None

        return True
    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred: {str(e)}")
        return False


#used in celery task - celery_HandleUpload
def UploadCSVDATA(file_uid):
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
    except ObjectDoesNotExist:
        raise ValueError(f"CsvFile with UID {file_uid} does not exist.")
    
    col_phonenumber = "LLR_PhoneNumber"

    file_key = csvfile.csvfile.name

    try:
        # Read file from S3 storage
        file = default_storage.open(file_key, 'rb')
        file_content = file.read().decode('latin-1')
    except Exception as e:
        raise ValueError(f"Error fetching file from S3: {str(e)}")

    clean_data = pd.read_csv(StringIO(file_content), 
                             encoding='latin-1', 
                             low_memory=True, 
                             on_bad_lines='skip', 
                             skip_blank_lines=True, 
                             dtype=str, 
                             skipinitialspace=True, 
                             usecols=[col_phonenumber])

    if col_phonenumber not in clean_data.columns:
        raise ValueError(f"Required column '{col_phonenumber}' is missing in the CSV file.")
    
    clean_data = clean_data.to_dict(orient='records')

    csvfiledata_objs = []
    for data in clean_data[:csvfile.total_rows_charged]:
        csvfiledata_objs.append(CsvFileData(csvfile=csvfile, phonenumber=data[col_phonenumber]))

    if len(csvfiledata_objs) > 0:
        CsvFileData.objects.bulk_create(csvfiledata_objs, ignore_conflicts=True, batch_size=900)

    # Cleanup
    csvfiledata_objs = None
    clean_data = None

from api.models import CsvFileEmail, CsvFileDataEmail
# def UploadCSVEmailDATA(file_uid):
#     try:
#         # Fetch the CsvFile object from the database
#         csvfile = CsvFileEmail.objects.get(uid=file_uid)
#     except ObjectDoesNotExist:
#         raise ValueError(f"CsvFile with UID {file_uid} does not exist.")

#     col_phonenumber = "LLR_Email"

#     # Initialize S3 client
#     s3 = get_s3_client()
    #   if not s3:
    #         raise RuntimeError("Failed to initialize S3 client from proxy")

#     # Get the file URL from the S3 bucket
#     s3_bucket_name = settings.AWS_STORAGE_BUCKET_NAME
#     file_key = csvfile.csvfile.name  # The path to the file in the S3 bucket

    

#     # Fetch the file from S3
#     try:
#         s3_object = s3.get_object(Bucket=s3_bucket_name, Key=file_key)
#         file_content = s3_object['Body'].read().decode('latin-1')  # Read file content and decode
#     except Exception as e:
#         raise ValueError(f"Error fetching file from S3: {str(e)}")

#     # Use pandas to read the CSV data from the file content
#     clean_data = pd.read_csv(StringIO(file_content),
#                              encoding='latin-1',
#                              low_memory=True,
#                              on_bad_lines='skip',
#                              skip_blank_lines=True,
#                              dtype=str,
#                              skipinitialspace=True)

  

#     # Check if the required column is in the CSV
#     if col_phonenumber not in clean_data.columns:
#         raise ValueError(f"Required column '{col_phonenumber}' is missing in the CSV file.")

#     # Convert the data to a list of dictionaries
#     clean_data = clean_data.to_dict(orient='records')
    
#     # Create CsvFileData objects
#     csvfiledata_objs = []
#     for data in clean_data[:csvfile.total_rows_charged]:
       
#         csvfiledata_objs.append(CsvFileDataEmail(csvfile=csvfile, email=data[col_phonenumber]))

#     # Bulk create CsvFileData objects
#     if len(csvfiledata_objs) > 0:
#         CsvFileDataEmail.objects.bulk_create(csvfiledata_objs, ignore_conflicts=True, batch_size=900)

#     # Cleanup
#     csvfiledata_objs = None
#     clean_data = None

# def UploadCSVEmailDATA(file_uid, user_email):
#     try:
#         # Fetch the CsvFile object from the database
#         csvfile = CsvFileEmail.objects.get(uid=file_uid)
#     except ObjectDoesNotExist:
#         raise ValueError(f"CsvFile with UID {file_uid} does not exist.")
#
#     col_phonenumber = "LLR_Email"
#
#     # Initialize S3 client
#     s3 =  get_s3_client()
    #   if not s3:
    #         raise RuntimeError("Failed to initialize S3 client from proxy")
#
#     # Get the file URL from the S3 bucket
#     s3_bucket_name = settings.AWS_STORAGE_BUCKET_NAME
#     file_key = csvfile.csvfile.name  # The path to the file in the S3 bucket
#
#
#
#     # Fetch the file from S3
#     try:
#         s3_object = s3.get_object(Bucket=s3_bucket_name, Key=file_key)
#         file_content = s3_object['Body'].read().decode('latin-1')  # Read file content and decode
#     except Exception as e:
#         raise ValueError(f"Error fetching file from S3: {str(e)}")
#
#     # Use pandas to read the CSV data from the file content
#     clean_data = pd.read_csv(StringIO(file_content),
#                              encoding='latin-1',
#                              low_memory=True,
#                              on_bad_lines='skip',
#                              skip_blank_lines=True,
#                              dtype=str,
#                              skipinitialspace=True)
#
#
#
#     # Check if the required column is in the CSV
#     if col_phonenumber not in clean_data.columns:
#         raise ValueError(f"Required column '{col_phonenumber}' is missing in the CSV file.")
#
#     # Convert the data to a list of dictionaries
#     clean_data = clean_data.to_dict(orient='records')
#
#
#     try:
#         # Fetch the CsvFile object from the database
#         csvfile = CsvFileEmail.objects.get(uid=file_uid)
#     except ObjectDoesNotExist:
#         raise ValueError(f"CsvFile with UID {file_uid} does not exist.")
#
#         # Reverse credits for duplicates
#     total_rows_duplicates = 0
#     for data in clean_data:
#         email = data[col_phonenumber]
#         if email and CsvFileDataEmail.objects.filter(csvfile__user=csvfile.user, email=email).exists():
#             total_rows_duplicates += 1  # Count duplicates without reversing credits here
#
#
#
#     # Reverse credits for duplicates after counting
#     data1 = 0
#     if total_rows_duplicates > 0:
#         try:
#             # Assume the `email` variable contains the email address of the logged-in user
#             # For example, if you have the email for the logged-in user from the request, fetch the profile.
#             # user_email = 'user@example.com'  # Replace this with the actual user email or logic to get it
#             up = UserProfile.objects.get(user=UserModel.objects.get(email=user_email))
#             previous_credits = up.email_credits
#             up.email_credits = F('email_credits') + total_rows_duplicates  # Reverse credits for duplicates
#             data1 = total_rows_duplicates
#             up.save()
#
#
#             user_bulk_upload_activity(
#                     user=up.user,
#                     description=f"{total_rows_duplicates} Credits After Duplicates for csv file {csvfile.csvfile_name} in Email mode",
#                     actions=UserActivityLog.ActionType.EMAILUPLOAD,
#                     amount=0,
#                     prev_credits=previous_credits,
#                     remaining_credits=previous_credits + total_rows_duplicates,
#                     earned_credits=0
#                 )
#
#
#
#         except UserProfile.DoesNotExist:
#             raise ValueError("User profile not found.")
#         except UserModel.DoesNotExist:
#             raise ValueError("User not found.")
#
#     else:
#         try:
#             up = UserProfile.objects.get(user=UserModel.objects.get(email=user_email))
#             previous_credits = up.email_credits
#             user_bulk_upload_activity(
#                 user=up.user,
#                 description=f"Credits After Duplicates for {csvfile.csvfile_name} in Email mode",
#                 actions=UserActivityLog.ActionType.EMAILUPLOAD,
#                 amount=0,
#                 prev_credits=previous_credits,
#                 remaining_credits=previous_credits,
#                 earned_credits=0
#             )
#
#         except UserProfile.DoesNotExist:
#             raise ValueError("User profile not found.")
#         except UserModel.DoesNotExist:
#             raise ValueError("User not found.")
#
#     # Update the CSV file record with the count of duplicates
#     csvfile.total_rows_duplicates = data1
#     csvfile.save()
#
#
#
#     # Create CsvFileData objects
#     csvfiledata_objs = []
#     for data in clean_data[:csvfile.total_rows_charged]:
#         email = data[col_phonenumber]
#
#         # Check if email is a duplicate and mark as duplicate in the CSVFileData
#         is_duplicate = CsvFileDataEmail.objects.filter(email=email).exists()
#
#         # Create the CsvFileDataEmail object
#         csvfiledata_obj = CsvFileDataEmail(
#             csvfile=csvfile,
#             email=email,
#             is_duplicate=is_duplicate  # Mark the entry as a duplicate if it already exists
#         )
#         csvfiledata_objs.append(csvfiledata_obj)
#
#     # Bulk create CsvFileData objects
#     if len(csvfiledata_objs) > 0:
#         CsvFileDataEmail.objects.bulk_create(csvfiledata_objs, ignore_conflicts=True, batch_size=900)
#
#     duplicate_count = CsvFileDataEmail.objects.filter(is_duplicate=True, csvfile=csvfile).count()
#     # csvfile.total_rows_duplicates = duplicate_count
#     print(f"===============**********==========************>{csvfile.total_rows_duplicates}")
#     csvfile.save()
#
#     # Cleanup
#     csvfiledata_objs = None
#     clean_data = None
#     print(f"===============**********------==========************>{csvfile.total_rows_duplicates}")
#     return csvfile.total_rows_duplicates
from collections import Counter


def UploadCSVEmailDATA(file_uid, user_email):
    try:
        csvfile = CsvFileEmail.objects.get(uid=file_uid)
    except ObjectDoesNotExist:
        raise ValueError(f"CsvFile with UID {file_uid} does not exist.")

    col_phonenumber = "LLR_Email"

    file_key = csvfile.csvfile.name

    try:
        # Read file from S3 storage
        file = default_storage.open(file_key, 'rb')
        file_content = file.read().decode('latin-1')
    except Exception as e:
        raise ValueError(f"Error fetching file from S3: {str(e)}")

    clean_data = pd.read_csv(StringIO(file_content),
                             encoding='latin-1',
                             low_memory=True,
                             on_bad_lines='skip',
                             skip_blank_lines=True,
                             dtype=str,
                             skipinitialspace=True)

    if col_phonenumber not in clean_data.columns:
        raise ValueError(f"Required column '{col_phonenumber}' is missing in the CSV file.")

    clean_data = clean_data.to_dict(orient='records')

    # Step 1: Extract all emails from file
    email_list = [data[col_phonenumber].strip() for data in clean_data if data.get(col_phonenumber)]

    # Step 2: Check for already existing emails for the user
    existing_emails = set(
        CsvFileDataEmail.objects.filter(csvfile__user=csvfile.user, email__in=email_list)
        .values_list("email", flat=True)
    )

    # Step 3: Detect duplicates correctly (first one is allowed, second is duplicate)
    seen_emails = set()
    duplicate_emails_set = set()
    duplicate_indices = set()

    for idx, email in enumerate(email_list):
        if email in seen_emails or email in existing_emails:
            duplicate_emails_set.add(email)
            duplicate_indices.add(idx)
        else:
            seen_emails.add(email)

    # Step 4: Reverse credits
    total_rows_duplicates = len(duplicate_indices)

    try:
        up = UserProfile.objects.get(user=UserModel.objects.get(email=user_email))
        previous_credits = up.email_credits

        if total_rows_duplicates > 0:
            up.email_credits = F("email_credits") + total_rows_duplicates
            up.save()

            user_bulk_upload_activity(
                user=up.user,
                # description=f"{total_rows_duplicates} duplicate emails found for CSV file '{csvfile.csvfile_name}' — credits reversed.",
                description=f"{total_rows_duplicates} Credits After Duplicates for csv file {csvfile.csvfile_name} in Email mode",
                actions=UserActivityLog.ActionType.EMAILUPLOAD,
                amount=0,
                prev_credits=previous_credits,
                remaining_credits=previous_credits + total_rows_duplicates,
                earned_credits=0
            )
        else:
            user_bulk_upload_activity(
                user=up.user,
                # description=f"No duplicates found for CSV file '{csvfile.csvfile_name}'.",
                description=f"Credits After Duplicates for csv file {csvfile.csvfile_name} in Email mode",
                actions=UserActivityLog.ActionType.EMAILUPLOAD,
                amount=0,
                prev_credits=previous_credits,
                remaining_credits=previous_credits,
                earned_credits=0
            )

    except UserProfile.DoesNotExist:
        raise ValueError("User profile not found.")
    except UserModel.DoesNotExist:
        raise ValueError("User not found.")

    csvfile.total_rows_duplicates = total_rows_duplicates
    csvfile.save()

    # Step 5: Create CsvFileDataEmail records with correct `is_duplicate`
    csvfiledata_objs = []

    for i, data in enumerate(clean_data[:csvfile.total_rows_charged]):
        email = data.get(col_phonenumber, "").strip()
        if not email:
            continue

        is_duplicate = (email in existing_emails or i in duplicate_indices)

        csvfiledata_obj = CsvFileDataEmail(
            csvfile=csvfile,
            email=email,
            is_duplicate=is_duplicate
        )
        csvfiledata_objs.append(csvfiledata_obj)

    if csvfiledata_objs:
        CsvFileDataEmail.objects.bulk_create(csvfiledata_objs, ignore_conflicts=True, batch_size=900)

    return total_rows_duplicates
def returnUserDuplicatesData(number_list, user_obj, bulk_file_uid=None, apibulk_uid=None):
    total_count = 0
    paginator = Paginator(number_list, 1000)

    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list

        if bulk_file_uid is None:
            csvdata_list = CsvFileData.objects.filter(csvfile__user=user_obj, csvfile__is_charged=True, csvfile__is_complete=True).filter(phonenumber__in=numbers_list).values_list('phonenumber', flat=True)
        else:
            csvdata_list = CsvFileData.objects.exclude(csvfile__uid=bulk_file_uid).filter(csvfile__user=user_obj, csvfile__is_charged=True, csvfile__is_complete=True).filter(phonenumber__in=numbers_list).values_list('phonenumber', flat=True)
        csvdata_list = list(set(csvdata_list))

        if apibulk_uid is None:
            api_qs_list = APIData.objects.filter(userprofile=user_obj.profile, phonenumber__in=numbers_list).values_list('phonenumber', flat=True)
        else:
            api_qs_list = APIData.objects.exclude(apibulk__uid=apibulk_uid).filter(userprofile=user_obj.profile, phonenumber__in=numbers_list).values_list('phonenumber', flat=True)
        
        api_qs_list = list(set(api_qs_list))
        merge_db_list = list(set(chain(csvdata_list, api_qs_list)))
        total_count += sum(f in merge_db_list for f in numbers_list)

    return total_count


def HandleBulkUploadReversedDuplicateNumbers(file_uid):
    # get csv file obj 
    csvfile_obj = CsvFile.objects.get(uid=file_uid)
    current_user = csvfile_obj.user 

    records = CsvFileData.objects.filter(csvfile=csvfile_obj).order_by('pk').exclude(phonenumber='invalid_data').values_list('phonenumber', flat=True)
    number_list = list(records)
   
    total_count = returnUserDuplicatesData(number_list=number_list, user_obj=current_user, bulk_file_uid=file_uid)
    csvfile_obj.total_rows_duplicates = total_count
    csvfile_obj.save()
    up = UserProfile.objects.get(user=current_user)
    up.credits = F('credits') + total_count
    up.save()
     


def HandleBulkAPIReversedDuplicateNumbers(apibulk_id):

    apibulk_obj = APIBULK.objects.get(uid=apibulk_id)
    current_user = apibulk_obj.user 
    records = APIData.objects.filter(apibulk=apibulk_obj).order_by('pk').values_list('phonenumber', flat=True)
    number_list = list(records)

    total_count = returnUserDuplicatesData(number_list=number_list, user_obj=current_user, apibulk_uid=apibulk_id)

    # print(total_count)

    apibulk_obj.total_rows_duplicates = total_count
    apibulk_obj.save()
    up = UserProfile.objects.get(user=current_user)
    up.credits = F('credits') + total_count
    up.save()

    return None 


#util method
def UpdateDncDatabase(matched_records):
    try:
        new_objects = []
        for key, value in matched_records.items():
            value = value.replace(',','').strip()
            new_objects.append(DNCNumberData(phonenumber = key, dnc_type = value))
        DNCNumberData.objects.bulk_create(new_objects, batch_size=800, ignore_conflicts=True)
    except: 
        pass


def HandleDNCTCPABulkAPI(input_numbers_list):
    found_in_db = DNCNumberData.objects.filter(phonenumber__in=input_numbers_list).values('phonenumber', 'dnc_type')
    found_in_db = [fid for fid in found_in_db]
    numbers_found_in_db = [str(ob1["phonenumber"]).strip() for ob1 in found_in_db]
    yet_to_crawl_numbers = list(set(input_numbers_list) - set(numbers_found_in_db))
    matched_records, cleaned_records = API_DNCTCPA_SPLIT().GetSmallList(yet_to_crawl_numbers)

    #celery method to update DNC database for DNC and litigators numbers
    if len(matched_records) > 0:
        UpdateDncDatabase(matched_records)
    
    try:
        #convert found_in_db to one dict and merge with others 
        found_in_db = [{mr['phonenumber']:mr['dnc_type']} for mr in found_in_db]
        found_in_db = reduce(lambda a, b: {**a, **b}, found_in_db)
    except:
        found_in_db = {}

    found_in_db.update(matched_records)
    found_in_db.update(cleaned_records)
    matched_records = None 
    cleaned_records = None 
    return found_in_db



def genrateCsvFileDataToCSV(file_uid, line_type='all', dnc_type='all', download_filter=None,endato_response=False,checkWithEndatoOnly=False):
    try:
        # Get the CSV file from the database
        csvfile = CsvFile.objects.get(uid=file_uid)

        # Try to access the file from S3 storage
        s3_file_path = csvfile.csvfile.name  # This is the path relative to your S3 bucket root
        file_found = False
        file = None

        # Try reading from S3 storage
        try:
            file = default_storage.open(s3_file_path, 'rb')
            file_found = True
        except FileNotFoundError:
            # If not found in either bucket, check local media storage
            local_file_path = os.path.join(settings.MEDIA_ROOT, s3_file_path)
            if os.path.exists(local_file_path):
                file = open(local_file_path, 'r')  # Open the file locally
                file_found = True

        if not file_found:
            return HttpResponse("File not found.", status=404)

        # Read the CSV file into a DataFrame
        user_df = pd.read_csv(file, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)

        # Get related data from CsvFileData
        if endato_response and not checkWithEndatoOnly:
            csvfiledata = CsvFileData.objects.filter(csvfile__uid=file_uid, is_processed=True).order_by('pk').values_list(*required_data_fields_list_full_two)
            output_df = pd.DataFrame(csvfiledata, columns=csv_output_columns_two)
        elif endato_response and checkWithEndatoOnly:
            csvfiledata = EndatoCsvFileData.objects.filter(csvfile__uid=file_uid).order_by('pk').values_list(*endato_required_data_fields_list_full)
            output_df = pd.DataFrame(csvfiledata, columns=endato_csv_output_columns)
        else:
            csvfiledata = CsvFileData.objects.filter(csvfile__uid=file_uid, is_processed=True).order_by('pk').values_list(*required_data_fields_list_full)
            output_df = pd.DataFrame(csvfiledata, columns=csv_output_columns)

        output_df = output_df.fillna('n/a')    

        # Combine the data
        new_df = pd.concat([user_df, output_df], axis=1, sort=False).reindex(user_df.index)
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]

        # Clean the data
        if not checkWithEndatoOnly:
            new_df['LLR_CarrierName'] = new_df['LLR_CarrierName'].apply(returnCleanCarrierName)

        # Apply filters if necessary
        if not checkWithEndatoOnly:
            if download_filter != 'full':
                if line_type != 'all':
                    new_df = new_df[new_df['LLR_LineType'].str.lower() == line_type]
                if dnc_type != 'all':
                    new_df = new_df[new_df['LLR_DNCType'].str.lower() == dnc_type]

        # Prepare CSV output
        buffer = io.StringIO()
        new_df.to_csv(buffer, encoding='latin-1', header=True, index=False, na_rep='N/A')
        buffer.seek(0)

        # Send the CSV file as a response
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_uid}.csv"'

        # Clean up
        output_df = None
        new_df = None
        user_df = None

        return response
    except Exception as e:
        print("Error generating CSV file:", e)
        return HttpResponse("Failed to generate CSV file.", status=500)


from api.models import CsvFileEmail, CsvFileDataEmail
def genrateCsvFileEmailDataToCSV(file_uid, line_type='all', dnc_type='all', download_filter=None):
    try:
        # Get the CSV file from the database
        csvfile = CsvFileEmail.objects.get(uid=file_uid)

        # Try to access the file from S3 storage
        s3_file_path = csvfile.csvfile.name  # This is the path relative to your S3 bucket root
        file_found = False
        file = None

        # Try reading from S3 storage
        try:
            file = default_storage.open(s3_file_path, 'rb')
            file_found = True
        except FileNotFoundError:
            # If not found in either bucket, check local media storage
            local_file_path = os.path.join(settings.MEDIA_ROOT, s3_file_path)
            if os.path.exists(local_file_path):
                file = open(local_file_path, 'r')  # Open the file locally
                file_found = True

        if not file_found:
            return HttpResponse("File not found.", status=404)

        # Read the CSV file into a DataFrame
        user_df = pd.read_csv(file, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)

        # Get related data from CsvFileData
        csvfiledata = CsvFileDataEmail.objects.filter(csvfile__uid=file_uid, is_processed=True).order_by('pk').values_list(*csvemaildata_model_required_fields)
        output_df = pd.DataFrame(csvfiledata, columns=csv_output_email_columns)
        output_df = output_df.fillna('n/a')

        # Combine the data
        new_df = pd.concat([user_df, output_df], axis=1, sort=False).reindex(user_df.index)
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]

        # Clean the data
        # new_df['LLR_CarrierName'] = new_df['LLR_CarrierName'].apply(returnCleanCarrierName)

        # Apply filters if necessary
        # if download_filter != 'full':
        #     if line_type != 'all':
        #         new_df = new_df[new_df['LLR_LineType'].str.lower() == line_type]
        #     if dnc_type != 'all':
        #         new_df = new_df[new_df['LLR_DNCType'].str.lower() == dnc_type]

        # Prepare CSV output
        buffer = io.StringIO()
        new_df.to_csv(buffer, encoding='latin-1', header=True, index=False, na_rep='N/A')
        buffer.seek(0)

        # Send the CSV file as a response
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_uid}.csv"'

        # Clean up
        output_df = None
        new_df = None
        user_df = None

        return response
    except Exception as e:
        print("Error generating CSV file:", e)
        return HttpResponse("Failed to generate CSV file.", status=500)



def UploadCSVFirstLastName(file_uid):
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
    except ObjectDoesNotExist:
        raise ValueError(f"CsvFile with UID {file_uid} does not exist.")

    col_phonenumber = "LLR_PhoneNumber"
    first_name_col = "LLR_FirstName"
    last_name_col = "LLR_LastName"

    file_key = csvfile.csvfile.name

    try:
        # Read file from S3 storage
        file = default_storage.open(file_key, 'rb')
        file_content = file.read().decode('latin-1')
    except Exception as e:
        raise ValueError(f"Error fetching file from S3: {str(e)}")
    
  
    clean_data = pd.read_csv(StringIO(file_content),
                             encoding='latin-1',
                             low_memory=True,
                             on_bad_lines='skip',
                             skip_blank_lines=True,
                             dtype=str,
                             skipinitialspace=True,
                             usecols=[col_phonenumber, first_name_col, last_name_col])
    
    if first_name_col not in clean_data.columns or last_name_col not in clean_data.columns:
        raise ValueError(f"Required columns '{first_name_col}' and/or '{last_name_col}' are missing in the CSV file.")


    clean_data = clean_data.to_dict(orient='records')

    csvfiledata_objs = []
    for data in clean_data[:csvfile.total_rows_charged]:
        phone_number = data[col_phonenumber].strip()
        first_name = data[first_name_col].strip()
        last_name = data[last_name_col].strip()

        csvfiledata_objs.append(EndatoApiResponse(
            csvfile=csvfile,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name
        ))

    if len(csvfiledata_objs) > 0:
        EndatoApiResponse.objects.bulk_create(csvfiledata_objs, ignore_conflicts=True, batch_size=900)
        print(f"{len(csvfiledata_objs)} records successfully saved to the database.")

    csvfiledata_objs = None
    clean_data = None



#used in celery task - celery_HandleUpload
# updated at november 2023
def saveCsvFileDataToCSV(file_uid,endato_response, checkprrows=False):
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
        
        # Open from S3 storage
        file = default_storage.open(csvfile.csvfile.name, 'rb')
        try:
            user_df = pd.read_csv(file, encoding='utf-8', encoding_errors='ignore',
                                  low_memory=True, on_bad_lines='skip', 
                                  skip_blank_lines=True, dtype=str)
        except:
            file.seek(0)  # Reset file pointer for retry
            user_df = pd.read_csv(file, encoding='latin-1', encoding_errors='ignore',
                                  low_memory=True, on_bad_lines='skip', 
                                  skip_blank_lines=True, dtype=str)
        if endato_response:
            if checkprrows:
                csvfiledata = CsvFileData.objects.filter(
                    csvfile__uid=file_uid, is_processed=True
                ).order_by('pk').values_list(*required_data_fields_list_full_two)
            else:
                csvfiledata = CsvFileData.objects.filter(
                        csvfile__uid=file_uid
                    ).order_by('pk').values_list(*required_data_fields_list_full_two)
        else:
            if checkprrows:
                csvfiledata = CsvFileData.objects.filter(
                    csvfile__uid=file_uid, is_processed=True
                ).order_by('pk').values_list(*required_data_fields_list_full)
            else:
                csvfiledata = CsvFileData.objects.filter(
                        csvfile__uid=file_uid
                    ).order_by('pk').values_list(*required_data_fields_list_full)

        
        output_df = pd.DataFrame(csvfiledata)
        output_df = output_df.fillna('n/a') 


        if endato_response:
            output_df.columns = csv_output_columns_two
        else:
            output_df.columns = csv_output_columns

        
        new_df = pd.concat([user_df, output_df], axis=1, sort=False).reindex(user_df.index)
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]  

        
        new_df['LLR_CarrierName'] = new_df['LLR_CarrierName'].apply(returnCleanCarrierName)
        
        s3 =  get_s3_client()
        if not s3:
            raise RuntimeError("Failed to initialize S3 client from proxy")
                
        csv_buffer = StringIO()

        new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False, na_rep='N/A')

        output_fp_s3 = f"csv_output_files/{file_uid}.csv"

        # Upload to S3 bucket
        uploaded = False
        s3_client = get_s3_client()
        if s3_client and settings.AWS_STORAGE_BUCKET_NAME:
            try:
                s3_client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=output_fp_s3, Body=csv_buffer.getvalue())
                uploaded = True
                print(f"✅ [CSV OUTPUT] Uploaded to S3 bucket: {output_fp_s3}")
            except Exception as e:
                print(f"❌ [ERROR] Failed to upload to S3: {str(e)}")
        
        if not uploaded:
            s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=output_fp_s3, Body=csv_buffer.getvalue())
            print(f"✅ [CSV OUTPUT] Uploaded to S3 bucket: {output_fp_s3}")

        csv_buffer.close()
        output_df = None
        new_df = None 
        user_df = None

        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False



def UploadendatoCSVDATA(file_uid):
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
    except ObjectDoesNotExist:
        raise ValueError(f"CsvFile with UID {file_uid} does not exist.")
    
    col_phonenumber = "LLR_PhoneNumber"

    file_key = csvfile.csvfile.name

    try:
        # Read file from S3 storage
        file = default_storage.open(file_key, 'rb')
        file_content = file.read().decode('latin-1')
    except Exception as e:
        raise ValueError(f"Error fetching file from S3: {str(e)}")

    clean_data = pd.read_csv(StringIO(file_content), 
                             encoding='latin-1', 
                             low_memory=True, 
                             on_bad_lines='skip', 
                             skip_blank_lines=True, 
                             dtype=str, 
                             skipinitialspace=True, 
                             usecols=[col_phonenumber])

    if col_phonenumber not in clean_data.columns:
        raise ValueError(f"Required column '{col_phonenumber}' is missing in the CSV file.")
    
    clean_data = clean_data.to_dict(orient='records')

    csvfiledata_objs = []
    for data in clean_data[:csvfile.total_rows_charged]:
        csvfiledata_objs.append(EndatoCsvFileData(csvfile=csvfile, phonenumber=data[col_phonenumber]))

    if len(csvfiledata_objs) > 0:
        EndatoCsvFileData.objects.bulk_create(csvfiledata_objs, ignore_conflicts=True, batch_size=900)

    csvfiledata_objs = None
    clean_data = None






def endatosaveCsvFileDataToCSV(file_uid,endato_response, checkprrows=False):
    try:
        csvfile = CsvFile.objects.get(uid=file_uid)
        
        # Open from S3 storage
        file = default_storage.open(csvfile.csvfile.name, 'rb')
        try:
            user_df = pd.read_csv(file, encoding='utf-8', encoding_errors='ignore',
                                  low_memory=True, on_bad_lines='skip', 
                                  skip_blank_lines=True, dtype=str)
        except:
            file.seek(0)  # Reset file pointer for retry
            user_df = pd.read_csv(file, encoding='latin-1', encoding_errors='ignore',
                                  low_memory=True, on_bad_lines='skip', 
                                  skip_blank_lines=True, dtype=str)
        if endato_response:
            if checkprrows:
                csvfiledata = EndatoCsvFileData.objects.filter(
                    csvfile__uid=file_uid, is_processed=True
                ).order_by('pk').values_list(*endato_required_data_fields_list_full)
            else:
                csvfiledata = EndatoCsvFileData.objects.filter(
                        csvfile__uid=file_uid
                    ).order_by('pk').values_list(*endato_required_data_fields_list_full)
        
        output_df = pd.DataFrame(csvfiledata)
        output_df = output_df.fillna('n/a') 

        if endato_response:
            output_df.columns = endato_csv_output_columns
        
        new_df = pd.concat([user_df, output_df], axis=1, sort=False).reindex(user_df.index)
        new_df = new_df.loc[:, ~new_df.columns.duplicated()]  

        s3 =  get_s3_client()
        if not s3:
            raise RuntimeError("Failed to initialize S3 client from proxy")
        
        csv_buffer = StringIO()

        new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False, na_rep='N/A')

        output_fp_s3 = f"csv_output_files/{file_uid}.csv"

        # Upload to S3 bucket
        uploaded = False
        s3_client = get_s3_client()
        if s3_client and settings.AWS_STORAGE_BUCKET_NAME:
            try:
                s3_client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=output_fp_s3, Body=csv_buffer.getvalue())
                uploaded = True
                print(f"✅ [CSV OUTPUT] Uploaded to S3 bucket: {output_fp_s3}")
            except Exception as e:
                print(f"❌ [ERROR] Failed to upload to S3: {str(e)}")
        
        if not uploaded:
            s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=output_fp_s3, Body=csv_buffer.getvalue())
            print(f"✅ [CSV OUTPUT] Uploaded to S3 bucket: {output_fp_s3}")

        csv_buffer.close()
        output_df = None
        new_df = None 
        user_df = None

        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False



# endato reverse credits 

def endatoHandleReversedCredits_v1(DjModel,bulkfile_uid = None,checkprrows=False):
    try:
        csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
        person_search_API = CheckEndatoApi.objects.get(csvfile=csvfile_obj, check_with_endato=True, check_with_endato_only =False )

        if csvfile_obj.is_complete or checkprrows:
            current_user = csvfile_obj.user 
            credits_to_return = util_endatoHandleReversedCredits_v1(DjModel,bulkfile_uid,checkprrows)
            csvfile_obj.total_rows_duplicates = credits_to_return

            if person_search_API:
                csvfile_obj.total_enrichment_rows_duplicates = credits_to_return

            csvfile_obj.save()
            up = UserProfile.objects.get(user=current_user)
            old_credits = up.endato_credits
            # up.endato_credits = F('endato_credits') + credits_to_return
            up.endato_credits = up.endato_credits + credits_to_return
            up.save()


            description = f"{credits_to_return} Credits After Duplicates for csv file {csvfile_obj.csvfile_name} in Enrichment mode" if credits_to_return > 0 else f"Credits After Duplicates for {csvfile_obj.csvfile_name} in Enrichment mode"
            remaining_credits = up.endato_credits
            try:
                user_bulk_upload_activity(
                    user=current_user,
                    description=description,
                    actions=UserActivityLog.ActionType.DATAENRICHBULKUPLOAD,
                    amount=0,
                    prev_credits=old_credits,
                    remaining_credits=remaining_credits,
                    earned_credits=0
                )

            except Exception as e:
                print(f'ERROR CREATING LOGS FOR REVERSE CREDITS IN ENRICHMENT MODE: {e}')

            return credits_to_return

    except:
        pass
    return None


def util_endatoHandleReversedCredits_v1(DjModel,bulkfile_uid = None,checkprrows=False):
    csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
    current_user = csvfile_obj.user 
    if checkprrows:
        csvfile_numbers_list = list(DjModel.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj,is_processed=True).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))
    else:
        csvfile_numbers_list = list(DjModel.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))
    
    
    paginator = Paginator(csvfile_numbers_list, 1000)
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        userdatalogs_numbers_list = endatoHandleUserDataLogsLookup_v3(current_user, numbers_list, csvfile_obj.uploaded_at)
        csvfile_numbers_list = list(set(csvfile_numbers_list) - set(userdatalogs_numbers_list))
        
    return csvfile_obj.total_rows_charged - len(csvfile_numbers_list)



# def helper_CsvFileDataWavix(file_uid, checkprrows=False):
#     try:
#         csvfile = CsvFile.objects.get(uid=file_uid)
#     except CsvFile.DoesNotExist:
#         print(f"CSVFILE with UID {file_uid} does not exist.")
#         return
#     except Exception as e:
#         print(f"An unexpected error occurred while retrieving the CSVFILE: {str(e)}")
#         return

#     if checkprrows:
#         records = CsvFileData.objects.exclude(phonenumber='invalid').filter(
#             csvfile__uid=file_uid,
#             is_processed=True
#         ).filter(
#             Q(line_type__isnull=True) | Q(line_type='')
#         )
#     else:
#         records = CsvFileData.objects.exclude(phonenumber='invalid').filter(
#             csvfile__uid=file_uid
#         ).filter(
#             Q(line_type__isnull=True) | Q(line_type='')
#         )
    
#     if not records.exists():
#         print(f"No records found for CSVFILE UID {file_uid}.")
#         return

#     all_number_list = []
#     wavix_response_received = False
#     try:
#         phone_data = [str(ob.phonenumber).strip() for ob in records if ob.phonenumber != 'invalid_data']
#         if phone_data:
#             try:
#                 tracker_object = WavixRequestTracker.objects.create(csvfile=csvfile)
#             except Exception as e:
#                 print(f"Failed to create WAVIX tracker for file UID {file_uid}: {str(e)}", exc_info=True)
#                 return
            
#             all_number_list.extend(['1' + str(num).strip() for num in phone_data])
#             validate_phone_numbers(all_number_list, csvfile,tracker_object)
#             wavix_response_received = True
#         else:
#             print("No phone data available for WAVIX processing.")
#     except Exception as e:
#         print(f"WAVIX priority processing encountered an error: {str(e)}", exc_info=True)
#         return

#     if wavix_response_received:
#         try:
#             tracker_object.is_completed = True
#             tracker_object.save()
#             print(f"WAVIX processing completed successfully for file UID {file_uid}.")
#         except Exception as e:
#             print(f"Error updating WAVIX tracker for file UID {file_uid}: {str(e)}")
#     else:
#         print("WAVIX processing yielded no data. Continuing with paginator logic.")


logger = logging.getLogger(__name__)



def util_handleCreditsAnalytics(bulkfile_uid = None,checkprrows=False):
    csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
    current_user = csvfile_obj.user 
    if checkprrows:
        csvfile_numbers_list = list(CsvFileData.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj,is_processed=True).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))
    else:
        csvfile_numbers_list = list(CsvFileData.objects.exclude(phonenumber='invalid_data').filter(csvfile=csvfile_obj).values_list('phonenumber', flat=True).order_by('phonenumber').distinct('phonenumber'))

    paginator = Paginator(csvfile_numbers_list, 1000)
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        userdatalogs_numbers_list = handleUserDataLogsLookup_v3(current_user, numbers_list, csvfile_obj.uploaded_at)
        csvfile_numbers_list = list(set(csvfile_numbers_list) - set(userdatalogs_numbers_list))
        
        

    paginator = Paginator(csvfile_numbers_list, 1000)
    for page in range(1, paginator.num_pages+1):
        numbers_list = paginator.page(page).object_list
        api_qs_list = APIData.objects.filter(userprofile=current_user.profile, phonenumber__in=numbers_list, timestamp__lt=csvfile_obj.uploaded_at).values_list('phonenumber', flat=True)
        csvfile_numbers_list = list(set(csvfile_numbers_list))

    if csvfile_numbers_list:
        from_db_numbers = list(CsvFileData.objects.filter(
        csvfile=csvfile_obj,
        phonenumber__in=csvfile_numbers_list,
        number_checked_from_db=True
        ).values_list('phonenumber', flat=True).distinct())

        from_api_numbers = list(CsvFileData.objects.filter(
            csvfile=csvfile_obj,
            phonenumber__in=csvfile_numbers_list,
        ).exclude(number_checked_from_db=True).exclude(phonenumber='invalid_data').values_list('phonenumber', flat=True).distinct())


        print(f"--- total_numbers : {len(csvfile_numbers_list)} ---- , --- db_checked_numbers: {len(from_db_numbers)} --- , --- api_called_numbers: {len(from_api_numbers)} ---")
        if current_user.profile.is_test_user:
            TestUserCreditAnalytics.objects.update_or_create(
                csvfile=csvfile_obj,
                defaults={
                    'total_numbers': len(csvfile_numbers_list),
                    'db_checked_numbers': len(from_db_numbers),
                    'api_called_numbers': len(from_api_numbers),
                }
            )

        else:
            CreditAnalytics.objects.update_or_create(
                csvfile=csvfile_obj,
                defaults={
                    'total_numbers': len(csvfile_numbers_list),
                    'db_checked_numbers': len(from_db_numbers),
                    'api_called_numbers': len(from_api_numbers),
                }
            )





def util_handleCreditsAnalyticsBulkApi(bulkapi_uid=None):
    if not bulkapi_uid:
        return

    try:
        api_obj = APIBULK.objects.get(uid=bulkapi_uid)
    except APIBULK.DoesNotExist:
        return  

    current_user = api_obj.user

    from_db_numbers = APIData.objects.filter(
        apibulk=api_obj,
        userprofile__user=current_user,
        number_checked_from_db=True
    ).values_list('phonenumber', flat=True).distinct()


    from_api_numbers = APIData.objects.filter(
        apibulk=api_obj,
        userprofile__user=current_user
    ).exclude(number_checked_from_db=True).values_list('phonenumber', flat=True).distinct()

    if current_user.profile.is_test_user:
         TestUserCreditAnalytics.objects.update_or_create(
            api_bulk=api_obj,
            defaults={
                'added_through' : CreditAnalytics.ADDED_THROUGH.BULK_API,
                'total_numbers': from_db_numbers.count() + from_api_numbers.count(),
                'db_checked_numbers': from_db_numbers.count(),
                'api_called_numbers': from_api_numbers.count(),
                }
            )
    else:
        CreditAnalytics.objects.update_or_create(
            api_bulk=api_obj,
            defaults={
                'added_through' : CreditAnalytics.ADDED_THROUGH.BULK_API,
                'total_numbers': from_db_numbers.count() + from_api_numbers.count(),
                'db_checked_numbers': from_db_numbers.count(),
                'api_called_numbers': from_api_numbers.count(),
            }
        )

def util_count_invalid_data(bulkfile_uid = None,checkprrows=False):
    csvfile_obj = CsvFile.objects.get(uid=bulkfile_uid)
    if checkprrows:
        csvfile_numbers_list = list(CsvFileData.objects.filter(csvfile=csvfile_obj,is_processed=True,phonenumber='invalid_data').values_list('phonenumber', flat=True).order_by('phonenumber'))
    else:
        csvfile_numbers_list = list(CsvFileData.objects.filter(csvfile=csvfile_obj,phonenumber='invalid_data').values_list('phonenumber', flat=True).order_by('phonenumber'))
    csvfile_obj.total_invalid_data_rows =  len(csvfile_numbers_list)
    csvfile_obj.save()
    return len(csvfile_numbers_list) or 0
