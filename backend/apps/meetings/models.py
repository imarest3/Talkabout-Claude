"""
Meeting models for the Talkabout application.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.events.models import Event


class Meeting(models.Model):
    """
    Video conference meeting created for an event.
    Multiple meetings can be created for a single event if there are too many participants.
    """
    class Platform(models.TextChoices):
        GOOGLE_MEET = 'GOOGLE_MEET', _('Google Meet')
        JITSI = 'JITSI', _('Jitsi')

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Programada')
        STARTED = 'STARTED', _('Iniciada')
        COMPLETED = 'COMPLETED', _('Completada')
        FAILED = 'FAILED', _('Fallida')

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='meetings',
        verbose_name=_('Evento')
    )

    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        default=Platform.JITSI,
        verbose_name=_('Plataforma')
    )

    meeting_url = models.URLField(
        verbose_name=_('URL de la reunión'),
        blank=True
    )

    meeting_id = models.CharField(
        max_length=255,
        verbose_name=_('ID de la reunión'),
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        verbose_name=_('Estado')
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Attendance',
        related_name='meetings',
        verbose_name=_('Participantes')
    )

    max_participants = models.PositiveIntegerField(
        verbose_name=_('Máximo de participantes')
    )

    # Meeting metadata from platform
    platform_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Datos de la plataforma')
    )

    # Error information if meeting creation fails
    error_message = models.TextField(
        blank=True,
        verbose_name=_('Mensaje de error')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Iniciada el')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completada el')
    )

    class Meta:
        verbose_name = _('Reunión')
        verbose_name_plural = _('Reuniones')
        ordering = ['event', 'created_at']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['status']),
            models.Index(fields=['platform']),
        ]

    def __str__(self):
        return f"Meeting {self.id} - {self.event} ({self.get_platform_display()})"

    @property
    def attendance_count(self):
        """Get count of users who attended."""
        return self.attendances.count()


class Attendance(models.Model):
    """
    Record of user attendance to a meeting.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Usuario')
    )

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Reunión')
    )

    # Timestamps
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Se unió el')
    )

    left_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Se fue el')
    )

    # Duration in seconds (calculated when user leaves)
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Duración (segundos)')
    )

    class Meta:
        verbose_name = _('Asistencia')
        verbose_name_plural = _('Asistencias')
        ordering = ['joined_at']
        unique_together = [['user', 'meeting']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['meeting']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.meeting}"

    def save(self, *args, **kwargs):
        # Calculate duration if both joined and left times are set
        if self.joined_at and self.left_at and not self.duration:
            self.duration = int((self.left_at - self.joined_at).total_seconds())
        super().save(*args, **kwargs)
