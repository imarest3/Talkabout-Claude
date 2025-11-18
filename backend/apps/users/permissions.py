"""
Custom permissions for the Talkabout application.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsTeacher(permissions.BasePermission):
    """
    Permission to check if user is a teacher or admin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_teacher


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Permission to allow teachers to edit, but allow read-only for others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_teacher


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow owners to edit their own objects, or admins to edit any.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_admin:
            return True

        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner
        return obj.created_by == request.user


class IsActivityOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is the activity owner or an admin.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.is_admin:
            return True

        # For activities, check if user is the creator
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        # For related objects (events, etc.), check the activity
        if hasattr(obj, 'activity'):
            return obj.activity.created_by == request.user

        return False
