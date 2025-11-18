"""
User models for the Talkabout application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """
    Custom User model with role-based permissions.

    Roles:
    - ADMIN: Full system access
    - TEACHER: Can create and manage activities
    - STUDENT: Can enroll in events and participate
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrador')
        TEACHER = 'TEACHER', _('Profesor')
        STUDENT = 'STUDENT', _('Estudiante')

    # Override email to make it unique and required
    email = models.EmailField(_('email address'), unique=True)

    # User role
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('Rol')
    )

    # External ID for edX integration (SHA-1 hash from edX USER_ID)
    external_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('ID Externo'),
        help_text=_('ID de usuario de edX (%%USER_ID%%)')
    )

    # Internal unique code for direct registrations
    user_code = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_('Código de Usuario')
    )

    # Profile information
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Teléfono')
    )

    timezone = models.CharField(
        max_length=50,
        default='Europe/Madrid',
        verbose_name=_('Zona Horaria')
    )

    # Preferences
    email_notifications = models.BooleanField(
        default=True,
        verbose_name=_('Notificaciones por Email')
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['user_code']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER or self.is_admin

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def save(self, *args, **kwargs):
        # Ensure superusers are always admins
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
