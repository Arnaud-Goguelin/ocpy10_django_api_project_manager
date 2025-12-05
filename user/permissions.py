from rest_framework import permissions


class IsUserSelf(permissions.BasePermission):
    """
    Custom permission: only allows users to access/edit their own user profile.
    Used with User model.
    """

    def has_object_permission(self, request, view, obj):
        # obj is a User instance
        return obj == request.user
