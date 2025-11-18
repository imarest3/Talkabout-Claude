"""
Service layer for meeting creation and participant distribution.
"""
import random
import math
from typing import List, Tuple
from django.conf import settings
from .models import Meeting
from apps.events.models import Event
from apps.enrollments.models import Enrollment
from apps.users.models import User


class MeetingService:
    """Service for creating and managing meetings."""

    @staticmethod
    def divide_participants(
        participants: List[User],
        min_participants: int,
        max_participants: int
    ) -> List[List[User]]:
        """
        Divide participants into groups for meetings.

        Args:
            participants: List of users to divide
            min_participants: Minimum number of participants per meeting
            max_participants: Maximum number of participants per meeting

        Returns:
            List of participant groups
        """
        total_participants = len(participants)

        # Not enough participants
        if total_participants < min_participants:
            return []

        # Calculate optimal number of groups
        num_groups = math.ceil(total_participants / max_participants)

        # Ensure each group has at least min_participants
        while num_groups > 1:
            avg_participants = total_participants / num_groups
            if avg_participants >= min_participants:
                break
            num_groups -= 1

        # If we can't form valid groups, return empty
        if num_groups < 1:
            return []

        # Shuffle participants for random distribution
        shuffled_participants = participants.copy()
        random.shuffle(shuffled_participants)

        # Distribute participants evenly
        groups = []
        participants_per_group = total_participants // num_groups
        remainder = total_participants % num_groups

        start_idx = 0
        for i in range(num_groups):
            # Add one extra participant to the first 'remainder' groups
            group_size = participants_per_group + (1 if i < remainder else 0)
            end_idx = start_idx + group_size
            groups.append(shuffled_participants[start_idx:end_idx])
            start_idx = end_idx

        return groups

    @staticmethod
    def create_meetings_for_event(
        event: Event,
        platform: str = Meeting.Platform.JITSI
    ) -> List[Meeting]:
        """
        Create meetings for an event based on enrolled participants.

        Args:
            event: The event to create meetings for
            platform: Platform to use (JITSI or GOOGLE_MEET)

        Returns:
            List of created meetings
        """
        from .integrations.jitsi import JitsiService
        from .integrations.google_meet import GoogleMeetService

        # Get active enrollments
        enrollments = Enrollment.objects.filter(
            event=event,
            is_active=True
        ).select_related('user')

        participants = [enrollment.user for enrollment in enrollments]

        if not participants:
            return []

        # Get participant limits from activity
        min_participants = event.activity.min_participants_per_meeting
        max_participants = event.activity.max_participants_per_meeting

        # Divide participants into groups
        groups = MeetingService.divide_participants(
            participants,
            min_participants,
            max_participants
        )

        if not groups:
            return []

        # Create meetings for each group
        meetings = []
        for idx, group in enumerate(groups):
            meeting = Meeting.objects.create(
                event=event,
                platform=platform,
                max_participants=len(group),
                status=Meeting.Status.SCHEDULED
            )

            # Create meeting on the platform
            try:
                if platform == Meeting.Platform.JITSI:
                    meeting_data = JitsiService.create_meeting(
                        event=event,
                        meeting_id=meeting.id,
                        participants=group
                    )
                else:  # GOOGLE_MEET
                    meeting_data = GoogleMeetService.create_meeting(
                        event=event,
                        participants=group
                    )

                meeting.meeting_url = meeting_data.get('url', '')
                meeting.meeting_id = meeting_data.get('id', '')
                meeting.platform_data = meeting_data
                meeting.status = Meeting.Status.STARTED
                meeting.save()

                meetings.append(meeting)

            except Exception as e:
                meeting.status = Meeting.Status.FAILED
                meeting.error_message = str(e)
                meeting.save()

        return meetings

    @staticmethod
    def get_meeting_for_user(event: Event, user: User) -> Meeting:
        """
        Get the meeting assigned to a user for a specific event.

        Args:
            event: The event
            user: The user

        Returns:
            Meeting object or None
        """
        # Check if user is enrolled
        if not Enrollment.objects.filter(
            event=event,
            user=user,
            is_active=True
        ).exists():
            return None

        # Find meeting where user is a participant
        meetings = event.meetings.filter(status=Meeting.Status.STARTED)

        for meeting in meetings:
            # Check if user should be in this meeting
            # This is a simplified version - in production you'd want to
            # store the participant assignments
            if user in meeting.participants.all():
                return meeting

        return None
