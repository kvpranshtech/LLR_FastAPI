import logging
import uuid
import requests
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
import os 
from dashboard.templatetags.dashboard_tags import has_feature
from datetime import timedelta
from django.utils import timezone
# models
from django_celery_results.models import TaskResult
from site_settings.models import SSLCertificateRenew
from adminv2.models import Team, TeamToken, UserActivityLog
from datastorage.models import InvalidNumbersDataLogs, UserDataLogs0, UserDataLogs1, UserDataLogs2, UserDataLogs3, \
    UserDataLogs4, UserDataLogs5, UserDataLogs6, UserDataLogs7, UserDataLogs8, UserDataLogs9
from api.models import APIBULK, APIData
from core.models import CsvFile, CsvFileData, StripeSubscriptions, CustomSubscriptions
from filecleaner.models import CsvFileCleaner
from site_settings.models import CustomSiteLogs
from utils.handle_logs import create_log_
from utils._base import returnDjModels
from django.contrib.auth.models import User
from dashboard.models import UserProfile, CustomerBillingAddress, Payment, RedeemOffers
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model

from utils.logs import user_bulk_upload_activity_with_subscription

UserModel = get_user_model()
logger = logging.getLogger(__name__)


def create_log(model_response, model_name, delete_datetime=None):
    #print(f"{model_name}:", model_response)
    if delete_datetime is None:
        delete_datetime = ''
    else:
        delete_datetime = f"Older Than {delete_datetime.date()}"

    try:
        if model_response[0] > 0:
            create_log_(level=2, log_type='AutoDataCleaner', 
                message=f"Removed {model_response[0]} Record(s) from Model: {model_name} {delete_datetime}", 
                metadata=model_response[1], inspect_stack=2
            )
    except:
        create_log_on_fail(model_name)


def create_log_on_fail(model_name):
    create_log_(level=3, log_type='AutoDataCleaner', message=f"Unable to remove records from Model: {model_name}")


def autoClean_RawCsvFiles():
    ## Remove Empty CSVfile Records which older than 7 days and didn't complete the process. 
    _7_days_ago = timezone.now() - timezone.timedelta(days=7)
    try:
        empty_csvfiles_response = CsvFile.objects.filter(uploaded_at__lt=_7_days_ago, is_charged=False, is_complete=False, is_failed=False).delete()
        create_log(empty_csvfiles_response, 'CsvFile',  _7_days_ago)
    except:
        create_log_on_fail(model_name='CsvFile')
    return None


#need modifications _ ignore which files already cleaned.
def autoClean_CsvFileData():
    ## Remove the csv files data from csvFileData not removed csvfiles instances from table older than 6 months/185days. 
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 
    empty_records = 0
    try:
        csvfiles_qs = CsvFile.objects.filter(is_complete=True, is_charged=True, is_failed=False, uploaded_at__lt=_6_months_ago).order_by('-id')
        #print("csvfiles_qs", len(csvfiles_qs))
        for csvfile in csvfiles_qs:
            if empty_records > 10: 
                break
            csvfiledata_response = CsvFileData.objects.filter(csvfile=csvfile).delete()
            create_log(csvfiledata_response, 'CsvFileData',  _6_months_ago)
            if csvfiledata_response[0] < 1:
                empty_records +=1
    except:
        create_log_on_fail(model_name='CsvFileData')
    return None



def autoClean_InvalidNumberDataLogs():
    ## Remove invalid number data older than 6 months
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 
    try:
        model_response = InvalidNumbersDataLogs.objects.filter(timestamp__lt=_6_months_ago).delete()
        create_log(model_response, 'InvalidNumbersDataLogs', _6_months_ago)
    except:
        create_log_on_fail(model_name='InvalidNumbersDataLogs')
    return None



def autoClean_DNCDataLogs():
    ## Cleaning/removing the DNC data older than 6 months
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 
    try:
        dj_models_list = returnDjModels(app_name='datastorage', models_names_list=[f"DNCNumbersDataLogs{i}" for i in range(0, 10)])
        for djmodel in dj_models_list:
            model_response = djmodel.objects.filter(timestamp__lt=_6_months_ago).delete()
            create_log(model_response, djmodel.__name__, _6_months_ago)
    except:
        create_log_on_fail(model_name='DNCNumbersDataLogs')

    return None


