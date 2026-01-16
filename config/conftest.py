import pytest

from faker import Faker
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import factory

from issue.models import Issue, Comment
from project.models import Project
from user.models import User

fake = Faker()

# === Factory Models ===

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    consent = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password properly using set_password() and attach plain password"""
        if not create:
            return

        # Use extracted password if provided, otherwise generate random
        if extracted:
            password = extracted
        else:
            password = fake.password(
                length=12,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True
                )
        obj.set_password(password)
        obj.save()

        # Attach plain password to the object for easy testing
        obj.plain_password = password

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Faker("catch_phrase")
    description = factory.Faker("text", max_nb_chars=200)
    type = factory.Faker("random_element", elements=[*Project.ProjectTypes])
    # the API normally sets the author
    contributors = factory.SubFactory(UserFactory)

class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue
    title = factory.Faker("sentence")
    content = factory.Faker("text")
    status = factory.Faker("random_element", elements=[*Issue.Status])
    priority = factory.Faker("random_element", elements=[*Issue.Priority])
    tags = factory.Faker("random_element", elements=[*Issue.Tags])
    #the API normally sets the author
    project = factory.SubFactory(ProjectFactory)

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker("text")
    issue = factory.SubFactory(IssueFactory)
    #the API normally sets the author


# === Fictures ===

@pytest.fixture
def api_client():
    """Return an API client for making requests"""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, db):
    """Return an authenticated API client"""
    auth_user = UserFactory()
    refresh = RefreshToken.for_user(auth_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    # Attach user and tokens to client for easy access
    api_client.user = auth_user
    api_client.refresh_token = str(refresh)
    api_client.access_token = str(refresh.access_token)
    return api_client
