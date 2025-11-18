"""
Celery tasks for events.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import timedelta
from .models import Event
from apps.enrollments.models import Enrollment


@shared_task
def check_upcoming_events():
    """
    Check for upcoming events and send notifications.
    Runs every 5 minutes via Celery Beat.
    """
    now = timezone.now()
    notification_time = now + timedelta(seconds=settings.NOTIFICATION_ADVANCE_TIME)

    # Get events that need notification
    events = Event.objects.filter(
        status=Event.Status.SCHEDULED,
        notification_sent=False,
        start_time__lte=notification_time,
        start_time__gte=now
    )

    for event in events:
        send_event_notification.delay(event.id)


@shared_task
def send_event_notification(event_id):
    """
    Send email notification to enrolled users about an upcoming event.

    Args:
        event_id: ID of the event
    """
    try:
        event = Event.objects.get(id=event_id)

        if event.notification_sent:
            return

        # Get enrolled users who want notifications
        enrollments = Enrollment.objects.filter(
            event=event,
            is_active=True,
            user__email_notifications=True
        ).select_related('user')

        recipients = [enrollment.user.email for enrollment in enrollments]

        if not recipients:
            event.notification_sent = True
            event.notification_sent_at = timezone.now()
            event.save()
            return

        # Prepare email
        subject = f"Recordatorio: {event.activity.title}"

        message = f"""
Hola,

Te recordamos que tienes una actividad de conversación programada:

Actividad: {event.activity.title}
Fecha y hora: {event.start_time.strftime('%d/%m/%Y a las %H:%M')}
Duración: {int((event.end_time - event.start_time).total_seconds() / 60)} minutos

Descripción:
{event.activity.description}

Por favor, asegúrate de estar disponible a la hora indicada. Recibirás el enlace a la videoconferencia cuando la reunión comience.

¡Nos vemos pronto!

Equipo de Talkabout
"""

        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        # Mark as notified
        event.notification_sent = True
        event.notification_sent_at = timezone.now()
        event.status = Event.Status.NOTIFIED
        event.save()

    except Event.DoesNotExist:
        pass
    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error sending notification for event {event_id}: {str(e)}")
