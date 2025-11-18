"""
Admin configuration for Activity models.
"""
from django.contrib import admin
from .models import Activity, ActivityFile


class ActivityFileInline(admin.TabularInline):
    model = ActivityFile
    extra = 0
    readonly_fields = ['file_size', 'uploaded_at']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'max_participants_per_meeting', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['title', 'description', 'created_by__username', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ActivityFileInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Configuración de reuniones', {
            'fields': ('max_participants_per_meeting', 'min_participants_per_meeting')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ActivityFile)
class ActivityFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'activity', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'activity__title']
    readonly_fields = ['file_size', 'uploaded_at']
