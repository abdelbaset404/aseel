# tokens/models.py

from django.conf import settings
from django.utils import timezone
from rest_framework.authtoken.models import Token as AuthToken
from django.db import models

class ExpiringToken(AuthToken):
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(seconds=settings.TOKEN_EXPIRE_TIME)
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
