from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from user.models import User

from .models import Contributor, Project


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "type", "description", "author", "contributors", "created_at"]
        # add contributors to read_only_fields because they are handled in other endpoints
        read_only_fields = ["created_at", "contributors"]
        # author is optional in input, but auto-set on creation
        # this allows transfer ownership of a project to another user on PUT/PATCH request
        extra_kwargs = {"author": {"required": False}}

    def create(self, validated_data):
        # Automatically set author
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class ProjectCreateSerializer(ProjectSerializer):
    """Serializer for Project creation - author is auto-set from request.user"""

    class Meta(ProjectSerializer.Meta):
        read_only_fields = ["created_at", "contributors", "author"]


class ProjectUpdateSerializer(ProjectSerializer):
    """Serializer for Project update - allows author transfer"""

    pass  # Uses the default ProjectSerializer behavior


class ContributorSerializer(ModelSerializer):
    """Serializer for Contributor model"""

    user_id = PrimaryKeyRelatedField(
        queryset=User.objects.only("id"),
        source="user",
        write_only=True,
        help_text="ID of the user to add as contributor",
    )

    class Meta:
        model = Contributor
        fields = ["id", "user_id", "user", "project"]
        read_only_fields = ["id", "user", "project"]

    def create(self, validated_data):
        """Create a new contributor with project from view context"""
        # Get project from view (set by ProjectMixin)
        validated_data["project"] = self.context["view"].project
        return super().create(validated_data)
