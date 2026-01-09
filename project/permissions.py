from rest_framework import permissions

from .models import Project


class IsContributor(permissions.BasePermission):
    """
    Custom permission: only allows users to read Project, Issues, and Comments if they are contributors to the Project.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow read operations
        if request.method not in permissions.SAFE_METHODS:
            return False

        # define project depending of obj type (Project or Issue, Comment, etc.)
        if isinstance(obj, Project):
            project = obj
        elif hasattr(obj, "project"):
            # For Issue, Comment, etc.
            project = obj.project
        else:
            return False

        # Check if user is a contributor of the project
        return project.contributors.filter(id=request.user.id).exists()
