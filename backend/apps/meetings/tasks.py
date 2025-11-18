"""
Celery tasks for meetings.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from .models import Meeting
from .services import MeetingService
from apps.events.models import Event
from apps.enrollments.models import Enrollment


@shared_task
def start_scheduled_meetings():
    """
    Check for events that should start now and create meetings.
    Runs every minute via Celery Beat.
    """
    now = timezone.now()
    start_window = now + timedelta(seconds=settings.MEETING_START_CHECK_INTERVAL)

    # Get events that should start soon and haven't been processed
    events = Event.objects.filter(
        status__in=[Event.Status.SCHEDULED, Event.Status.NOTIFIED],
        start_time__lte=start_window,
        start_time__gte=now
    )

    for event in events:
        # Check if meetings already created
        if event.meetings.exists():
            continue

        create_meetings_for_event.delay(event.id)


@shared_task
def create_meetings_for_event(event_id, platform='JITSI'):
    """
    Create meetings for an event and notify participants.

    Args:
        event_id: ID of the event
        platform: Platform to use (JITSI or GOOGLE_MEET)
    """
    try:
        event = Event.objects.get(id=event_id)

        # Update event status
        event.status = Event.Status.IN_PROGRESS
        event.save()

        # Create meetings
        meetings = MeetingService.create_meetings_for_event(
            event=event,
            platform=platform
        )

        if not meetings:
            # No meetings created (not enough participants)
            return

        # Send meeting links to participants
        for meeting in meetings:
            send_meeting_link_to_participants.delay(meeting.id)

    except Event.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error creating meetings for event {event_id}: {str(e)}")


@shared_task
def send_meeting_link_to_participants(meeting_id):
    """
    Send meeting link to all participants.

    Args:
        meeting_id: ID of the meeting
    """
    try:
        meeting = Meeting.objects.get(id=meeting_id)

        # Get participants who are enrolled and want notifications
        enrollments = Enrollment.objects.filter(
            event=meeting.event,
            is_active=True,
            user__email_notifications=True
        ).select_related('user')

        # In a real implementation, you'd want to assign specific users to specific meetings
        # For now, we'll send the link to all enrolled users
        recipients = [enrollment.user.email for enrollment in enrollments]

        if not recipients:
            return

        subject = f"¡Tu reunión está lista! - {meeting.event.activity.title}"

        message = f"""
Hola,

Tu reunión de conversación está lista:

Actividad: {meeting.event.activity.title}
Hora de inicio: {meeting.event.start_time.strftime('%d/%m/%Y a las %H:%M')}
Plataforma: {meeting.get_platform_display()}

Enlace a la reunión:
{meeting.meeting_url}

Haz clic en el enlace para unirte a la videoconferencia.

¡Disfruta de la conversación!

Equipo de Talkabout
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

    except Meeting.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error sending meeting link for meeting {meeting_id}: {str(e)}")


@shared_task
def complete_finished_meetings():
    """
    Mark meetings as completed after their end time.
    Runs periodically via Celery Beat.
    """
    now = timezone.now()

    meetings = Meeting.objects.filter(
        status=Meeting.Status.STARTED,
        event__end_time__lt=now
    )

    for meeting in meetings:
        meeting.status = Meeting.Status.COMPLETED
        meeting.completed_at = now
        meeting.save()

        # Update event status
        event = meeting.event
        if event.meetings.filter(status=Meeting.Status.STARTED).count() == 0:
            event.status = Event.Status.COMPLETED
            event.save()
