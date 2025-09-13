from rest_framework import serializers
from .models import SalaryStatement

class SalaryStatementSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    class Meta:
        model = SalaryStatement
        exclude = ['user']
