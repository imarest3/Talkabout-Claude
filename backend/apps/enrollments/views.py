"""
Views for Enrollment models.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Enrollment
from .serializers import (
    EnrollmentSerializer, EnrollmentCreateSerializer, EnrollmentListSerializer
)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Enrollment model.
    Students can enroll and unenroll from events.
    Teachers can view enrollments for their activities.
    """
    queryset = Enrollment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event', 'is_active']
    ordering_fields = ['enrolled_at']
    ordering = ['-enrolled_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return EnrollmentCreateSerializer
        elif self.action == 'list':
            return EnrollmentListSerializer
        return EnrollmentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.select_related('user', 'event', 'event__activity').all()

        # Admins see all enrollments
        if user.is_admin:
            return queryset

        # Teachers see enrollments for their activities
        if user.is_teacher:
            return queryset.filter(event__activity__created_by=user)

        # Students see only their own enrollments
        return queryset.filter(user=user)

    def create(self, request, *args, **kwargs):
        """Create a new enrollment for the current user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an enrollment."""
        enrollment = self.get_object()

        # Check permissions
        if not (request.user.is_admin or enrollment.user == request.user):
            return Response(
                {'detail': 'No tienes permiso para cancelar esta inscripción.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if event hasn't started yet
        if enrollment.event.start_time < timezone.now():
            return Response(
                {'detail': 'No puedes cancelar una inscripción después de que el evento haya comenzado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment.cancel()
        return Response(
            {'detail': 'Inscripción cancelada exitosamente.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def my_enrollments(self, request):
        """Get current user's enrollments."""
        enrollments = Enrollment.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('event', 'event__activity')

        # Filter upcoming
        if request.query_params.get('upcoming'):
            enrollments = enrollments.filter(event__start_time__gte=timezone.now())

        serializer = EnrollmentListSerializer(enrollments, many=True)
        return Response(serializer.data)
