"""
Google Meet integration service.
"""
from typing import Dict, List
from datetime import datetime, timedelta
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from apps.users.models import User
from apps.events.models import Event


class GoogleMeetService:
    """Service for creating Google Meet meetings."""

    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]

    @staticmethod
    def _get_calendar_service():
        """
        Get authenticated Google Calendar service.

        Note: This requires a service account credentials file.
        In production, you should store credentials securely.
        """
        try:
            # Load credentials from file or environment
            # This is a placeholder - implement actual credential loading
            credentials = service_account.Credentials.from_service_account_file(
                'credentials.json',
                scopes=GoogleMeetService.SCOPES
            )

            service = build('calendar', 'v3', credentials=credentials)
            return service
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google: {str(e)}")

    @staticmethod
    def create_meeting(
        event: Event,
        participants: List[User]
    ) -> Dict:
        """
        Create a Google Meet meeting.

        Args:
            event: The event
            participants: List of participants

        Returns:
            Dictionary with meeting data including URL
        """
        try:
            service = GoogleMeetService._get_calendar_service()

            # Create calendar event with Google Meet
            calendar_event = {
                'summary': f"{event.activity.title}",
                'description': event.activity.description,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': settings.TIME_ZONE,
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': settings.TIME_ZONE,
                },
                'attendees': [
                    {'email': participant.email}
                    for participant in participants
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"talkabout-{event.id}-{datetime.now().timestamp()}",
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }

            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=calendar_event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()

            # Extract Google Meet link
            meet_link = created_event.get('hangoutLink', '')

            return {
                'id': created_event['id'],
                'url': meet_link,
                'event_id': created_event['id'],
                'html_link': created_event.get('htmlLink', ''),
                'participants': [p.email for p in participants]
            }

        except Exception as e:
            # For development without credentials, return a placeholder
            # Remove this in production
            return GoogleMeetService._create_placeholder_meeting(event, participants)

    @staticmethod
    def _create_placeholder_meeting(event: Event, participants: List[User]) -> Dict:
        """
        Create a placeholder meeting for development.
        This should be removed in production.
        """
        placeholder_id = f"meet-{event.id}-{datetime.now().timestamp()}"
        return {
            'id': placeholder_id,
            'url': f'https://meet.google.com/{placeholder_id}',
            'event_id': placeholder_id,
            'html_link': f'https://meet.google.com/{placeholder_id}',
            'participants': [p.email for p in participants],
            'note': 'Placeholder meeting - configure Google credentials for production'
        }

    @staticmethod
    def delete_meeting(meeting_id: str) -> bool:
        """
        Delete a Google Meet meeting.

        Args:
            meeting_id: Google Calendar event ID

        Returns:
            True if successful, False otherwise
        """
        try:
            service = GoogleMeetService._get_calendar_service()
            service.events().delete(
                calendarId='primary',
                eventId=meeting_id
            ).execute()
            return True
        except Exception:
            return False
