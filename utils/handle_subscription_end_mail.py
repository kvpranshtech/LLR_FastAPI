from datetime import timedelta, date
from celery import shared_task
from core.models import Subscription
from django.conf import settings
from utils.handle_emailing import send_subscription_end_mail_

@shared_task
def notify_users_before_subscription_expires():
    today = date.today()

    #  send mail before 1 and 3 days from now
    notify_days = [today + timedelta(days=1), today + timedelta(days=3)]

    subscriptions = Subscription.objects.filter(
            is_active=True,
            end_date__in=notify_days
        ).select_related('user')

    total = len(subscriptions)

    for subscription in subscriptions:
        days_left = (subscription.end_date - today).days

        print(f"sent {total} mails for subscription expiry ---- ")
        subscription_plan = subscription.subscription_plan.name
        subscription_type = subscription.subscription_plan.plan_type
        send_subscription_end_mail_(subscription.user.email, subscription.user.username, subscription_plan, subscription_type, subscription.duration, days_left, subscription.end_date)

# run in terminal ---
# from utils.handle_subscription_end_mail import notify_users_before_subscription_expires
# notify_users_before_subscription_expires()
