from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from config.docs import DocsTypingParameters
from config.global_permissions import IsObjectAuthor
from config.mixins import ProjectMixin
from project.models import Contributor, Project

from .permissions import WriteContributor
from .serializers import ContributorSerializer, ProjectCreateSerializer, ProjectSerializer, ProjectUpdateSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Get all Projects",
        tags=["Project"],
    ),
    retrieve=extend_schema(
        summary="Get a Project",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
    ),
    create=extend_schema(
        summary="Create a Project",
        tags=["Project"],
        request=ProjectCreateSerializer,
    ),
    update=extend_schema(
        summary="Update entirely a Project",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
        request=ProjectUpdateSerializer,
    ),
    partial_update=extend_schema(
        summary="Update one or many Project's fields",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
        request=ProjectUpdateSerializer,
    ),
    destroy=extend_schema(
        summary="Delete Project",
        tags=["Project"],
        parameters=[DocsTypingParameters.project_id.value],
    ),
)
class ProjectModelViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsObjectAuthor]
    lookup_url_kwarg = 'project_id'

    def get_serializer_class(self):
        if self.action == "create":
            return ProjectCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ProjectUpdateSerializer
        else:
            return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        return (
            Project.objects.select_related("author")
            .prefetch_related("contributors")
            .filter(Q(contributors=user) | Q(author=user))
            .distinct()
        )


@extend_schema_view(
    list=extend_schema(
        summary="Get all contributors of a Project",
        tags=["Project-Contributor"],
    ),
    retrieve=extend_schema(
        summary="Get a Project",
        tags=["Project-Contributor"],
        parameters=[
            DocsTypingParameters.contributor_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    create=extend_schema(
        summary="Create a Project",
        tags=["Project-Contributor"],
        parameters=[
            DocsTypingParameters.contributor_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    update=extend_schema(
        summary="Update entirely a Project",
        tags=["Project-Contributor"],
        parameters=[
            DocsTypingParameters.contributor_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    partial_update=extend_schema(
        summary="Update one or many Project's fields",
        tags=["Project-Contributor"],
        parameters=[
            DocsTypingParameters.contributor_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    destroy=extend_schema(
        summary="Delete Project",
        tags=["Project-Contributor"],
        parameters=[
            DocsTypingParameters.contributor_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
)
class ContributorModelViewSet(ProjectMixin, ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, WriteContributor]
    lookup_url_kwarg = 'contributor_id'

    def get_queryset(self):
        user = self.request.user

        return (
            Contributor.objects.select_related("project", "user")
            .filter(project=self.project)
            # object__attribute syntax to go through relationship
            # project__author = contributor.project.author
            .filter(Q(project__author=user) | Q(project__contributors=user))
            # avoid duplicates
            .distinct()
        )
