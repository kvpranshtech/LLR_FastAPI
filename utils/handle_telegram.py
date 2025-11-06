from django.conf import settings
from adminv2.models import TelegramConfigurations
import requests



# def alertOnTelegram(alert_message):
#     try:
#         url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={settings.TELEGRAM_BOT_CHAT_ID}&text={alert_message}"
#         response = requests.post(url, verify=True, timeout=90)
#         response.raise_for_status()
#         return True
#     except:
#         pass
#     return False


def alertOnTelegram(alert_message):
    telegram_config = TelegramConfigurations.objects.first()

    try:
        url = f"https://api.telegram.org/bot{telegram_config.bot_token}/sendMessage?chat_id={telegram_config.bot_chat_id}&text={alert_message}"
        response = requests.post(url, verify=True, timeout=90)
        response.raise_for_status()
        return True
    except:
        pass
    return False
