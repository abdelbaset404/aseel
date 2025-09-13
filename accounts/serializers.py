from rest_framework import serializers
from django.contrib.auth import authenticate
from tokens.models import ExpiringToken
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import ValidationError

class CustomAuthTokenSerializer(serializers.Serializer):
    employee_id = serializers.CharField(label="Employee ID")
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        employee_id = attrs.get('employee_id')
        password = attrs.get('password')

        if not employee_id or not password:
            raise ValidationError({
                "statusCode": 401,
                "message": "يجب إدخال رقم الموظف وكلمة المرور."
            })

        user = authenticate(
            request=self.context.get('request'),
            username=employee_id,
            password=password
        )

        if not user:
            raise ValidationError({
                "statusCode": 401,
                "message": "بيانات الدخول غير صحيحة. برجاء المحاولة مرة أخرى."
            })

        attrs['user'] = user
        return attrs