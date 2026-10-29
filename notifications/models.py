from django.db import models
from django.conf import settings


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    key = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    email_error = models.TextField(blank=True)
    email_attempts = models.PositiveSmallIntegerField(default=0)
