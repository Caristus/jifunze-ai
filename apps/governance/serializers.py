from rest_framework import serializers
from .models import ConsentRecord, DataRequest
class ConsentRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    class Meta:
        model = ConsentRecord
        fields = ["id", "username", "purpose", "consent_version", "granted", "guardian_name", "recorded_at", "withdrawn_at"]
        read_only_fields = ["id", "recorded_at", "withdrawn_at"]
class DataRequestSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source="requested_by.username", read_only=True)
    class Meta:
        model = DataRequest
        fields = ["id", "request_type", "status", "notes", "created_at", "resolved_at", "requested_by_name"]
        read_only_fields = ["id", "status", "created_at", "resolved_at"]
