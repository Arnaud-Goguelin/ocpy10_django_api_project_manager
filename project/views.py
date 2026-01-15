from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from config.docs import project_id_parameter
from project.models import Contributor, Project

from config.global_permissions import IsAuthor
from .permissions import IsContributor
from .serializers import ContributorSerializer, ProjectSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Get all Projects",
        tags=["Project"],
        parameters=[project_id_parameter],
    ),
    retrieve=extend_schema(
        summary="Get a Project",
        tags=["Project"],
        parameters=[project_id_parameter],
    ),
    create=extend_schema(
        summary="Create a Project",
        tags=["Project"],
    ),
    update=extend_schema(
        summary="Update entirely a Project",
        tags=["Project"],
        parameters=[project_id_parameter],
    ),
    partial_update=extend_schema(
        summary="Update one or many Project's fields",
        tags=["Project"],
        parameters=[project_id_parameter],
    ),
    destroy=extend_schema(
        summary="Delete Project",
        tags=["Project"],
        parameters=[project_id_parameter],
    ),
)
class ProjectModelViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthor | IsContributor]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(Q(contributors=user) | Q(author=user)).distinct()


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
class ContributorModelViewSet(ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contributor.objects.filter(project_id=self.kwargs.get("project_id"))
