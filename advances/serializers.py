from rest_framework import serializers
from .models import AdvanceRequest

class AdvanceRequestSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    status = serializers.SerializerMethodField()
    class Meta:
        model = AdvanceRequest
        # المستخدم يبعت amount بس
        fields = ['id', 'amount', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    def get_status(self, obj):
        # ده بيرجع النص العربي من choices اللي معرفه في الموديل
        return obj.get_status_display()
