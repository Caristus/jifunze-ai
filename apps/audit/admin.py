from django.contrib import admin
from .models import AuditEvent
@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "institution", "resource_type", "created_at")
    list_filter = ("action", "institution")
    readonly_fields = ("created_at", "metadata")
