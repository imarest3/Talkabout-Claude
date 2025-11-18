"""
Admin configuration for Meeting models.
"""
from django.contrib import admin
from .models import Meeting, Attendance


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ['joined_at', 'left_at', 'duration']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'platform', 'status', 'max_participants', 'attendance_count', 'created_at']
    list_filter = ['platform', 'status', 'created_at']
    search_fields = ['event__activity__title', 'meeting_id', 'meeting_url']
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'attendance_count']
    inlines = [AttendanceInline]

    fieldsets = (
        (None, {
            'fields': ('event', 'platform', 'max_participants')
        }),
        ('Detalles de la reunión', {
            'fields': ('meeting_url', 'meeting_id', 'platform_data')
        }),
        ('Estado', {
            'fields': ('status', 'error_message')
        }),
        ('Estadísticas', {
            'fields': ('attendance_count',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'started_at', 'completed_at')
        }),
    )

    def attendance_count(self, obj):
        return obj.attendance_count
    attendance_count.short_description = 'Asistentes'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'meeting', 'joined_at', 'left_at', 'duration']
    list_filter = ['joined_at', 'meeting__platform']
    search_fields = ['user__username', 'user__email', 'meeting__event__activity__title']
    readonly_fields = ['joined_at', 'left_at', 'duration']
    date_hierarchy = 'joined_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'meeting')
        }),
        ('Tiempos', {
            'fields': ('joined_at', 'left_at', 'duration')
        }),
    )
