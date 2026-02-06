from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from config.docs import DocsTypingParameters
from config.global_permissions import IsObjectAuthor, IsProjectContributor
from config.mixins import ProjectMixin

from .models import Comment, Issue
from .serializers import CommentSerializer, IssueSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Get all Issues",
        tags=["Issue"],
        parameters=[
            DocsTypingParameters.project_id.value,
            ],
    ),
    retrieve=extend_schema(
        summary="Get an Issue",
        tags=["Issue"],
        parameters=[
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    create=extend_schema(
        summary="Create an Issue",
        tags=["Issue"],
        parameters=[
            DocsTypingParameters.project_id.value,
            ],
    ),
    update=extend_schema(
        summary="Update entirely an Issue",
        tags=["Issue"],
        parameters=[
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    partial_update=extend_schema(
        summary="Update one or many Issue's fields",
        tags=["Issue"],
        parameters=[
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    destroy=extend_schema(
        summary="Delete an Issue",
        tags=["Issue"],
        parameters=[
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
)
class IssueModelViewSet(ProjectMixin, ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsObjectAuthor, IsProjectContributor]
    lookup_url_kwarg = "issue_id"

    def get_queryset(self):
        """Filter by project_id from URL"""
        return (
            Issue.objects.select_related("project", "author")
            .filter(project=self.project)
            # object__attribute syntax to go through relationship
            # project__contributors = project.contributors.user
            .filter(Q(author=self.request.user) | Q(project__contributors=self.request.user))
            # avoid duplicates
            .distinct()
        )


@extend_schema_view(
    list=extend_schema(
        summary="Get all Comments",
        tags=["Comment"],
        parameters=[
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
            ],
    ),
    retrieve=extend_schema(
        summary="Get an Comment",
        tags=["Comment"],
        parameters=[
            DocsTypingParameters.comment_id.value,
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
        ],
    ),
    create=extend_schema(
        summary="Create an Comment",
        tags=["Comment"],
        parameters=[
            DocsTypingParameters.comment_id.value,
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
        ],
    ),
    update=extend_schema(
        summary="Update entirely an Comment",
        tags=["Comment"],
        parameters=[
            DocsTypingParameters.comment_id.value,
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
        ],
    ),
    partial_update=extend_schema(
        summary="Update one or many Comment's fields",
        tags=["Comment"],
        parameters=[
            DocsTypingParameters.comment_id.value,
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
        ],
    ),
    destroy=extend_schema(
        summary="Delete an Comment",
        tags=["Comment"],
        parameters=[
            DocsTypingParameters.comment_id.value,
            DocsTypingParameters.issue_id.value,
            DocsTypingParameters.project_id.value,
        ],
    ),
)
class CommentModelViewSet(ProjectMixin, ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsObjectAuthor, IsProjectContributor]
    lookup_url_kwarg = "comment_id"

    def initial(self, request, *args, **kwargs):
        """
        Set issue from URL as an instance attribute.
        Called before every action (list, create, retrieve, etc.)
        As CommentModelViewSet is the only view to need this, it is useless to create a mixin
        """
        super().initial(request, *args, **kwargs)

        # Get and validate issue_id from URL
        issue_id = self.kwargs.get("issue_id")
        try:
            # do not forget to filter by project, to ensure the issue is part of the current project
            self.issue = Issue.objects.select_related("project", "author").get(id=issue_id, project=self.project)
        except Issue.DoesNotExist as error:
            raise NotFound(f"Issue with id {issue_id} does not exist.") from error

    def get_queryset(self):
        """Filter comments by issue"""
        # object__attribute syntax to go through relationship
        # issue__project__contributors = issue.project.contributor.user
        return (
            (
                (Comment.objects.select_related("issue", "author").filter(issue=self.issue)).filter(
                    Q(author=self.request.user) | Q(issue__project__contributors=self.request.user)
                )
            )
            # avoid duplicates
            .distinct()
        )

    def get_serializer_context(self):
        """Add issue to serializer context"""
        context = super().get_serializer_context()
        context["issue"] = self.issue
        return context
