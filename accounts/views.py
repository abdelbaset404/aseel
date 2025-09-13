from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_login
from django.views import View
from accounts.models import CustomUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import CustomAuthTokenSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.conf import settings
from tokens.models import ExpiringToken

class CustomLoginView(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        with transaction.atomic():
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

        return Response({
            'token': token.key,
            'employee_id': user.employee_id,
            'username': user.username,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_defult_password': user.is_defult_password,
        })
    
class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'message': ['يرجى إدخال كلمة المرور وتأكيدها.']},
                            status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'message': ['كلمتا المرور غير متطابقتين.']},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 4:
            return Response({'message':[ 'كلمة المرور يجب أن تكون على الأقل 4 أحرف.']},
                            status=status.HTTP_400_BAD_REQUEST)
        if new_password == "0000":
            return Response({'message':[ 'غير مسموح بتكرار كلمة المرور الافتراضية']},
                            status=status.HTTP_400_BAD_REQUEST)


        user.set_password(new_password)
        user.is_defult_password = False
        user.save()

        return Response({'message': ['تم تغيير كلمة المرور بنجاح. الرجاء تسجيل الدخول مجددًا.']},
                        status=status.HTTP_200_OK)

        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response(
            {'message': 'Successfully logged out.'},
            status=status.HTTP_200_OK
        )

class WebLoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('salary_list')
        return render(request, self.template_name)

    def post(self, request):
        employee_id = request.POST.get('employee_id')
        password = request.POST.get('password')
        user = authenticate(request, employee_id=employee_id, password=password)

        if user is not None:
            auth_login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            messages.success(request, 'تم تسجيل الدخول بنجاح')
            
            if user.is_defult_password:
                auth_login(request, user) 
                return redirect('reset-password')
            
            return redirect('salary_list')
        else:
            messages.error(request, 'بيانات الدخول غير صحيحة')
            return render(request, self.template_name)
    



from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

@login_required
def web_logout(request):
    auth_logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('web-login')

class ResetPasswordView(View):
    template_name = 'accounts/reset_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'كلمتا المرور غير متطابقتين')
            return render(request, self.template_name)

        if len(new_password) < 4:
            messages.error(request, 'كلمة المرور يجب أن تكون على الأقل 4 أحرف')
            return render(request, self.template_name)
        if new_password == "0000":
            messages.error(request, 'غير مسموح بتكرار كلمة المرور الافتراضية')
            return render(request, self.template_name)
        

        user = request.user
        user.set_password(new_password)
        user.is_defult_password = False
        user.save()

        messages.success(request, 'تم تحديث كلمة المرور بنجاح. يرجى تسجيل الدخول مرة أخرى.')
        return redirect('web-login')
