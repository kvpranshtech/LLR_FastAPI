from utils.handle_telegram import alertOnTelegram
from utils.handle_emailing import sendAlertEmail

"""
    - feb 24
    - it will take alert message and send on telegram
    - status: working
"""
def send_AlertOnTelegram(alert_message):
    status_ = alertOnTelegram(alert_message)
    return status_


def send_AlertOnEmail(email_, subject_, message_ ):
    try:
        sendAlertEmail(email_, subject_, message_)
    except:
        pass