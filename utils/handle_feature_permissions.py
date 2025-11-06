from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from dashboard.models import Feature, FeaturePermission
from django.conf import settings

User = get_user_model()

@shared_task
def assign_all_permissions_to_all_users(feature_ids):
    features = Feature.objects.filter(id__in=feature_ids)
    users = User.objects.all()

    for user in users:
        for feature in features:
            FeaturePermission.objects.get_or_create(user=user, feature=feature)

    return f"Permissions applied to {users.count()} users for {features.count()} selected features."


# use shell command
"""
1> python manage.py shell
>>> from utils.handle_feature_permissions import assign_all_permissions_to_all_users
>>> assign_all_permissions_to_all_users()         
"""