def autoClean_TelynxDataLogs():
    ## Cleaning/removing the Telynxdata data older than 6 months
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 
    try:
        dj_models_list = returnDjModels(app_name='datastorage', models_names_list=[f"TelynxNumbersDataLogs{i}" for i in range(0, 10)])
        for djmodel in dj_models_list:
            model_response = djmodel.objects.filter(timestamp__lt=_6_months_ago).delete()
            create_log(model_response, djmodel.__name__, _6_months_ago)
    except:
        create_log_on_fail(model_name='TelynxNumbersDataLogs')

    return None


def autoClean_SignalwireDataLogs():
    ## Cleaning/removing the Signalwire data older than 6 months
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 
    try:
        dj_models_list = returnDjModels(app_name='datastorage', models_names_list=[f"SignalwireNumbersDataLogs{i}" for i in range(0, 10)])
        for djmodel in dj_models_list:
            model_response = djmodel.objects.filter(timestamp__lt=_6_months_ago).delete()
            create_log(model_response, djmodel.__name__, _6_months_ago)
    except:
        create_log_on_fail(model_name='SignalwireNumbersDataLogs')

    return None


def autoClean_NetNumberingDataLogs():
    ## Cleaning/removing the Signalwire data older than 6 months
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 
    try:
        dj_models_list = returnDjModels(app_name='datastorage', models_names_list=[f"NetNumberingDataLogs{i}" for i in range(0, 10)])
        for djmodel in dj_models_list:
            model_response = djmodel.objects.filter(timestamp__lt=_6_months_ago).delete()
            create_log(model_response, djmodel.__name__, _6_months_ago)
    except:
        create_log_on_fail(model_name='NetNumberingDataLogs')

    return None



def autoClean_APIData():
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 

    try:
        ## Remove the Bulk api records with APIdata older than 6 months.
        bulkapi_response = APIBULK.objects.filter(timestamp__lte=_6_months_ago).delete()
        create_log(bulkapi_response, 'APIBULK',  _6_months_ago)
    except:
        create_log_on_fail(model_name='APIBULK')

    try:
        ## Remove the Single APIData older than 6 months.
        apidata_response = APIData.objects.filter(timestamp__lte=_6_months_ago).delete()
        create_log(apidata_response, 'APIData',  _6_months_ago)
    except:
        create_log_on_fail(model_name='APIData')

    return None


def autoClean_UserDataLogs():
    ## Cleaning/removing the User data logs  older than 6 months
    _6_months_ago = timezone.now() - timezone.timedelta(days=185) 
    try:
        dj_models_list = returnDjModels(app_name='datastorage', models_names_list=[f"UserDataLogs{i}" for i in range(0, 10)])
        for djmodel in dj_models_list:
            model_response = djmodel.objects.filter(timestamp__lt=_6_months_ago).delete()
            create_log(model_response, djmodel.__name__, _6_months_ago)
    except:
        create_log_on_fail(model_name='UserDataLogs')
    return None


def autoClean_CeleryTaskResults():
    ## Remove the celery tasks logs older than 3 months.
    _6_months_ago = timezone.now() - timezone.timedelta(days=93) 
    try:
        apidata_response = TaskResult.objects.filter(date_created__lte=_6_months_ago).delete()
        create_log(apidata_response, 'TaskResult',  _6_months_ago)
    except:
        create_log_on_fail(model_name='TaskResult')
    return None


def autoClean_CustomSiteLogs():
    ## Remove the Custom site logs older than 3 months.
    _6_months_ago = timezone.now() - timezone.timedelta(days=93) 
    try:
        apidata_response = CustomSiteLogs.objects.filter(timestamp__lte=_6_months_ago).delete()
        create_log(apidata_response, 'CustomSiteLogs',  _6_months_ago)
    except:
        create_log_on_fail(model_name='CustomSiteLogs')
    return None


def autoClean_LogFile():
    ## Auto Clean Log file every 15 days | set cron in admin ui
    logs_fp = 'llr_site.log'
    current_dt = timezone.now() 

    try:
        with open(logs_fp, 'w', encoding='utf-8') as file:
            file.write('\n')

        create_log_(level=2, log_type='AutoDataCleaner', inspect_stack=1,
                message=f"AutoClean LogFile {logs_fp} at {current_dt}"
            )
    except:
        create_log_(level=3, log_type='AutoDataCleaner', message=f"Unable to clean the logs from {logs_fp}")

    return None 


