# accounts/urls.py
from django.urls import path
from .views import CustomLoginView, WebLoginView,web_logout,LogoutView,ResetPasswordView,ChangePasswordAPI

urlpatterns = [
    path('api/login/', CustomLoginView.as_view(), name='api-login'),
    path('api/logout/', LogoutView.as_view(), name='api-logout'),
    path('api/change-password/', ChangePasswordAPI.as_view(), name='change-password-api'),
    path('login/', WebLoginView.as_view(), name='web-login'),
    path('logout/', web_logout, name='logout'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]