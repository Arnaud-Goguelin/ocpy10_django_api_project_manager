import io
import logging
import os
import uuid

from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


logger = logging.getLogger("projects")


class Project(models.Model):

    class ProjectTypes(models.TextChoices):
        backend = "backend"
        frontend = "frontend"
        ios = "ios"
        android = "android"

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="contributed_projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(choices=ProjectTypes)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_contributors(self):
        return self.contributors.all()
