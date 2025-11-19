"""
Activity models for the Talkabout application.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
import os
import uuid


def activity_file_path(instance, filename):
    """Generate file path for activity attachments."""
    return f'activities/{instance.activity.id}/{filename}'


class Activity(models.Model):
    """
    Communication activity proposed by a teacher.
    Can have multiple events associated with it.
    """
    # Unique code for activity identification (from edX or generated)
    activity_code = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,
        verbose_name=_('Código de Actividad'),
        help_text=_('Código único para identificar la actividad')
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_('Título')
    )

    description = models.TextField(
        verbose_name=_('Descripción'),
        help_text=_('Descripción detallada de la actividad de conversación')
    )

    # HTML description for rich content
    description_html = models.TextField(
        blank=True,
        verbose_name=_('Descripción HTML'),
        help_text=_('Descripción con formato HTML para mostrar en la interfaz')
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

    # Waiting room configuration
    waiting_time_minutes = models.PositiveIntegerField(
        default=3,
        verbose_name=_('Tiempo de espera (minutos)'),
        help_text=_('Tiempo que el sistema esperará a que se unan usuarios antes de crear las videoconferencias')
    )

    # Reminder configuration
    first_reminder_hours = models.PositiveIntegerField(
        default=24,
        verbose_name=_('Primer recordatorio (horas antes)'),
        help_text=_('Horas antes del evento para enviar el primer recordatorio')
    )

    second_reminder_minutes = models.PositiveIntegerField(
        default=5,
        verbose_name=_('Segundo recordatorio (minutos antes)'),
        help_text=_('Minutos antes del evento para enviar el segundo recordatorio con enlace de acceso')
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
            models.Index(fields=['activity_code']),
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


class WaitingRoom(models.Model):
    """
    Waiting room for an event where users wait before meetings are created.
    """
    class Status(models.TextChoices):
        WAITING = 'WAITING', _('Esperando')
        PROCESSING = 'PROCESSING', _('Procesando')
        COMPLETED = 'COMPLETED', _('Completado')
        CANCELLED = 'CANCELLED', _('Cancelado')

    event = models.OneToOneField(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='waiting_room',
        verbose_name=_('Evento')
    )

    # Unique token for access
    access_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_('Token de Acceso')
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
        verbose_name=_('Estado')
    )

    # When the waiting room opens (usually X minutes before event start)
    opens_at = models.DateTimeField(
        verbose_name=_('Abre el')
    )

    # When meetings will be created (event start_time + waiting_time_minutes)
    closes_at = models.DateTimeField(
        verbose_name=_('Cierra el')
    )

    # Users who joined the waiting room
    joined_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='WaitingRoomJoin',
        related_name='waiting_rooms',
        verbose_name=_('Usuarios que se unieron')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Procesado el')
    )

    class Meta:
        verbose_name = _('Sala de Espera')
        verbose_name_plural = _('Salas de Espera')
        ordering = ['opens_at']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['access_token']),
            models.Index(fields=['status']),
            models.Index(fields=['opens_at']),
        ]

    def __str__(self):
        return f"Sala de espera - {self.event}"

    @property
    def participant_count(self):
        """Get count of users who joined."""
        return self.waitingroomjoin_set.count()


class WaitingRoomJoin(models.Model):
    """
    Record of a user joining a waiting room.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waiting_room_joins',
        verbose_name=_('Usuario')
    )

    waiting_room = models.ForeignKey(
        WaitingRoom,
        on_delete=models.CASCADE,
        verbose_name=_('Sala de Espera')
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Se unió el')
    )

    # IP address for tracking
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Dirección IP')
    )

    # User agent for tracking
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('User Agent')
    )

    class Meta:
        verbose_name = _('Entrada a Sala de Espera')
        verbose_name_plural = _('Entradas a Salas de Espera')
        ordering = ['joined_at']
        unique_together = [['user', 'waiting_room']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['waiting_room']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.waiting_room}"
