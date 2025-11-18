"""
Event models for the Talkabout application.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.activities.models import Activity


class Event(models.Model):
    """
    Specific time slot for an activity.
    Users can enroll in events.
    """
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Programado')
        NOTIFIED = 'NOTIFIED', _('Notificado')
        IN_PROGRESS = 'IN_PROGRESS', _('En progreso')
        COMPLETED = 'COMPLETED', _('Completado')
        CANCELLED = 'CANCELLED', _('Cancelado')

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_('Actividad')
    )

    start_time = models.DateTimeField(
        verbose_name=_('Hora de inicio')
    )

    end_time = models.DateTimeField(
        verbose_name=_('Hora de fin')
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        verbose_name=_('Estado')
    )

    notification_sent = models.BooleanField(
        default=False,
        verbose_name=_('Notificación enviada')
    )

    notification_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Notificación enviada el')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Evento')
        verbose_name_plural = _('Eventos')
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['activity']),
            models.Index(fields=['start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['notification_sent']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_after_start_time'
            )
        ]

    def __str__(self):
        return f"{self.activity.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_past(self):
        """Check if event is in the past."""
        return self.end_time < timezone.now()

    @property
    def is_upcoming(self):
        """Check if event is upcoming (not started yet)."""
        return self.start_time > timezone.now()

    @property
    def is_active(self):
        """Check if event is currently active."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    @property
    def enrolled_count(self):
        """Get count of enrolled users."""
        return self.enrollments.filter(is_active=True).count()

    @property
    def attended_count(self):
        """Get count of users who attended."""
        from apps.meetings.models import Attendance
        meeting_ids = self.meetings.values_list('id', flat=True)
        return Attendance.objects.filter(meeting_id__in=meeting_ids).values('user').distinct().count()

    def can_enroll(self):
        """Check if users can still enroll."""
        return self.is_upcoming and self.status == self.Status.SCHEDULED
