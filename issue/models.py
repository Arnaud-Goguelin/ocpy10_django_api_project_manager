import logging

from django.conf import settings
from django.db import models

from project.models import Project


logger = logging.getLogger("issues")


class Issue(models.Model):
    class Status(models.TextChoices):
        todo = "todo", "To Do"
        in_progress = "in_progress", "In Progress"
        closed = "closed", "Closed"

    class Priority(models.TextChoices):
        low = "low", "Low"
        medium = "medium", "Medium"
        high = "high", "High"
        urgent = "urgent", "Urgent"

    class Tags(models.TextChoices):
        bug = "bug", "Bug"
        feature = "feature", "Feature"
        improvement = "improvement", "Improvement"

    # If User/Author is deleted, do not delete the issue to preserve history
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    # If Project is deleted, delete issue too (issue cannot exist without a project)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="issues")
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    status = models.CharField(choices=Status, default=Status.todo)
    priority = models.CharField(choices=Priority, default=Priority.low)
    tags = models.CharField(choices=Tags, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    issue = models.ForeignKey(to=Issue, on_delete=models.CASCADE, related_name="comments")
    # If User/Author is deleted, do not delete the comment to preserve history
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
