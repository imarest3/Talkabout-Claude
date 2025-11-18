"""
Serializers for Activity models.
"""
from rest_framework import serializers
from .models import Activity, ActivityFile


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
            'id', 'title', 'description', 'created_by', 'created_by_name',
            'max_participants_per_meeting', 'min_participants_per_meeting',
            'is_active', 'files', 'event_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

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
