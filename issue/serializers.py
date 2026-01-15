from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from user.models import User
from .models import Comment, Issue


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ["title", "content", "status", "priority", "tags", "created_at", "project", "author"]
        read_only_fields = ["author", "project", "created_at"]

    def create(self, validated_data):
        """Automatically set author and project from context"""
        validated_data["author"] = self.context["request"].user
        validated_data["project"] = self.context["view"].project
        return super().create(validated_data)


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ["title", "content", "author", "created_at"]
        read_only_fields = ["author", "issue", "created_at"]

    def create(self, validated_data):
        """Automatically set author and issue from context"""
        validated_data["author"] = self.context["request"].user
        validated_data["issue"] = self.context["issue"]
        return super().create(validated_data)
