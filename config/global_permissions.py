from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    """
    Custom permission: only allows users to write.delete Project, Issues, and Comments if they are the author of the
    object.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
