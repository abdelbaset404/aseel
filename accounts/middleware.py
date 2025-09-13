from django.utils import timezone
from django.contrib.auth import logout
from tokens.models import ExpiringToken

class TokenExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request, 'auth'):
            if request.auth.is_expired:
                logout(request)
                request.auth.delete()
        
        return self.get_response(request)