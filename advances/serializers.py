from rest_framework import serializers
from .models import AdvanceRequest

class AdvanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceRequest
        # المستخدم يبعت amount بس
        fields = ['id', 'amount', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
