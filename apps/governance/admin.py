from django.contrib import admin
from .models import ConsentRecord, DataRequest
@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "purpose", "consent_version", "granted", "recorded_at", "withdrawn_at")
    list_filter = ("purpose", "granted", "institution")
@admin.register(DataRequest)
class DataRequestAdmin(admin.ModelAdmin):
    list_display = ("requested_by", "institution", "request_type", "status", "created_at", "resolved_at")
    list_filter = ("request_type", "status", "institution")
