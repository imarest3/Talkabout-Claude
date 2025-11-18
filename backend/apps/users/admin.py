"""
Admin configuration for User model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'external_id', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'external_id', 'user_code']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Información adicional'), {
            'fields': ('role', 'external_id', 'user_code', 'phone', 'timezone', 'email_notifications')
        }),
        (_('Fechas importantes'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ['user_code', 'created_at', 'updated_at']

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Información adicional'), {
            'fields': ('email', 'role', 'external_id', 'phone', 'timezone')
        }),
    )
