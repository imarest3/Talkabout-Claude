"""
Serializers for Statistics.
"""
from rest_framework import serializers


class ActivityStatisticsSerializer(serializers.Serializer):
    """Serializer for activity statistics."""
    activity_id = serializers.IntegerField()
    activity_title = serializers.CharField()
    total_events = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    total_meetings = serializers.IntegerField()
    total_attendances = serializers.IntegerField()
    attendance_rate = serializers.FloatField()


class EventStatisticsSerializer(serializers.Serializer):
    """Serializer for event statistics."""
    event_id = serializers.IntegerField()
    activity_title = serializers.CharField()
    start_time = serializers.DateTimeField()
    total_enrollments = serializers.IntegerField()
    total_attendances = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    total_meetings = serializers.IntegerField()


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics."""
    user_id = serializers.IntegerField()
    user_name = serializers.CharField()
    total_enrollments = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    total_attendances = serializers.IntegerField()
    attendance_rate = serializers.FloatField()
    total_duration = serializers.IntegerField()  # in seconds
