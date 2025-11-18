"""
Admin configuration for Event models.
"""
from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['activity', 'start_time', 'end_time', 'status', 'enrolled_count', 'notification_sent']
    list_filter = ['status', 'notification_sent', 'start_time', 'activity']
    search_fields = ['activity__title']
    readonly_fields = ['created_at', 'updated_at', 'notification_sent_at', 'enrolled_count', 'attended_count']
    date_hierarchy = 'start_time'

    fieldsets = (
        (None, {
            'fields': ('activity', 'start_time', 'end_time')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Notificaciones', {
            'fields': ('notification_sent', 'notification_sent_at')
        }),
        ('Estadísticas', {
            'fields': ('enrolled_count', 'attended_count')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def enrolled_count(self, obj):
        return obj.enrolled_count
    enrolled_count.short_description = 'Inscritos'

    def attended_count(self, obj):
        return obj.attended_count
    attended_count.short_description = 'Asistentes'
