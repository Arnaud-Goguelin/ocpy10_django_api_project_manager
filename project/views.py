from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from config.docs import DocsTypingParameters
from config.global_permissions import IsAuthor
from config.mixins import ProjectMixin
from project.models import Contributor, Project

from .permissions import IsContributor
from .serializers import ContributorSerializer, ProjectSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Get all Projects",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
    ),
    retrieve=extend_schema(
        summary="Get a Project",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
    ),
    create=extend_schema(
        summary="Create a Project",
        tags=["Project"],
    ),
    update=extend_schema(
        summary="Update entirely a Project",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
    ),
    partial_update=extend_schema(
        summary="Update one or many Project's fields",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
    ),
    destroy=extend_schema(
        summary="Delete Project",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
    ),
)
class ProjectModelViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthor | IsContributor]

    def get_queryset(self):
        user = self.request.user
        return (
            Project.objects
            .select_related("author")
            .prefetch_related("contributors")
            .filter(Q(contributors=user) | Q(author=user)).distinct()
        )


@extend_schema_view(
    list=extend_schema(
        summary="Get all contributors of a Project",
        tags=["Project-Contributor"],
    ),
    retrieve=extend_schema(
        summary="Get a Project",
        tags=["Project-Contributor"],
    ),
    create=extend_schema(
        summary="Create a Project",
        tags=["Project-Contributor"],
    ),
    update=extend_schema(
        summary="Update entirely a Project",
        tags=["Project-Contributor"],
    ),
    partial_update=extend_schema(
        summary="Update one or many Project's fields",
        tags=["Project-Contributor"],
    ),
    destroy=extend_schema(
        summary="Delete Project",
        tags=["Project-Contributor"],
    ),
)
class ContributorModelViewSet(ProjectMixin, ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Contributor.objects
            .select_related("project", "user")
            .filter(project=self.project)
        )