def autoClean_CeleryLogFile():
    ## Auto Clean Log file every 15 days | set cron in admin ui
    logs_fp = 'celery_logs.txt'
    current_dt = timezone.now() 

    try:
        with open(logs_fp, 'w', encoding='utf-8') as file:
            file.write('\n')
        create_log_(level=2, log_type='AutoDataCleaner', inspect_stack=1,
                message=f"AutoClean LogFile {logs_fp} at {current_dt}"
            )
    except:
        create_log_(level=3, log_type='AutoDataCleaner', message=f"Unable to clean the logs from {logs_fp}")

    return None 



def autoClean_CeleryBeatLogFile():
    ## Auto Clean Log file every 15 days | set cron in admin ui
    logs_fp = 'celery_beat_logs.txt'
    current_dt = timezone.now() 

    try:
        with open(logs_fp, 'w', encoding='utf-8') as file:
            file.write('\n')
        create_log_(level=2, log_type='AutoDataCleaner', inspect_stack=1,
                message=f"AutoClean LogFile {logs_fp} at {current_dt}"
            )
    except:
        create_log_(level=3, log_type='AutoDataCleaner', message=f"Unable to clean the logs from {logs_fp}")

    return None 

def autoClean_MediaFiles():
    ## Auto delete media files from storage older than 6 months
    _6_months_ago = timezone.now() - timezone.timedelta(days=1) 
    logs_ = {
        'total_files': 0,
        'uploaded_files': 0,
        'output_files': 0,
    }
    try:
        csvfiles = CsvFile.objects.filter(uploaded_at__lt=_6_months_ago).order_by('id')

        for csvfile_ in csvfiles[:]:
            output_absolute_path = os.path.join(settings.MEDIA_ROOT, 'csv_output_files', f"{csvfile_.uid}.csv")
            if os.path.exists(output_absolute_path):
                os.remove(output_absolute_path)
                logs_['output_files'] += 1

            uploaded_absolute_path = csvfile_.csvfile.path 
            if os.path.exists(uploaded_absolute_path):
                os.remove(uploaded_absolute_path)
                logs_['uploaded_files'] += 1

        logs_['total_files'] = sum(logs_.values())

        create_log_(level=2, log_type='AutoDataCleaner', 
                    message=f"AutoClean {logs_['total_files']} Media Files Older Than {_6_months_ago.date()}", metadata=str(logs_),
                    inspect_stack=1,
                )
    except:
        create_log_(level=3, log_type='AutoDataCleaner', message=f"Unable to clean the media files")

    return None 

def autoClean_testusers():
    today_time = timezone.now() - timezone.timedelta(days=1)

    users_joined_today = User.objects.filter(date_joined__gte=today_time, is_superuser=False)

    test_users = []
    for users in users_joined_today:
        check_test_user = UserProfile.objects.filter(user=users, is_test_user=True).first()

        if check_test_user:
            test_users.append(check_test_user.user)

    try:
        for user in test_users:
            CsvFileCleaner.objects.filter(user=user).delete()

            # deleting logs
            UserDataLogs0.objects.filter(user=user).delete()
            UserDataLogs1.objects.filter(user=user).delete()
            UserDataLogs2.objects.filter(user=user).delete()
            UserDataLogs3.objects.filter(user=user).delete()
            UserDataLogs4.objects.filter(user=user).delete()
            UserDataLogs5.objects.filter(user=user).delete()
            UserDataLogs6.objects.filter(user=user).delete()
            UserDataLogs7.objects.filter(user=user).delete()
            UserDataLogs8.objects.filter(user=user).delete()
            UserDataLogs9.objects.filter(user=user).delete()

            ## deleting apis data
            APIBULK.objects.filter(user=user).delete()
            APIData.objects.filter(userprofile__user=user).delete()

            ## Deleting payments and billing address
            CustomerBillingAddress.objects.filter(user=user).delete()
            Payment.objects.filter(user=user).delete()
            RedeemOffers.objects.filter(user=user).delete()

            um = User.objects.filter(username=user)
            um.delete()
        return None
    except Exception as e:
        print("Error in delete user --> ",e)

