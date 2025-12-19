import logging

from django.conf import settings
from django.db import models

from user.models import User


logger = logging.getLogger("projects")


class Project(models.Model):
    class ProjectTypes(models.TextChoices):
        backend = "backend", "Back-end"
        frontend = "frontend", "Front-end"
        ios = "ios", "iOS"
        android = "android", "Android"

    # on_delete=models.PROTECT ensure an object is not deleted
    # if a Project in DB is still referencing it
    # example: a User can be deleted only if he is not referenced by any Project
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="projects")
    contributors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="contributed_projects")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(choices=ProjectTypes)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_contributors(self):
        return self.contributors.all()

    def transfer_project_ownership(self, new_owner: "User"):
        if new_owner == self.author:
            raise ValueError("Cannot transfer project ownership to self.")

        if not new_owner:
            raise ValueError("New owner cannot be None.")

        self.author = new_owner
        self.save()
