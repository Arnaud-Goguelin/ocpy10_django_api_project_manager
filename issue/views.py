from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import ModelViewSet

from .mixins import ProjectScopedMixin
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
class IssueModelViewSet(ProjectScopedMixin, ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = []


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

    def initial(self, request, *args, **kwargs):
        """
        Set issue from URL as an instance attribute.
        Called before every action (list, create, retrieve, etc.)
        """
        super().initial(request, *args, **kwargs)

        # Get and validate issue_id from URL
        issue_id = self.kwargs.get("issue_id")
        if issue_id:
            try:
                self.issue = Issue.objects.get(id=issue_id)
            except Issue.DoesNotExist as error:
                raise NotFound(f"Issue with id {issue_id} does not exist.") from error
        else:
            self.issue = None

    def get_queryset(self):
        """Filter comments by issue"""
        if self.issue:
            return Comment.objects.filter(issue=self.issue)
        return Comment.objects.none()

    def get_serializer_context(self):
        """Add issue to serializer context"""
        context = super().get_serializer_context()
        context["issue"] = self.issue
        return context
