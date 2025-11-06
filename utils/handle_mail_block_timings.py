from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from dashboard.models import ForgotPasswordMailBlock

@shared_task
def update_request_time(minutes_to_update):
    now = timezone.now()
    # Fetch all active blocks
    active_blocks = ForgotPasswordMailBlock.objects.filter(
        created_at__lte=now,
        new_request_time__gte=now
    )

    for block in active_blocks:
        block.new_request_time = block.created_at + timedelta(minutes=minutes_to_update)
        block.save(update_fields=["new_request_time"])
