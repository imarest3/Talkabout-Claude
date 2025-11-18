"""
Views for Meeting models.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Meeting, Attendance
from .serializers import MeetingSerializer, MeetingListSerializer, AttendanceSerializer
from apps.users.permissions import IsAdmin


class MeetingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Meeting model.
    Meetings are created automatically by the system.
    Teachers and admins can view meetings for their events.
    """
    queryset = Meeting.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'platform', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return MeetingListSerializer
        return MeetingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Meeting.objects.select_related('event', 'event__activity').all()

        # Admins see all meetings
        if user.is_admin:
            return queryset

        # Teachers see meetings for their activities
        if user.is_teacher:
            return queryset.filter(event__activity__created_by=user)

        # Students see meetings they're enrolled in
        from apps.enrollments.models import Enrollment
        enrolled_event_ids = Enrollment.objects.filter(
            user=user,
            is_active=True
        ).values_list('event_id', flat=True)

        return queryset.filter(event_id__in=enrolled_event_ids)

    def create(self, request, *args, **kwargs):
        """Prevent manual creation of meetings."""
        return Response(
            {'detail': 'Las reuniones son creadas automáticamente por el sistema.'},
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        """Only admins can delete meetings."""
        if not request.user.is_admin:
            return Response(
                {'detail': 'Solo los administradores pueden eliminar reuniones.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Record user joining a meeting."""
        meeting = self.get_object()

        # Check if user is enrolled in the event
        from apps.enrollments.models import Enrollment
        if not Enrollment.objects.filter(
            user=request.user,
            event=meeting.event,
            is_active=True
        ).exists():
            return Response(
                {'detail': 'Debes estar inscrito en el evento para unirte a la reunión.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create or get attendance record
        attendance, created = Attendance.objects.get_or_create(
            user=request.user,
            meeting=meeting
        )

        if not created:
            return Response(
                {'detail': 'Ya te has unido a esta reunión.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Record user leaving a meeting."""
        meeting = self.get_object()

        try:
            attendance = Attendance.objects.get(
                user=request.user,
                meeting=meeting
            )
        except Attendance.DoesNotExist:
            return Response(
                {'detail': 'No te has unido a esta reunión.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attendance.left_at:
            return Response(
                {'detail': 'Ya has salido de esta reunión.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.utils import timezone
        attendance.left_at = timezone.now()
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
