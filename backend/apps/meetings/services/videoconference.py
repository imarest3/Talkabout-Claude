"""
Service for creating videoconferences using Google Meet or Jitsi.
"""
from django.conf import settings
from typing import Dict, Optional, List
import secrets
import hashlib
import time
import json


class VideoConferenceService:
    """
    Service to create videoconference meetings using different platforms.
    Supports Google Meet and Jitsi.
    """

    @staticmethod
    def create_meeting(
        platform: str,
        meeting_title: str,
        participants: Optional[List] = None,
        **kwargs
    ) -> Dict:
        """
        Create a videoconference meeting.

        Args:
            platform: 'GOOGLE_MEET' or 'JITSI'
            meeting_title: Title/name of the meeting
            participants: List of participant objects (optional)
            **kwargs: Additional platform-specific parameters

        Returns:
            Dictionary with:
                - success: bool
                - meeting_url: str (URL to join the meeting)
                - meeting_id: str (unique ID of the meeting)
                - platform_data: dict (additional platform-specific data)
                - error: str (if success=False)
        """
        if platform == 'GOOGLE_MEET':
            return VideoConferenceService._create_google_meet(
                meeting_title, participants, **kwargs
            )
        elif platform == 'JITSI':
            return VideoConferenceService._create_jitsi_meeting(
                meeting_title, participants, **kwargs
            )
        else:
            return {
                'success': False,
                'error': f'Unsupported platform: {platform}'
            }

    @staticmethod
    def _create_google_meet(
        meeting_title: str,
        participants: Optional[List] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Create a Google Meet conference.

        Note: This requires Google Calendar API setup.
        For now, this is a placeholder that would need Google API integration.
        """
        try:
            # TODO: Implement actual Google Meet API integration
            # This would require:
            # 1. Google Calendar API credentials
            # 2. Creating a calendar event with conferenceData
            # 3. Extracting the Meet link from the response

            # For now, return error indicating setup needed
            if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
                return {
                    'success': False,
                    'error': 'Google Meet API credentials not configured'
                }

            # Placeholder for actual implementation
            return {
                'success': False,
                'error': 'Google Meet integration not yet implemented. Please use Jitsi or implement Google API.'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating Google Meet: {str(e)}'
            }

    @staticmethod
    def _create_jitsi_meeting(
        meeting_title: str,
        participants: Optional[List] = None,
        **kwargs
    ) -> Dict:
        """
        Create a Jitsi meeting.

        Jitsi doesn't require pre-creation - meetings are created on-demand
        when someone joins the URL. We generate a unique, secure room name.
        """
        try:
            # Generate a unique room name
            # Use a combination of meeting title and random token for security
            random_token = secrets.token_urlsafe(16)
            timestamp = str(int(time.time()))

            # Create a URL-safe room name
            room_base = meeting_title.lower().replace(' ', '-')
            room_base = ''.join(c for c in room_base if c.isalnum() or c == '-')

            # Create unique room ID
            unique_string = f"{room_base}-{timestamp}-{random_token}"
            room_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16]
            room_name = f"{room_base}-{room_id}"

            # Get Jitsi domain from settings
            jitsi_domain = settings.JITSI_DOMAIN

            # Construct meeting URL
            meeting_url = f"https://{jitsi_domain}/{room_name}"

            # Additional configuration (can be passed as URL parameters)
            config_params = []

            # Set display name if provided
            if kwargs.get('user_display_name'):
                config_params.append(f"userInfo.displayName={kwargs['user_display_name']}")

            # Add config parameters to URL if any
            if config_params:
                meeting_url += "#config." + "&config.".join(config_params)

            return {
                'success': True,
                'meeting_url': meeting_url,
                'meeting_id': room_name,
                'platform_data': {
                    'domain': jitsi_domain,
                    'room_name': room_name,
                    'room_id': room_id,
                    'created_at': timestamp
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating Jitsi meeting: {str(e)}'
            }

    @staticmethod
    def get_participant_url(
        meeting_url: str,
        participant_name: str,
        platform: str = 'JITSI'
    ) -> str:
        """
        Get a personalized URL for a specific participant.

        Args:
            meeting_url: Base meeting URL
            participant_name: Name of the participant
            platform: Platform type

        Returns:
            Personalized URL for the participant
        """
        if platform == 'JITSI':
            # Add display name to URL
            if '#config' in meeting_url:
                return f"{meeting_url}&config.userInfo.displayName={participant_name}"
            else:
                return f"{meeting_url}#config.userInfo.displayName={participant_name}"
        else:
            # For other platforms, return base URL
            return meeting_url
