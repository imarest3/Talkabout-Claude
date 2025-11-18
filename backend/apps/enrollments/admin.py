"""
Admin configuration for Enrollment models.
"""
from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'is_active', 'enrolled_at', 'cancelled_at']
    list_filter = ['is_active', 'enrolled_at', 'event__activity']
    search_fields = ['user__username', 'user__email', 'event__activity__title']
    readonly_fields = ['enrolled_at', 'cancelled_at']
    date_hierarchy = 'enrolled_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'event')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('enrolled_at', 'cancelled_at')
        }),
    )
