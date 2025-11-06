from django.utils import timezone
from datetime import datetime
from datastorage.models import (NetNumberingDataLogs0,
                                NetNumberingDataLogs1,
                                NetNumberingDataLogs2,
                                NetNumberingDataLogs3,
                                NetNumberingDataLogs4,
                                NetNumberingDataLogs5,
                                NetNumberingDataLogs6,
                                NetNumberingDataLogs7,
                                NetNumberingDataLogs8,
                                NetNumberingDataLogs9)

def get_current_month_netnumbering_count():
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    netnumbering_models = [
        NetNumberingDataLogs0,
        NetNumberingDataLogs1,
        NetNumberingDataLogs2,
        NetNumberingDataLogs3,
        NetNumberingDataLogs4,
        NetNumberingDataLogs5,
        NetNumberingDataLogs6,
        NetNumberingDataLogs7,
        NetNumberingDataLogs8,
        NetNumberingDataLogs9
    ]

    total_count = 0

    for model in netnumbering_models:
        count = model.objects.filter(
            timestamp__year=current_year, 
            timestamp__month=current_month
        ).count()
        total_count += count

    return total_count

