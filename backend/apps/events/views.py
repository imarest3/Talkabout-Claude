"""
Views for Event models.
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Event
from .serializers import EventSerializer, EventCreateSerializer, EventListSerializer
from apps.users.permissions import IsTeacherOrReadOnly, IsActivityOwnerOrAdmin


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Event model.
    Teachers can create events for their activities.
    Students can view events.
    """
    queryset = Event.objects.all()
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activity', 'status', 'start_time']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['start_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return EventCreateSerializer
        elif self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Event.objects.select_related('activity').all()

        # Filter by activity if provided
        activity_id = self.request.query_params.get('activity_id')
        if activity_id:
            queryset = queryset.filter(activity_id=activity_id)

        # Filter upcoming events
        if self.request.query_params.get('upcoming'):
            queryset = queryset.filter(start_time__gte=timezone.now())

        # Filter past events
        if self.request.query_params.get('past'):
            queryset = queryset.filter(end_time__lt=timezone.now())

        # Admins see all events
        if user.is_admin:
            return queryset

        # Teachers see events for their activities
        if user.is_teacher:
            return queryset.filter(activity__created_by=user)

        # Students see only events for active activities
        return queryset.filter(activity__is_active=True)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsActivityOwnerOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """Get all enrollments for an event."""
        from apps.enrollments.models import Enrollment
        from apps.enrollments.serializers import EnrollmentListSerializer

        event = self.get_object()

        # Check permissions
        if not (request.user.is_admin or event.activity.created_by == request.user):
            return Response(
                {'detail': 'No tienes permiso para ver las inscripciones de este evento.'},
                status=403
            )

        enrollments = Enrollment.objects.filter(event=event, is_active=True).select_related('user')
        serializer = EnrollmentListSerializer(enrollments, many=True)
        return Response(serializer.data)
