from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from config.docs import project_id_parameter, issue_id_parameter, comment_id_parameter
from project.models import Project
from config.global_permissions import IsAuthor
from project.permissions import IsContributor
from .models import Comment, Issue
from .serializers import CommentSerializer, IssueSerializer




@extend_schema_view(
    list=extend_schema(
        summary="Get all Issues",
        tags=["Issue"],
        parameters=[project_id_parameter, issue_id_parameter],
    ),
    retrieve=extend_schema(
        summary="Get an Issue",
        tags=["Issue"],
        parameters=[project_id_parameter, issue_id_parameter],
    ),
    create=extend_schema(
        summary="Create an Issue",
        tags=["Issue"],
        parameters=[project_id_parameter],
    ),
    update=extend_schema(
        summary="Update entirely an Issue",
        tags=["Issue"],
        parameters=[project_id_parameter, issue_id_parameter],
    ),
    partial_update=extend_schema(
        summary="Update one or many Issue's fields",
        tags=["Issue"],
        parameters=[project_id_parameter, issue_id_parameter],
    ),
    destroy=extend_schema(
        summary="Delete an Issue",
        tags=["Issue"],
        parameters=[project_id_parameter, issue_id_parameter],
    ),
)
class IssueModelViewSet(ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsAuthor | IsContributor]

    def initial(self, request, *args, **kwargs):
        self.project =Project.object.get(id=self.kwargs.get("project_id"))
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        """Filter by project_id from URL"""
        return Issue.objects.filter(project=self.project)

    def get_serializer_context(self):
        """Add project_id to serializer context"""
        context = super().get_serializer_context()
        context["project_id"] = self.kwargs.get("project_id")
        return context


@extend_schema_view(
    list=extend_schema(
        summary="Get all Comments",
        tags=["Comment"],
        parameters=[project_id_parameter, issue_id_parameter],
    ),
    retrieve=extend_schema(
        summary="Get an Comment",
        tags=["Comment"],
        parameters=[project_id_parameter, issue_id_parameter, comment_id_parameter],
    ),
    create=extend_schema(
        summary="Create an Comment",
        tags=["Comment"],
        parameters=[project_id_parameter, issue_id_parameter],
    ),
    update=extend_schema(
        summary="Update entirely an Comment",
        tags=["Comment"],
        parameters=[project_id_parameter, issue_id_parameter, comment_id_parameter],
    ),
    partial_update=extend_schema(
        summary="Update one or many Comment's fields",
        tags=["Comment"],
        parameters=[project_id_parameter, issue_id_parameter, comment_id_parameter],
    ),
    destroy=extend_schema(
        summary="Delete an Comment",
        tags=["Comment"],
        parameters=[project_id_parameter, issue_id_parameter, comment_id_parameter],
    ),
)
class CommentModelViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthor | IsContributor]

    def initial(self, request, *args, **kwargs):
        """
        Set issue from URL as an instance attribute.
        Called before every action (list, create, retrieve, etc.)
        """
        super().initial(request, *args, **kwargs)

        # Get and validate issue_id from URL
        issue_id = self.kwargs.get("issue_id")
        project_id = self.kwargs.get("project_id")
        try:
            # do not forget to filter by project_id, to ensure issue is part of the project
            self.issue = Issue.objects.get(id=issue_id, project_id=project_id)
            self.project = self.issue.project
        except Issue.DoesNotExist as error:
            raise NotFound(f"Issue with id {issue_id} does not exist.") from error

    def get_queryset(self):
        """Filter comments by issue"""
        return Comment.objects.filter(issue=self.issue)

    def get_serializer_context(self):
        """Add issue to serializer context"""
        context = super().get_serializer_context()
        context["issue"] = self.issue
        return context