def get_count_checks_users():
    total_users = UserModel.objects.all()
    print("total users -->> ", total_users.count())

    users_total_verified = UserModel.objects.filter(emailaddress__verified=True).count()
    users_total_unverified = UserModel.objects.filter(emailaddress__verified=False).count()

    print(f"Email verified user count--->> {users_total_verified} ,,, Email Unverified User count--->> {users_total_unverified}")

    user_total_phone_verified = UserModel.objects.filter(profile__otp_verified=True).count()
    user_total_phone_unverified = UserModel.objects.filter(profile__otp_verified=False).count()

    print(f"Phone verified user count--->> {user_total_phone_verified} ,,, Phone Unverified User count--->> {user_total_phone_unverified}")

    return None


def refresh_team_tokens():
    teams = Team.objects.filter(is_deleted=False)

    refreshed_count = 0
    for team in teams:  
        # Delete expired tokens for this team
        print("--------", team)
        expired_tokens = TeamToken.objects.filter(
            team_name=team,
            token_expiry_date__lt=timezone.now()
        )
        if expired_tokens.exists():
            logger.info(f"Deleting {expired_tokens.count()} expired tokens for team '{team.team_name}'")
            print(f"Deleting {expired_tokens.count()} expired tokens for team '{team.team_name}'")
            expired_tokens.delete()

        # Check if there's still a valid token
        # has_valid_token = TeamToken.objects.filter(
        #     team_name=team,
        #     token_expiry_date__gte=timezone.now()
        # ).exists()

        # # If no valid token exists, create a new one
        # if not has_valid_token:
        #     TeamToken.objects.create(team_name=team)
        #     refreshed_count += 1
        #     logger.info(f"Created new token for team '{team.team_name}'")

    logger.info(f"Refreshed tokens for {refreshed_count} teams.")
    return None

# from utils.handle_tasks import auto_change_team_token
# auto_change_team_token()


from django.utils import timezone

def renew_subscriptions_credits():
    now = timezone.now()  # UTC-aware
    now_utc = now.astimezone(timezone.utc) 
    print(now,'{}}{}{}{{}}')
    print(now_utc,':::::::::::::::::') # ensure UTC for comparisons

    profiles = UserProfile.objects.filter(
        subscription_status="active",
        plan_duration=UserProfile.PlanDuration.YEAR,
        subscriptions_period_start__isnull=False,
        subscriptions_period_end__isnull=False,
    )

    for profile in profiles:
        start = profile.subscriptions_period_start
        end = profile.subscriptions_period_end
        last_reset = profile.last_credit_reset_date

        # Convert DB fields to UTC for comparison
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)
        last_reset_utc = last_reset.astimezone(timezone.utc) if last_reset else None

        # Skip if outside subscription range
        if not (start_utc <= now_utc <= end_utc):
            logger.info(f'inside first conditions ---------------- ')
            continue

        subscription = StripeSubscriptions.objects.filter(
            price_id=profile.active_subscription_price_id
        ).first()

        if subscription:
            plan = subscription
        else:
            plan = CustomSubscriptions.objects.filter(
                price_id=profile.active_subscription_price_id
            ).first()

        if not plan:
            continue

        # Feature-based reset (fast reset in 3 mins)
        if has_feature(profile.user, "credit_reset"):
            logger.info(f'{profile.user}-user')
            if not last_reset_utc or last_reset_utc + timedelta(minutes=3) <= now_utc:
                logger.info(f'inside conditions ---------------- ')
                reset_credits(profile, now, plan)
            continue

        # First reset OR cycle restart
        if not last_reset_utc or last_reset_utc < start_utc:
            logger.info(f'inside third conditions ---------------- ')
            reset_credits(profile, now, plan)
            continue

        # Monthly reset check
        if now_utc >= last_reset_utc + relativedelta(months=1):
            logger.info(f'inside fourth conditions ---------------- ')
            reset_credits(profile, now, plan)
        else:
            logger.info(f'no condition executed  ---------------- ')



