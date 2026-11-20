from django.contrib import admin
from .models import Institution, Membership
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "institution_type", "ai_provider", "is_active", "created_at")
    list_filter = ("country", "institution_type", "ai_provider", "is_active")
    search_fields = ("name",)
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active", "institution")
    search_fields = ("user__username", "institution__name")
