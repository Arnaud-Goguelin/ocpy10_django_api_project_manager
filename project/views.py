from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings

from project.models import Project
from .serializers import ProjectSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Get all Projects",
        tags=["Project"],
    ),
    retrieve=extend_schema(
        summary="Get a Project",
        tags=["Project"],
    ),
    create=extend_schema(
        summary="Create a Project",
        tags=["Project"],
    ),
    update=extend_schema(
        summary="Update entirely a Project",
        tags=["Project"],
    ),
    partial_update=extend_schema(
        summary="Update one or many Project's fields",
        tags=["Project"],
    ),
    destroy=extend_schema(
        summary="Delete Project",
        tags=["Project"],
    ),
)
class ProjectModelViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = []

    @extend_schema(
        methods=['GET'],
        summary="List all contributors of a Project",
        description="Returns the list of all users who are contributors to this Project.",
        tags=["Project Contributors"],
        )
    @extend_schema(
        methods=['POST'],
        summary="Add a contributor to a Project",
        description="Add a user as a contributor to this Project.",
        tags=["Project Contributors"],
        )
    @action(detail=True, methods=['get', 'post'], url_path='contributors')
    def contributors(self, request, pk=None):
        """
        GET: List all contributors of a project
        <br>POST: Add a contributor to a project
        <br>
        <br>**Authentification required**: Yes
        <br>**Permissions required**: None
        """
        project = self.get_object()

        if request.method == 'GET':
            return self._list_contributors(project)
        elif request.method == 'POST':
            return self._add_contributor(project, request)

    def _list_contributors(self, project):
        """Private method to handle GET logic"""
        contributors = project.contributors.all()
        from user.serializers import UserSerializer
        serializer = UserSerializer(contributors, many=True)
        return Response(serializer.data)

    def _add_contributor(self, project, request):
        """Private method to handle POST logic"""
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
                )

        from django.apps import apps
        UserModel = apps.get_model(settings.AUTH_USER_MODEL)
        user = get_object_or_404(UserModel, pk=user_id)

        if user in project.contributors.all():
            return Response(
                {"error": "User is already a contributor"},
                status=status.HTTP_400_BAD_REQUEST
                )

        project.contributors.add(user)
        return Response(
            {"message": f"User {user.username} added as contributor"},
            status=status.HTTP_201_CREATED
            )

    @extend_schema(
        methods=['DELETE'],
        summary="Pop a contributor to a Project",
        description="Remove a user from this Project's contributor.",
        tags=["Project Contributors"],
        )
    @action(detail=True, methods=['delete'], url_path='contributors/(?P<user_id>[^/.]+)')
    def remove_contributor(self, request, pk=None, user_id=None):
        """
        Remove a specific contributor from a project
        <br>
        <br>**Authentification required**: Yes
        <br>**Permissions required**: None
        """
        project = self.get_object()

        User = settings.AUTH_USER_MODEL
        from django.apps import apps
        UserModel = apps.get_model(User)
        user = get_object_or_404(UserModel, pk=user_id)

        if user not in project.contributors.all():
            return Response(
                {"error": "User is not a contributor of this project"},
                status=status.HTTP_404_NOT_FOUND
                )

        project.contributors.remove(user)
        return Response(
            {"message": f"User {user.username} removed from contributors"},
            status=status.HTTP_204_NO_CONTENT
            )
