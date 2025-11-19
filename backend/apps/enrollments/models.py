"""
Enrollment models for the Talkabout application.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.events.models import Event
import uuid


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


class EmailNotification(models.Model):
    """
    Track email notifications sent to users.
    """
    class NotificationType(models.TextChoices):
        ENROLLMENT_CONFIRMATION = 'ENROLLMENT_CONFIRMATION', _('Confirmación de Inscripción')
        FIRST_REMINDER = 'FIRST_REMINDER', _('Primer Recordatorio')
        SECOND_REMINDER = 'SECOND_REMINDER', _('Segundo Recordatorio (con enlace)')
        MEETING_READY = 'MEETING_READY', _('Reunión Lista')
        CANCELLATION = 'CANCELLATION', _('Cancelación')

    # Unique token for unsubscribe/response links
    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_('Token')
    )

    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='email_notifications',
        verbose_name=_('Inscripción')
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name=_('Tipo de Notificación')
    )

    recipient_email = models.EmailField(
        verbose_name=_('Email del Destinatario')
    )

    subject = models.CharField(
        max_length=255,
        verbose_name=_('Asunto')
    )

    # Whether the email was successfully sent
    sent = models.BooleanField(
        default=False,
        verbose_name=_('Enviado')
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Enviado el')
    )

    # Error message if sending failed
    error_message = models.TextField(
        blank=True,
        verbose_name=_('Mensaje de Error')
    )

    # User response (e.g., clicked "Not attending" in email)
    user_responded = models.BooleanField(
        default=False,
        verbose_name=_('Usuario Respondió')
    )

    user_response = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Respuesta del Usuario'),
        help_text=_('accepted, declined, tentative, unsubscribed')
    )

    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Respondió el')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notificación por Email')
        verbose_name_plural = _('Notificaciones por Email')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['enrollment']),
            models.Index(fields=['token']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['sent']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.enrollment.user.email}"
