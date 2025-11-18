"""
Views for Statistics.
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Avg, Sum
from apps.activities.models import Activity
from apps.events.models import Event
from apps.enrollments.models import Enrollment
from apps.meetings.models import Meeting, Attendance
from apps.users.models import User
from apps.users.permissions import IsTeacher, IsAdmin
from .serializers import (
    ActivityStatisticsSerializer, EventStatisticsSerializer,
    UserStatisticsSerializer
)


class StatisticsViewSet(viewsets.ViewSet):
    """
    ViewSet for statistics endpoints.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def activities(self, request):
        """Get statistics for all activities."""
        # Only teachers and admins can see activity statistics
        if not (request.user.is_teacher or request.user.is_admin):
            return Response(
                {'detail': 'No tienes permiso para ver estas estadísticas.'},
                status=403
            )

        # Filter activities based on user role
        if request.user.is_admin:
            activities = Activity.objects.all()
        else:
            activities = Activity.objects.filter(created_by=request.user)

        stats = []
        for activity in activities:
            total_enrollments = Enrollment.objects.filter(
                event__activity=activity,
                is_active=True
            ).count()

            total_events = activity.events.count()
            total_meetings = Meeting.objects.filter(event__activity=activity).count()
            total_attendances = Attendance.objects.filter(
                meeting__event__activity=activity
            ).values('user').distinct().count()

            attendance_rate = (
                (total_attendances / total_enrollments * 100)
                if total_enrollments > 0 else 0
            )

            stats.append({
                'activity_id': activity.id,
                'activity_title': activity.title,
                'total_events': total_events,
                'total_enrollments': total_enrollments,
                'total_meetings': total_meetings,
                'total_attendances': total_attendances,
                'attendance_rate': round(attendance_rate, 2)
            })

        serializer = ActivityStatisticsSerializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def events(self, request):
        """Get statistics for events."""
        # Only teachers and admins can see event statistics
        if not (request.user.is_teacher or request.user.is_admin):
            return Response(
                {'detail': 'No tienes permiso para ver estas estadísticas.'},
                status=403
            )

        # Filter events based on user role
        if request.user.is_admin:
            events = Event.objects.all()
        else:
            events = Event.objects.filter(activity__created_by=request.user)

        # Filter by activity if provided
        activity_id = request.query_params.get('activity_id')
        if activity_id:
            events = events.filter(activity_id=activity_id)

        stats = []
        for event in events:
            total_enrollments = Enrollment.objects.filter(
                event=event,
                is_active=True
            ).count()

            total_meetings = event.meetings.count()
            total_attendances = Attendance.objects.filter(
                meeting__event=event
            ).values('user').distinct().count()

            attendance_rate = (
                (total_attendances / total_enrollments * 100)
                if total_enrollments > 0 else 0
            )

            stats.append({
                'event_id': event.id,
                'activity_title': event.activity.title,
                'start_time': event.start_time,
                'total_enrollments': total_enrollments,
                'total_attendances': total_attendances,
                'attendance_rate': round(attendance_rate, 2),
                'total_meetings': total_meetings
            })

        serializer = EventStatisticsSerializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def users(self, request):
        """Get statistics for users."""
        # Only admins can see all user statistics
        if not request.user.is_admin:
            return Response(
                {'detail': 'No tienes permiso para ver estas estadísticas.'},
                status=403
            )

        users = User.objects.filter(role=User.Role.STUDENT)

        stats = []
        for user in users:
            total_enrollments = Enrollment.objects.filter(user=user).count()
            active_enrollments = Enrollment.objects.filter(
                user=user,
                is_active=True
            ).count()

            attendances = Attendance.objects.filter(user=user)
            total_attendances = attendances.count()

            total_duration = attendances.aggregate(
                total=Sum('duration')
            )['total'] or 0

            attendance_rate = (
                (total_attendances / total_enrollments * 100)
                if total_enrollments > 0 else 0
            )

            stats.append({
                'user_id': user.id,
                'user_name': user.get_full_name() or user.username,
                'total_enrollments': total_enrollments,
                'active_enrollments': active_enrollments,
                'total_attendances': total_attendances,
                'attendance_rate': round(attendance_rate, 2),
                'total_duration': total_duration
            })

        serializer = UserStatisticsSerializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """Get statistics for the current user."""
        user = request.user

        total_enrollments = Enrollment.objects.filter(user=user).count()
        active_enrollments = Enrollment.objects.filter(
            user=user,
            is_active=True
        ).count()

        attendances = Attendance.objects.filter(user=user)
        total_attendances = attendances.count()

        total_duration = attendances.aggregate(
            total=Sum('duration')
        )['total'] or 0

        attendance_rate = (
            (total_attendances / total_enrollments * 100)
            if total_enrollments > 0 else 0
        )

        stats = {
            'user_id': user.id,
            'user_name': user.get_full_name() or user.username,
            'total_enrollments': total_enrollments,
            'active_enrollments': active_enrollments,
            'total_attendances': total_attendances,
            'attendance_rate': round(attendance_rate, 2),
            'total_duration': total_duration
        }

        serializer = UserStatisticsSerializer(stats)
        return Response(serializer.data)
