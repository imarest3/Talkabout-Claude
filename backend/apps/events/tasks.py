"""
Celery tasks for events.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Event
from apps.enrollments.models import Enrollment, EmailNotification
from apps.enrollments.services import EmailService
from apps.activities.models import WaitingRoom
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_and_send_first_reminders():
    """
    Check for events and send first reminders (configured hours before event).
    Runs every hour via Celery Beat.
    """
    now = timezone.now()

    # Get events that are scheduled
    events = Event.objects.filter(
        status=Event.Status.SCHEDULED,
        start_time__gt=now
    ).select_related('activity')

    for event in events:
        # Check if it's time to send first reminder
        reminder_hours = event.activity.first_reminder_hours
        reminder_time = event.start_time - timedelta(hours=reminder_hours)

        # Allow 1 hour window to send reminder
        if reminder_time <= now <= (reminder_time + timedelta(hours=1)):
            send_first_reminder_for_event.delay(event.id)


@shared_task
def send_first_reminder_for_event(event_id):
    """
    Send first reminder emails to all enrolled users.

    Args:
        event_id: ID of the event
    """
    try:
        event = Event.objects.get(id=event_id)

        # Get active enrollments
        enrollments = Enrollment.objects.filter(
            event=event,
            is_active=True,
            user__email_notifications=True,
            user__is_anonymized=False
        ).select_related('user')

        for enrollment in enrollments:
            # Check if first reminder already sent
            existing = EmailNotification.objects.filter(
                enrollment=enrollment,
                notification_type=EmailNotification.NotificationType.FIRST_REMINDER
            ).first()

            if existing and existing.sent:
                continue

            # Create or get notification record
            notification, created = EmailNotification.objects.get_or_create(
                enrollment=enrollment,
                notification_type=EmailNotification.NotificationType.FIRST_REMINDER,
                defaults={
                    'recipient_email': enrollment.user.email,
                    'subject': f"Recordatorio: {event.activity.title}"
                }
            )

            # Send email
            result = EmailService.send_first_reminder(
                enrollment=enrollment,
                notification_token=str(notification.token),
                user_timezone=enrollment.user.timezone
            )

            # Update notification record
            if result['success']:
                notification.sent = True
                notification.sent_at = timezone.now()
                notification.save()
                logger.info(f"First reminder sent for event {event_id} to {enrollment.user.email}")
            else:
                notification.error_message = result.get('error', '')
                notification.save()
                logger.error(f"Failed to send first reminder: {result.get('error')}")

    except Event.DoesNotExist:
        logger.error(f"Event {event_id} not found")
    except Exception as e:
        logger.error(f"Error sending first reminder for event {event_id}: {str(e)}")


@shared_task
def check_and_send_second_reminders():
    """
    Check for events and send second reminders with waiting room link.
    Runs every minute via Celery Beat.
    """
    now = timezone.now()

    # Get events that are scheduled or notified
    events = Event.objects.filter(
        status__in=[Event.Status.SCHEDULED, Event.Status.NOTIFIED],
        start_time__gt=now
    ).select_related('activity')

    for event in events:
        # Check if it's time to send second reminder
        reminder_minutes = event.activity.second_reminder_minutes
        reminder_time = event.start_time - timedelta(minutes=reminder_minutes)

        # Allow 5 minute window
        if reminder_time <= now <= (reminder_time + timedelta(minutes=5)):
            send_second_reminder_for_event.delay(event.id)


@shared_task
def send_second_reminder_for_event(event_id):
    """
    Send second reminder emails with waiting room link.
    Also creates waiting room if it doesn't exist.

    Args:
        event_id: ID of the event
    """
    try:
        event = Event.objects.get(id=event_id)

        # Create or get waiting room
        waiting_room, created = WaitingRoom.objects.get_or_create(
            event=event,
            defaults={
                'opens_at': timezone.now(),
                'closes_at': event.start_time + timedelta(
                    minutes=event.activity.waiting_time_minutes
                ),
                'status': WaitingRoom.Status.WAITING
            }
        )

        # Build waiting room URL
        base_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:8000'
        waiting_room_url = f"{base_url}/waiting-room/{waiting_room.access_token}/"

        # Get active enrollments
        enrollments = Enrollment.objects.filter(
            event=event,
            is_active=True,
            user__email_notifications=True,
            user__is_anonymized=False
        ).select_related('user')

        for enrollment in enrollments:
            # Check if second reminder already sent
            existing = EmailNotification.objects.filter(
                enrollment=enrollment,
                notification_type=EmailNotification.NotificationType.SECOND_REMINDER
            ).first()

            if existing and existing.sent:
                continue

            # Create or get notification record
            notification, created = EmailNotification.objects.get_or_create(
                enrollment=enrollment,
                notification_type=EmailNotification.NotificationType.SECOND_REMINDER,
                defaults={
                    'recipient_email': enrollment.user.email,
                    'subject': f"¡Comienza pronto! {event.activity.title}"
                }
            )

            # Send email
            result = EmailService.send_second_reminder(
                enrollment=enrollment,
                waiting_room_url=waiting_room_url,
                notification_token=str(notification.token),
                user_timezone=enrollment.user.timezone
            )

            # Update notification record
            if result['success']:
                notification.sent = True
                notification.sent_at = timezone.now()
                notification.save()
                logger.info(f"Second reminder sent for event {event_id} to {enrollment.user.email}")
            else:
                notification.error_message = result.get('error', '')
                notification.save()
                logger.error(f"Failed to send second reminder: {result.get('error')}")

        # Update event status
        if event.status == Event.Status.SCHEDULED:
            event.status = Event.Status.NOTIFIED
            event.notification_sent = True
            event.notification_sent_at = timezone.now()
            event.save()

    except Event.DoesNotExist:
        logger.error(f"Event {event_id} not found")
    except Exception as e:
        logger.error(f"Error sending second reminder for event {event_id}: {str(e)}")


@shared_task
def send_enrollment_confirmation(enrollment_id):
    """
    Send enrollment confirmation email with calendar invitation.

    Args:
        enrollment_id: ID of the enrollment
    """
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)

        # Create notification record
        notification = EmailNotification.objects.create(
            enrollment=enrollment,
            notification_type=EmailNotification.NotificationType.ENROLLMENT_CONFIRMATION,
            recipient_email=enrollment.user.email,
            subject=f"Confirmación: {enrollment.event.activity.title}"
        )

        # Send email
        result = EmailService.send_enrollment_confirmation(
            enrollment=enrollment,
            notification_token=str(notification.token),
            user_timezone=enrollment.user.timezone
        )

        # Update notification record
        if result['success']:
            notification.sent = True
            notification.sent_at = timezone.now()
            notification.save()
            logger.info(f"Enrollment confirmation sent to {enrollment.user.email}")
        else:
            notification.error_message = result.get('error', '')
            notification.save()
            logger.error(f"Failed to send enrollment confirmation: {result.get('error')}")

    except Enrollment.DoesNotExist:
        logger.error(f"Enrollment {enrollment_id} not found")
    except Exception as e:
        logger.error(f"Error sending enrollment confirmation: {str(e)}")
