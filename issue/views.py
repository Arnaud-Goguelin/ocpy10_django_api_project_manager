from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

from .models import Comment, Issue
from .serializers import CommentSerializer, IssueSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Get all Issues",
        tags=["Issue"],
    ),
    retrieve=extend_schema(
        summary="Get an Issue",
        tags=["Issue"],
    ),
    create=extend_schema(
        summary="Create an Issue",
        tags=["Issue"],
    ),
    update=extend_schema(
        summary="Update entirely an Issue",
        tags=["Issue"],
    ),
    partial_update=extend_schema(
        summary="Update one or many Issue's fields",
        tags=["Issue"],
    ),
    destroy=extend_schema(
        summary="Delete an Issue",
        tags=["Issue"],
    ),
)
class IssueModelViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = []

    def get_queryset(self):
        """Filter issues by project_id from URL"""
        project_id = self.kwargs.get("project_id")
        return Issue.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        """Automatically set author and project when creating an issue"""
        project_id = self.kwargs.get("project_id")
        serializer.save(author=self.request.user, project_id=project_id)


@extend_schema_view(
    list=extend_schema(
        summary="Get all Comments",
        tags=["Comment"],
    ),
    retrieve=extend_schema(
        summary="Get an Comment",
        tags=["Comment"],
    ),
    create=extend_schema(
        summary="Create an Comment",
        tags=["Comment"],
    ),
    update=extend_schema(
        summary="Update entirely an Comment",
        tags=["Comment"],
    ),
    partial_update=extend_schema(
        summary="Update one or many Comment's fields",
        tags=["Comment"],
    ),
    destroy=extend_schema(
        summary="Delete an Comment",
        tags=["Comment"],
    ),
)
class CommentModelViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = []

    def get_queryset(self):
        """Filter issues by issue_id from URL"""
        issue_id = self.kwargs.get("issue_id")
        return Comment.objects.filter(issue_id=issue_id)

    def perform_create(self, serializer):
        """Automatically set author and issue when creating a comment"""
        issue_id = self.kwargs.get("issue_id")
        serializer.save(author=self.request.user, issue_id=issue_id)
