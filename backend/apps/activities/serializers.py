"""
Serializers for Activity models.
"""
from rest_framework import serializers
from .models import Activity, ActivityFile, WaitingRoom, WaitingRoomJoin


class ActivityFileSerializer(serializers.ModelSerializer):
    """Serializer for ActivityFile model."""

    class Meta:
        model = ActivityFile
        fields = ['id', 'file', 'filename', 'file_size', 'uploaded_at']
        read_only_fields = ['id', 'filename', 'file_size', 'uploaded_at']


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model."""
    files = ActivityFileSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id', 'activity_code', 'title', 'description', 'description_html',
            'created_by', 'created_by_name', 'max_participants_per_meeting',
            'min_participants_per_meeting', 'waiting_time_minutes',
            'first_reminder_hours', 'second_reminder_minutes',
            'is_active', 'files', 'event_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'activity_code', 'created_by', 'created_at', 'updated_at']

    def get_event_count(self, obj):
        return obj.events.count()

    def validate(self, attrs):
        min_participants = attrs.get('min_participants_per_meeting')
        max_participants = attrs.get('max_participants_per_meeting')

        if min_participants and max_participants:
            if min_participants > max_participants:
                raise serializers.ValidationError(
                    "El mínimo de participantes no puede ser mayor que el máximo."
                )

        return attrs


class ActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating activities."""

    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'max_participants_per_meeting',
            'min_participants_per_meeting'
        ]

    def validate(self, attrs):
        min_participants = attrs.get('min_participants_per_meeting', 2)
        max_participants = attrs.get('max_participants_per_meeting')

        if min_participants > max_participants:
            raise serializers.ValidationError(
                "El mínimo de participantes no puede ser mayor que el máximo."
            )

        return attrs


class ActivityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing activities."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'created_by_name', 'max_participants_per_meeting',
            'is_active', 'event_count', 'created_at'
        ]

    def get_event_count(self, obj):
        return obj.events.count()


class WaitingRoomSerializer(serializers.ModelSerializer):
    """Serializer for WaitingRoom model."""
    event_title = serializers.CharField(source='event.activity.title', read_only=True)
    participant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WaitingRoom
        fields = [
            'id', 'event', 'event_title', 'access_token', 'status',
            'opens_at', 'closes_at', 'participant_count', 'created_at'
        ]
        read_only_fields = ['id', 'access_token', 'created_at']


class WaitingRoomJoinSerializer(serializers.ModelSerializer):
    """Serializer for WaitingRoomJoin model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = WaitingRoomJoin
        fields = [
            'id', 'user', 'user_name', 'waiting_room', 'joined_at',
            'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'joined_at']
