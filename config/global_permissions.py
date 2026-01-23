from rest_framework import permissions


class IsObjectAuthor(permissions.BasePermission):
    """
    Custom permission: only allows users to write.delete Project, Issues, and Comments if they are the author of the
    object.
    """

    # no overwrite has_permission as this one rules safe methods only on request
    # to read only an object, only authenticated user is required
    # yet views filters objects by user_id
    # so it is not a question of permissions, but of views filtering

    # Nevertheless, for write methods, only the author can modify the object
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "author"):
            return obj.author == request.user
        else:
            # if object has no author attribute, it is not concerned by this permission
            # example: Contributor object has no author attribute
            return True
