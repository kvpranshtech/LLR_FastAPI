from django_celery_beat.models import CrontabSchedule, PeriodicTask, IntervalSchedule
import json 
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

def handleTestServicePeriodicTask(obj):
    start_time_ = timezone.now() 

    if obj.service_status:
        interval_schedule_obj = create_or_get_InvertalSchedule(obj.success_interval)
    else:
        interval_schedule_obj = create_or_get_InvertalSchedule(obj.failure_interval)


    if obj._state.adding:
        task_name = f"ServiceAlertSheduling_{obj.uid}"
        celery_task_ = "utils.handle_tasks.celery_handleAutoServiceAlert"
        required_params = {"uid":str(obj.uid)}
        createPeriodicTask(interval_schedule_obj, task_name, celery_task_, required_params, start_time_, obj.allow_tracking)
    else:
        updatePeriodicTask_Interval(obj.uid, interval_schedule_obj)

    if obj.allow_tracking:
        enablePeriodicTasks(uid_=obj.uid)
    else:
        disablePeriodicTask(uid_=obj.uid)

    return None 



def create_or_get_InvertalSchedule(minutes):
    _schedule, created = IntervalSchedule.objects.get_or_create(every=minutes, period=IntervalSchedule.MINUTES)
    return _schedule



def createPeriodicTask(interval_schedule_obj, task_name, celery_task_, required_params, start_time_, enable_status=True):
    periodic_task, created = PeriodicTask.objects.get_or_create(
        interval = interval_schedule_obj,
        name = task_name,
        task = celery_task_,
        kwargs = json.dumps(required_params),  # Serialize arguments to JSON
        enabled = enable_status,
        start_time = start_time_,
        priority = 100,
    )
    return periodic_task


def disablePeriodicTask(uid_):
    periodic_tasks_qs = PeriodicTask.objects.filter(name__icontains=uid_)
    for task_ in periodic_tasks_qs:
        task_.enabled = False
        task_.one_off = True
        task_.save()

def enablePeriodicTasks(uid_):
    periodic_tasks_qs = PeriodicTask.objects.filter(name__icontains=uid_)
    for task_ in periodic_tasks_qs:
        task_.enabled = True
        task_.one_off = False
        task_.save()


def deletePeriodicTasks(uid_):
    PeriodicTask.objects.filter(name__icontains=uid_).delete()

def updatePeriodicTask_Interval(uid_, interval_obj):
    disablePeriodicTask(uid_)
                                                                       
    periodic_tasks_qs = PeriodicTask.objects.filter(name__icontains=uid_)
    for task_ in periodic_tasks_qs:
        task_.interval = interval_obj
        task_.save()

    enablePeriodicTasks(uid_)
