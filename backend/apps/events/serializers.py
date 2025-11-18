"""
Serializers for Event models.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Event
from apps.activities.serializers import ActivityListSerializer


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    activity_detail = ActivityListSerializer(source='activity', read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    attended_count = serializers.IntegerField(read_only=True)
    can_enroll = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'activity', 'activity_detail', 'start_time', 'end_time',
            'status', 'notification_sent', 'notification_sent_at',
            'enrolled_count', 'attended_count', 'can_enroll',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'notification_sent', 'notification_sent_at',
            'created_at', 'updated_at'
        ]

    def get_can_enroll(self, obj):
        return obj.can_enroll()

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError(
                    "La hora de fin debe ser posterior a la hora de inicio."
                )

            if start_time < timezone.now():
                raise serializers.ValidationError(
                    "La hora de inicio no puede estar en el pasado."
                )

        return attrs


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events."""

    class Meta:
        model = Event
        fields = ['activity', 'start_time', 'end_time']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if end_time <= start_time:
            raise serializers.ValidationError(
                "La hora de fin debe ser posterior a la hora de inicio."
            )

        if start_time < timezone.now():
            raise serializers.ValidationError(
                "La hora de inicio no puede estar en el pasado."
            )

        return attrs


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing events."""
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    can_enroll = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'activity', 'activity_title', 'start_time', 'end_time',
            'status', 'enrolled_count', 'can_enroll'
        ]

    def get_can_enroll(self, obj):
        return obj.can_enroll()
