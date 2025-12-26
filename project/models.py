import logging

from django.conf import settings
from django.db import models

from user.models import User


logger = logging.getLogger("projects")


class Contributor(models.Model):
    class ContributorRoles(models.TextChoices):
        admin = "admin", "Admin"
        contributor = "contributor", "Contributor"

    # TODO: on_delete=models.CASCADE ??? pas on_delete=models.Contributor
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey("project.Project", on_delete=models.CASCADE)
    role = models.CharField(choices=ContributorRoles)
    pass


class Project(models.Model):
    class ProjectTypes(models.TextChoices):
        backend = "backend", "Back-end"
        frontend = "frontend", "Front-end"
        ios = "ios", "iOS"
        android = "android", "Android"

    # on_delete=models.PROTECT ensure an object is not deleted
    # if a Project in DB is still referencing it
    # example: a User can be deleted only if he is not referenced by any Project
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="projects")
    contributors = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL, through=Contributor, related_name="contributed_projects"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type = models.CharField(choices=ProjectTypes)
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: delete useless property
    @property
    def get_contributors(self):
        return self.contributors.all()

    # TODO: already done in patch ?
    def transfer_project_ownership(self, new_owner: "User"):
        if new_owner == self.author:
            raise ValueError("Cannot transfer project ownership to self.")

        if not new_owner:
            raise ValueError("New owner cannot be None.")

        self.author = new_owner
        self.save()
