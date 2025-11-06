from djproject.celery import app

from djproject.celery import app as celery_app

from utils.handle_telegram import alertOnTelegram
from django.conf import settings

def terminateTask(task_id):
    app.control.revoke(task_id, terminate=True,signal='SIGKILL')
    return None 
def terminateTask_v3(task_id):
    app.control.revoke(task_id, terminate=True,signal='SIGKILL')
    return None 