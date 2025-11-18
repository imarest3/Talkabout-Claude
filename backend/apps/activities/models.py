"""
Activity models for the Talkabout application.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import os


def activity_file_path(instance, filename):
    """Generate file path for activity attachments."""
    return f'activities/{instance.activity.id}/{filename}'


class Activity(models.Model):
    """
    Communication activity proposed by a teacher.
    Can have multiple events associated with it.
    """
    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )

    description = models.TextField(
        verbose_name=_('Descripción'),
        help_text=_('Descripción detallada de la actividad de conversación')
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_activities',
        verbose_name=_('Creado por'),
        limit_choices_to={'role__in': ['TEACHER', 'ADMIN']}
    )

    max_participants_per_meeting = models.PositiveIntegerField(
        default=settings.DEFAULT_MAX_PARTICIPANTS_PER_MEETING,
        validators=[MinValueValidator(2)],
        verbose_name=_('Máximo de participantes por reunión'),
        help_text=_('Número máximo de usuarios por videoconferencia')
    )

    min_participants_per_meeting = models.PositiveIntegerField(
        default=settings.MIN_PARTICIPANTS_PER_MEETING,
        validators=[MinValueValidator(2)],
        verbose_name=_('Mínimo de participantes por reunión')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activa')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Actividad')
        verbose_name_plural = _('Actividades')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Validate min/max participants
        if self.min_participants_per_meeting > self.max_participants_per_meeting:
            self.min_participants_per_meeting = self.max_participants_per_meeting
        super().save(*args, **kwargs)


class ActivityFile(models.Model):
    """
    Files associated with an activity.
    """
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('Actividad')
    )

    file = models.FileField(
        upload_to=activity_file_path,
        verbose_name=_('Archivo')
    )

    filename = models.CharField(
        max_length=255,
        verbose_name=_('Nombre del archivo')
    )

    file_size = models.PositiveIntegerField(
        verbose_name=_('Tamaño del archivo (bytes)'),
        default=0
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Archivo de actividad')
        verbose_name_plural = _('Archivos de actividad')
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.activity.title} - {self.filename}"

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = os.path.basename(self.file.name)
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