def reset_credits(profile, now, plan):
    profile.subscriptions_credits_number_checks = plan.nm_credits
    profile.last_credit_reset_date = now
    profile.save(update_fields=["subscriptions_credits_number_checks", "last_credit_reset_date"])
    print(f"Credits reset for {profile.user.email} on {now}")

    try:
        if profile.last_credit_reset_date:
            user_bulk_upload_activity_with_subscription(
                user=profile.user,
                actions=UserActivityLog.ActionType.UPDATED,
                description=f"Subscription credits renewed for plan '{plan.name}', {plan.nm_credits} credits added",
                subscription_remaining_credits=profile.subscriptions_credits_number_checks,
                subscription_earned_credits=plan.nm_credits
            )
        else:
            user_bulk_upload_activity_with_subscription(
                user=profile.user,
                actions=UserActivityLog.ActionType.UPDATED,
                description=f"Earned subscription credits for plan '{plan.name}', {plan.nm_credits} credits added",
                subscription_remaining_credits=profile.subscriptions_credits_number_checks,
                subscription_earned_credits=plan.nm_credits
            )

        print(f"Credits reset and log added for {profile.user.username}")
    except Exception as e:
        print(f"[Renew Flow Log Error] {e}")


def renew_custom_subscriptions_credits():
    now = timezone.now()  # always datetime

    profiles = UserProfile.objects.filter(
        subscription_status="active",
        is_custom_subscription=True,
        subscription_plan_id__isnull=False,
        plan_duration=UserProfile.PlanDuration.YEAR,
        subscriptions_period_start__isnull=False,
        subscriptions_period_end__isnull=False,
    )

    for profile in profiles:
        start = profile.subscriptions_period_start
        end = profile.subscriptions_period_end
        last_reset = profile.last_credit_reset_date

        # Skip if outside subscription range
        if not (start <= now <= end):
            continue

        try:
            plan_id = int(profile.subscription_plan_id)
            plan = CustomSubscriptions.objects.get(id=plan_id)
        except CustomSubscriptions.DoesNotExist:
            continue

        if not plan:
            continue

        # Feature-based reset (e.g. fast reset within 10 mins)
        if has_feature(profile.user, "credit_reset"):
            if not last_reset or last_reset + timedelta(minutes=1) <= now:
                reset_credits(profile, now, plan)
            continue

        # First reset OR cycle restart
        if not last_reset or last_reset < start:
            reset_credits(profile, now, plan)
            continue

        # Monthly reset check
        if now >= last_reset + relativedelta(months=1):
            reset_credits(profile, now, plan)


def cancel_custom_subscriptions():
    now = timezone.now()

    profiles = UserProfile.objects.filter(
        subscription_status="active",
        is_custom_subscription=True,
        subscription_plan_id__isnull=False,
        subscriptions_period_start__isnull=False,
        subscriptions_period_end__isnull=False,
    )

    for profile in profiles:
        end = profile.subscriptions_period_end

        if end and end < now:

            profile.subscriptions_credits_number_checks = 0
            profile.is_custom_subscription = False
            profile.subscription_plan_id = None
            profile.subscriptions_period_start = None
            profile.subscriptions_period_end = None
            profile.last_credit_reset_date = None
            profile.subscription_status = None
            profile.active_subscription_price_id = None
            profile.stripe_subscription_id = None

            print(f"Subscription is expired for user --- profile --{profile}")
            profile.save(update_fields=[
                "subscriptions_credits_number_checks",
                "is_custom_subscription",
                "subscription_plan_id",
                "subscriptions_period_start",
                "subscriptions_period_end",
                "last_credit_reset_date",
                "subscription_status",
                "active_subscription_price_id",
                "stripe_subscription_id",
            ])






def ssl_expiry_alerts():
    now = timezone.now()
    upcoming = now + timedelta(days=3)


    expiring_soon = SSLCertificateRenew.objects.filter(
        next_renewal__lte=upcoming,
        next_renewal__gte=now
    )

    if not expiring_soon.exists():
        return "No SSL expiring soon."

    for cert in expiring_soon:
        domain = cert.domain_name
        next_date = cert.next_renewal.strftime("%Y-%m-%d %H:%M")

        message = (
            f"⚠️ *SSL Expiry Alert*\n\n"
            f"🌐 Domain: `{domain}`\n"
            f"📅 Expires On: *{next_date}*\n"
            f"⏰ Please renew within 3 days."
        )

        send_telegram_message(message)


def send_telegram_message(message: str):
    """Send formatted message to Telegram bot chat."""
    bot_token = '8259031566:AAEn7Tp1qqvqpa2Hg_KfFgIPTUPD589Zzpo'
    chat_id = '-1002543674852'
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    print(data,"url--->>",url)
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram send error: {e}")
