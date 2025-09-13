from django.contrib.auth.backends import ModelBackend
from .models import CustomUser, ExpiringToken

class ExpiringTokenAuthenticationBackend(ModelBackend):
    def authenticate(self, request, token_key=None, **kwargs):
        try:
            token = ExpiringToken.objects.select_related('user').get(key=token_key)
            if token.is_expired:
                token.delete()
                return None
            return token.user
        except ExpiringToken.DoesNotExist:
            return None