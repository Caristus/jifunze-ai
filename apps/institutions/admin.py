from django.contrib import admin
from .models import Institution, Membership
class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "institution_type", "curriculum", "is_active", "created_at")
    list_filter = ("country", "institution_type", "is_active")
    search_fields = ("name", "curriculum")
    inlines = [MembershipInline]
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "institution__name")
    autocomplete_fields = []
