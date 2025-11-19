"""
Serializers for Enrollment models.
"""
from rest_framework import serializers
from .models import Enrollment, EmailNotification
from apps.events.serializers import EventListSerializer
from apps.users.serializers import UserSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model."""
    user_detail = UserSerializer(source='user', read_only=True)
    event_detail = EventListSerializer(source='event', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_detail', 'event', 'event_detail',
            'is_active', 'enrolled_at', 'cancelled_at'
        ]
        read_only_fields = ['id', 'enrolled_at', 'cancelled_at']

    def validate(self, attrs):
        user = attrs.get('user')
        event = attrs.get('event')

        # Check if event allows enrollment
        if not event.can_enroll():
            raise serializers.ValidationError(
                "No se puede inscribir en este evento. El evento ya pasó o está cancelado."
            )

        # Check if user is already enrolled
        if Enrollment.objects.filter(user=user, event=event, is_active=True).exists():
            raise serializers.ValidationError(
                "Ya estás inscrito en este evento."
            )

        return attrs


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating enrollments."""

    class Meta:
        model = Enrollment
        fields = ['event']

    def validate_event(self, value):
        if not value.can_enroll():
            raise serializers.ValidationError(
                "No se puede inscribir en este evento. El evento ya pasó o está cancelado."
            )
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        event = validated_data['event']

        # Check if already enrolled
        if Enrollment.objects.filter(user=user, event=event, is_active=True).exists():
            raise serializers.ValidationError(
                "Ya estás inscrito en este evento."
            )

        enrollment = Enrollment.objects.create(user=user, event=event)
        return enrollment


class EnrollmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing enrollments."""
    event_title = serializers.CharField(source='event.activity.title', read_only=True)
    event_start_time = serializers.DateTimeField(source='event.start_time', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_name', 'event', 'event_title',
            'event_start_time', 'is_active', 'enrolled_at'
        ]


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Serializer for EmailNotification model."""
    enrollment_detail = serializers.SerializerMethodField()

    class Meta:
        model = EmailNotification
        fields = [
            'id', 'token', 'enrollment', 'enrollment_detail',
            'notification_type', 'recipient_email', 'subject',
            'sent', 'sent_at', 'error_message',
            'user_responded', 'user_response', 'responded_at',
            'created_at'
        ]
        read_only_fields = [
            'id', 'token', 'sent_at', 'responded_at', 'created_at'
        ]

    def get_enrollment_detail(self, obj):
        return {
            'user': obj.enrollment.user.get_full_name(),
            'event': str(obj.enrollment.event)
        }
