"""
Views for Activity models.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Activity, ActivityFile
from .serializers import (
    ActivitySerializer, ActivityCreateSerializer, ActivityListSerializer,
    ActivityFileSerializer
)
from apps.users.permissions import IsTeacherOrReadOnly, IsActivityOwnerOrAdmin


class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Activity model.
    Teachers can create and manage their activities.
    Students can view activities.
    """
    queryset = Activity.objects.all()
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'created_by']
    search_fields = ['title', 'description']

    def get_serializer_class(self):
        if self.action == 'create':
            return ActivityCreateSerializer
        elif self.action == 'list':
            return ActivityListSerializer
        return ActivitySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Activity.objects.all()

        # Admins see all activities
        if user.is_admin:
            return queryset

        # Teachers see their own activities
        if user.is_teacher:
            return queryset.filter(created_by=user)

        # Students see only active activities
        return queryset.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsActivityOwnerOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_file(self, request, pk=None):
        """Upload a file to an activity."""
        activity = self.get_object()

        # Check permissions
        if not (request.user.is_admin or activity.created_by == request.user):
            return Response(
                {'detail': 'No tienes permiso para subir archivos a esta actividad.'},
                status=status.HTTP_403_FORBIDDEN
            )

        file_serializer = ActivityFileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save(activity=activity)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        """List all files for an activity."""
        activity = self.get_object()
        files = activity.files.all()
        serializer = ActivityFileSerializer(files, many=True)
        return Response(serializer.data)
