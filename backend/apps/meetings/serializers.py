"""
Serializers for Meeting models.
"""
from rest_framework import serializers
from .models import Meeting, Attendance
from apps.users.serializers import UserSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model."""
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'user_detail', 'meeting',
            'joined_at', 'left_at', 'duration'
        ]
        read_only_fields = ['id', 'joined_at', 'left_at', 'duration']


class MeetingSerializer(serializers.ModelSerializer):
    """Serializer for Meeting model."""
    attendances = AttendanceSerializer(many=True, read_only=True)
    event_title = serializers.CharField(source='event.activity.title', read_only=True)
    attendance_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'event', 'event_title', 'platform', 'meeting_url',
            'meeting_id', 'status', 'max_participants', 'platform_data',
            'error_message', 'attendances', 'attendance_count',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'meeting_url', 'meeting_id', 'platform_data',
            'created_at', 'started_at', 'completed_at'
        ]


class MeetingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing meetings."""
    event_title = serializers.CharField(source='event.activity.title', read_only=True)
    event_start_time = serializers.DateTimeField(source='event.start_time', read_only=True)
    attendance_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'event', 'event_title', 'event_start_time',
            'platform', 'meeting_url', 'status', 'max_participants',
            'attendance_count', 'created_at'
        ]
