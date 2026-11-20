from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_minor", "is_active", "created_at")
    list_filter = ("role", "is_minor", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("JIFUNZE Profile", {"fields": ("role", "preferred_language", "is_minor")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("JIFUNZE Profile", {"fields": ("role", "preferred_language", "is_minor")}),
    )
