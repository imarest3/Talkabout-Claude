"""
Service for sending email notifications with iCalendar attachments.
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from typing import Optional, Dict
from .icalendar_service import ICalendarService
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service to send email notifications for event enrollments.
    Includes iCalendar attachments compatible with Google Calendar.
    """

    @staticmethod
    def send_enrollment_confirmation(
        enrollment,
        notification_token: str,
        user_timezone: str = "UTC"
    ) -> Dict[str, any]:
        """
        Send enrollment confirmation email with calendar invitation.

        Args:
            enrollment: Enrollment object
            notification_token: Unique token for user responses
            user_timezone: User's timezone for displaying times

        Returns:
            Dictionary with success status and error message if any
        """
        try:
            event = enrollment.event
            activity = event.activity
            user = enrollment.user

            # Get base URL for response links
            base_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:8000'

            # Build context for email template
            context = {
                'user_name': user.get_full_name() or user.username,
                'activity_title': activity.title,
                'activity_description': activity.description,
                'event_start_time': event.start_time,
                'event_end_time': event.end_time,
                'user_timezone': user_timezone,
                'accept_url': f"{base_url}/api/notifications/{notification_token}/accept/",
                'decline_url': f"{base_url}/api/notifications/{notification_token}/decline/",
                'tentative_url': f"{base_url}/api/notifications/{notification_token}/tentative/",
                'unsubscribe_url': f"{base_url}/api/notifications/{notification_token}/unsubscribe/",
            }

            # Render email templates
            subject = f"Confirmación: {activity.title}"
            text_content = render_to_string('emails/enrollment_confirmation.txt', context)
            html_content = render_to_string('emails/enrollment_confirmation.html', context)

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")

            # Generate iCalendar attachment
            ics_content = ICalendarService.generate_ics(
                summary=activity.title,
                description=activity.description,
                start_time=event.start_time,
                end_time=event.end_time,
                organizer_email=settings.DEFAULT_FROM_EMAIL,
                organizer_name="Talkabout",
                attendee_email=user.email,
                attendee_name=user.get_full_name() or user.username,
                uid=f"event-{event.id}@talkabout",
                timezone=user_timezone
            )

            # Attach iCalendar file
            email.attach('event.ics', ics_content, 'text/calendar')

            # Send email
            email.send()

            return {
                'success': True,
                'message': 'Enrollment confirmation sent successfully'
            }

        except Exception as e:
            logger.error(f"Error sending enrollment confirmation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def send_first_reminder(
        enrollment,
        notification_token: str,
        user_timezone: str = "UTC"
    ) -> Dict[str, any]:
        """
        Send first reminder email (24 hours before event).

        Args:
            enrollment: Enrollment object
            notification_token: Unique token for user responses
            user_timezone: User's timezone

        Returns:
            Dictionary with success status
        """
        try:
            event = enrollment.event
            activity = event.activity
            user = enrollment.user

            base_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:8000'

            context = {
                'user_name': user.get_full_name() or user.username,
                'activity_title': activity.title,
                'event_start_time': event.start_time,
                'user_timezone': user_timezone,
                'decline_url': f"{base_url}/api/notifications/{notification_token}/decline/",
                'unsubscribe_url': f"{base_url}/api/notifications/{notification_token}/unsubscribe/",
            }

            subject = f"Recordatorio: {activity.title} - Mañana"
            text_content = render_to_string('emails/first_reminder.txt', context)
            html_content = render_to_string('emails/first_reminder.html', context)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return {'success': True}

        except Exception as e:
            logger.error(f"Error sending first reminder: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def send_second_reminder(
        enrollment,
        waiting_room_url: str,
        notification_token: str,
        user_timezone: str = "UTC"
    ) -> Dict[str, any]:
        """
        Send second reminder email with waiting room link (5 minutes before event).

        Args:
            enrollment: Enrollment object
            waiting_room_url: URL to join the waiting room
            notification_token: Unique token for user responses
            user_timezone: User's timezone

        Returns:
            Dictionary with success status
        """
        try:
            event = enrollment.event
            activity = event.activity
            user = enrollment.user

            context = {
                'user_name': user.get_full_name() or user.username,
                'activity_title': activity.title,
                'event_start_time': event.start_time,
                'waiting_room_url': waiting_room_url,
                'user_timezone': user_timezone,
            }

            subject = f"¡Comienza pronto! {activity.title}"
            text_content = render_to_string('emails/second_reminder.txt', context)
            html_content = render_to_string('emails/second_reminder.html', context)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return {'success': True}

        except Exception as e:
            logger.error(f"Error sending second reminder: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def send_cancellation(
        enrollment,
        notification_token: str,
        user_timezone: str = "UTC"
    ) -> Dict[str, any]:
        """
        Send cancellation email.

        Args:
            enrollment: Enrollment object
            notification_token: Unique token
            user_timezone: User's timezone

        Returns:
            Dictionary with success status
        """
        try:
            event = enrollment.event
            activity = event.activity
            user = enrollment.user

            context = {
                'user_name': user.get_full_name() or user.username,
                'activity_title': activity.title,
                'event_start_time': event.start_time,
                'user_timezone': user_timezone,
            }

            subject = f"Cancelación: {activity.title}"
            text_content = render_to_string('emails/cancellation.txt', context)
            html_content = render_to_string('emails/cancellation.html', context)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")

            # Generate cancellation iCalendar
            ics_content = ICalendarService.generate_cancellation_ics(
                summary=activity.title,
                start_time=event.start_time,
                end_time=event.end_time,
                uid=f"event-{event.id}@talkabout",
                organizer_email=settings.DEFAULT_FROM_EMAIL,
                organizer_name="Talkabout",
                attendee_email=user.email,
                timezone=user_timezone
            )

            email.attach('cancellation.ics', ics_content, 'text/calendar')
            email.send()

            return {'success': True}

        except Exception as e:
            logger.error(f"Error sending cancellation: {str(e)}")
            return {'success': False, 'error': str(e)}
