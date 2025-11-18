"""
Jitsi Meet integration service.
"""
import hashlib
import time
import jwt
from typing import Dict, List
from django.conf import settings
from apps.users.models import User
from apps.events.models import Event


class JitsiService:
    """Service for creating Jitsi meetings."""

    @staticmethod
    def create_meeting(
        event: Event,
        meeting_id: int,
        participants: List[User]
    ) -> Dict:
        """
        Create a Jitsi meeting.

        Args:
            event: The event
            meeting_id: Database meeting ID
            participants: List of participants

        Returns:
            Dictionary with meeting data including URL
        """
        # Generate a unique room name
        room_name = f"talkabout-{event.id}-meeting-{meeting_id}"

        # Jitsi domain
        domain = settings.JITSI_DOMAIN

        # Create meeting URL
        meeting_url = f"https://{domain}/{room_name}"

        # If Jitsi JWT is configured, generate a token
        token = None
        if settings.JITSI_APP_ID and settings.JITSI_APP_SECRET:
            token = JitsiService._generate_jwt_token(
                room_name=room_name,
                user_name=event.activity.created_by.get_full_name(),
                user_email=event.activity.created_by.email,
                moderator=True
            )
            meeting_url += f"?jwt={token}"

        return {
            'id': room_name,
            'url': meeting_url,
            'room_name': room_name,
            'domain': domain,
            'jwt_token': token,
            'participants': [p.email for p in participants]
        }

    @staticmethod
    def _generate_jwt_token(
        room_name: str,
        user_name: str,
        user_email: str,
        moderator: bool = False
    ) -> str:
        """
        Generate a JWT token for Jitsi authentication.

        Args:
            room_name: Name of the room
            user_name: User's display name
            user_email: User's email
            moderator: Whether user is a moderator

        Returns:
            JWT token string
        """
        payload = {
            'iss': settings.JITSI_APP_ID,
            'aud': settings.JITSI_APP_ID,
            'sub': settings.JITSI_DOMAIN,
            'room': room_name,
            'iat': int(time.time()),
            'exp': int(time.time()) + 7200,  # 2 hours
            'context': {
                'user': {
                    'name': user_name,
                    'email': user_email,
                    'moderator': str(moderator).lower()
                }
            }
        }

        token = jwt.encode(
            payload,
            settings.JITSI_APP_SECRET,
            algorithm='HS256'
        )

        return token

    @staticmethod
    def generate_participant_token(
        room_name: str,
        user: User
    ) -> str:
        """
        Generate a JWT token for a participant.

        Args:
            room_name: Name of the room
            user: User object

        Returns:
            JWT token string
        """
        return JitsiService._generate_jwt_token(
            room_name=room_name,
            user_name=user.get_full_name() or user.username,
            user_email=user.email,
            moderator=False
        )
