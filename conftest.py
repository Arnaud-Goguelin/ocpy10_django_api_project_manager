import pytest

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from config.factories import CommentFactory, IssueFactory, ProjectFactory, UserFactory


# === Fixtures ===

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


@pytest.fixture
def create_project(authenticated_client, db):
    """Create a project with the authenticated user as author"""
    return ProjectFactory(author=authenticated_client.user)


@pytest.fixture
def create_issue(authenticated_client, db):
    """Create an issue for the given project"""
    return IssueFactory(author=authenticated_client.user)


@pytest.fixture
def create_comment(authenticated_client, db):
    """Create a comment for the given issue"""
    return CommentFactory(author=authenticated_client.user)
