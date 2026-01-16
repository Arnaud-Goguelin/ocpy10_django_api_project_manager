import pytest

from django.contrib.auth import get_user_model
from faker import Faker
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()
fake = Faker()


@pytest.fixture
def api_client():
    """Return an API client for making requests"""
    return APIClient()


@pytest.fixture
def user_factory(db):
    """Factory to create multiple users"""
    def make_user(**kwargs):
        defaults = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": "TestPass123!@#",
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80),
            "consent": True,
        }
        defaults.update(kwargs)
        password = defaults.pop("password")
        user = User.objects.create_user(password=password, **defaults)
        # attach plain password to user for easy access in test
        user.plain_password = password
        return user
    return make_user


@pytest.fixture
def create_user(user_factory):
    """Create and return a test user with random data"""
    return user_factory()


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client"""
    refresh = RefreshToken.for_user(create_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    # Attach user and tokens to client for easy access
    api_client.user = create_user
    api_client.refresh_token = str(refresh)
    api_client.access_token = str(refresh.access_token)
    return api_client
