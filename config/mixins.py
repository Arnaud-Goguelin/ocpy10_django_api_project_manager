from rest_framework.exceptions import NotFound

from project.models import Project


class ProjectMixin:
    """
    Mixin to automatically fetch and set the project from URL kwargs.
    Sets self.project for use in permissions and queryset filtering.
    """

    project = None

    def initial(self, request, *args, **kwargs):
        """
        Set project from URL as an instance attribute.
        Called before every action (list, create, retrieve, etc.)
        """
        # Get and validate project_id from URL
        project_id = self.kwargs.get("project_id")

        if project_id:
            try:
                self.project = Project.objects.get(id=project_id)
            except Project.DoesNotExist as error:
                raise NotFound(f"Project with id {project_id} does not exist.") from error

        # once self.project is set, call super to proceed with view initialization and permissions
        super().initial(request, *args, **kwargs)
