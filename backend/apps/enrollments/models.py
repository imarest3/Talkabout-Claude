"""
Enrollment models for the Talkabout application.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.events.models import Event


class Enrollment(models.Model):
    """
    User enrollment in an event.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Usuario')
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Evento')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Activa'),
        help_text=_('Si está marcada como inactiva, el usuario se dio de baja')
    )

    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Cancelada el')
    )

    class Meta:
        verbose_name = _('Inscripción')
        verbose_name_plural = _('Inscripciones')
        ordering = ['-enrolled_at']
        unique_together = [['user', 'event']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['event']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.event}"

    def cancel(self):
        """Cancel the enrollment."""
        from django.utils import timezone
        self.is_active = False
        self.cancelled_at = timezone.now()
        self.save()
