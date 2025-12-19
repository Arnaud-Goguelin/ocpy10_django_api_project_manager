from rest_framework.serializers import IntegerField, ModelSerializer, Serializer

from .models import Project


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ["name", "type", "description", "author", "contributors", "created_at"]


class ContributorSerializer(Serializer):
    """Serializer for adding a contributor to a project"""

    user_id = IntegerField(required=True, help_text="ID of the user to add as contributor")
