"""
Celery tasks for meetings.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Meeting, Attendance
from .services import UserDistributionService, VideoConferenceService
from apps.events.models import Event
from apps.activities.models import WaitingRoom, WaitingRoomJoin
from apps.enrollments.models import Enrollment
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_and_process_waiting_rooms():
    """
    Check for waiting rooms that should close and create meetings.
    Runs every minute via Celery Beat.
    """
    now = timezone.now()

    # Get waiting rooms that should close
    waiting_rooms = WaitingRoom.objects.filter(
        status=WaitingRoom.Status.WAITING,
        closes_at__lte=now
    ).select_related('event', 'event__activity')

    for waiting_room in waiting_rooms:
        process_waiting_room.delay(waiting_room.id)


@shared_task
def process_waiting_room(waiting_room_id):
    """
    Process a waiting room: distribute users and create meetings.

    Args:
        waiting_room_id: ID of the waiting room
    """
    try:
        waiting_room = WaitingRoom.objects.get(id=waiting_room_id)

        # Mark as processing
        waiting_room.status = WaitingRoom.Status.PROCESSING
        waiting_room.save()

        event = waiting_room.event
        activity = event.activity

        # Get users who joined the waiting room
        joins = WaitingRoomJoin.objects.filter(
            waiting_room=waiting_room
        ).select_related('user').values_list('user_id', flat=True)

        participant_ids = list(joins)

        if not participant_ids:
            logger.warning(f"No participants in waiting room {waiting_room_id}")
            waiting_room.status = WaitingRoom.Status.CANCELLED
            waiting_room.processed_at = timezone.now()
            waiting_room.save()
            return

        # Distribute users into groups
        groups = UserDistributionService.distribute_users(
            user_ids=participant_ids,
            max_participants=activity.max_participants_per_meeting,
            min_participants=activity.min_participants_per_meeting
        )

        if not groups:
            logger.warning(f"Could not create valid groups for waiting room {waiting_room_id}")
            waiting_room.status = WaitingRoom.Status.CANCELLED
            waiting_room.processed_at = timezone.now()
            waiting_room.save()
            return

        # Create meetings for each group
        meetings_created = []
        platform = 'JITSI'  # Default platform

        for group_index, group_user_ids in enumerate(groups):
            # Create meeting
            meeting_title = f"{activity.title} - Grupo {group_index + 1}"

            # Create videoconference
            vc_result = VideoConferenceService.create_meeting(
                platform=platform,
                meeting_title=meeting_title
            )

            if not vc_result['success']:
                logger.error(f"Failed to create videoconference: {vc_result.get('error')}")
                continue

            # Create Meeting record
            meeting = Meeting.objects.create(
                event=event,
                platform=platform,
                meeting_url=vc_result['meeting_url'],
                meeting_id=vc_result['meeting_id'],
                status=Meeting.Status.STARTED,
                max_participants=activity.max_participants_per_meeting,
                platform_data=vc_result.get('platform_data', {}),
                started_at=timezone.now()
            )

            # Add participants to meeting
            for user_id in group_user_ids:
                Attendance.objects.create(
                    user_id=user_id,
                    meeting=meeting,
                    joined_at=timezone.now()
                )

            meetings_created.append(meeting)
            logger.info(f"Created meeting {meeting.id} with {len(group_user_ids)} participants")

        # Mark waiting room as completed
        waiting_room.status = WaitingRoom.Status.COMPLETED
        waiting_room.processed_at = timezone.now()
        waiting_room.save()

        # Update event status
        event.status = Event.Status.IN_PROGRESS
        event.save()

        logger.info(f"Processed waiting room {waiting_room_id}: created {len(meetings_created)} meetings")

    except WaitingRoom.DoesNotExist:
        logger.error(f"Waiting room {waiting_room_id} not found")
    except Exception as e:
        logger.error(f"Error processing waiting room {waiting_room_id}: {str(e)}")
        # Mark as failed
        try:
            waiting_room = WaitingRoom.objects.get(id=waiting_room_id)
            waiting_room.status = WaitingRoom.Status.CANCELLED
            waiting_room.save()
        except:
            pass


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
    ).select_related('event')

    for meeting in meetings:
        meeting.status = Meeting.Status.COMPLETED
        meeting.completed_at = now
        meeting.save()
        logger.info(f"Marked meeting {meeting.id} as completed")

    # Check if all meetings for events are completed
    events = Event.objects.filter(
        status=Event.Status.IN_PROGRESS,
        end_time__lt=now
    )

    for event in events:
        # Check if all meetings are completed
        if not event.meetings.filter(status=Meeting.Status.STARTED).exists():
            event.status = Event.Status.COMPLETED
            event.save()
            logger.info(f"Marked event {event.id} as completed")


@shared_task
def cleanup_old_waiting_rooms():
    """
    Clean up old waiting rooms that were never processed.
    Runs daily via Celery Beat.
    """
    cutoff_time = timezone.now() - timedelta(days=1)

    waiting_rooms = WaitingRoom.objects.filter(
        status=WaitingRoom.Status.WAITING,
        closes_at__lt=cutoff_time
    )

    count = waiting_rooms.count()
    waiting_rooms.update(
        status=WaitingRoom.Status.CANCELLED,
        processed_at=timezone.now()
    )

    logger.info(f"Cleaned up {count} old waiting rooms")
