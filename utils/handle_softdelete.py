from django.db import models
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    """
    Custom manager to filter out soft-deleted objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)