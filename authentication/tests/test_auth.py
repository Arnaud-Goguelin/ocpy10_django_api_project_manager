import pytest

from django.urls import reverse
from rest_framework import status

from config.conftest import fake, UserFactory, authenticated_client, api_client


base_auth_url = "auth:"


@pytest.mark.django_db
class TestTokenObtainPair:
    """Tests for login endpoint (JWT token obtain)"""

    def test_login_success(self, api_client):
        test_user = UserFactory()
        url = reverse(f"{base_auth_url}token_obtain_pair")
        data = {
            "username": test_user.username,
            "password": test_user.plain_password,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert isinstance(response.data["access"], str)
        assert isinstance(response.data["refresh"], str)
        assert len(response.data["access"]) > 0
        assert len(response.data["refresh"]) > 0

    def test_login_invalid_credentials(self, api_client):
        """Failure with wrong password"""
        test_user = UserFactory()
        url = reverse(f"{base_auth_url}token_obtain_pair")
        data = {
            "username": test_user.username,
            # random wrong password
            "password": fake.password(),
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data
        assert "refresh" not in response.data


@pytest.mark.django_db
class TestTokenRefresh:
    """Tests for token refresh endpoint"""

    def test_refresh_token_success(self, authenticated_client):
        url = reverse(f"{base_auth_url}token_refresh")
        data = {"refresh": authenticated_client.refresh_token}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert isinstance(response.data["access"], str)
        # New access token should be different from the old one
        assert response.data["access"] != authenticated_client.access_token

    def test_refresh_token_invalid(self, api_client):
        """Failure: Invalid refresh token is rejected"""
        url = reverse(f"{base_auth_url}token_refresh")
        data = {"refresh": "invalid_fake_token_" + fake.uuid4()}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in response.data


@pytest.mark.django_db
class TestLogout:
    """Tests for logout endpoint"""

    def test_logout_success(self, authenticated_client):
        url = reverse(f"{base_auth_url}logout")
        data = {"refresh": authenticated_client.refresh_token}

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify token is blacklisted by trying to refresh
        refresh_url = reverse(f"{base_auth_url}token_refresh")
        refresh_response = authenticated_client.post(
            refresh_url, {"refresh": authenticated_client.refresh_token}, format="json"
        )
        # Should fail because token is blacklisted
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_unauthenticated(self, api_client):
        """Failure: Unauthenticated user cannot logout"""
        url = reverse(f"{base_auth_url}logout")
        # Use fake refresh token
        # do not use authenticated_client as it has a valid refresh token
        data = {"refresh": "false_refresh_token"}

        # Use non-authenticated client (no authentication header)
        response = api_client.post(url, data, format="json")

        # Should return 401 because IsAuthenticated permission is not met
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_missing_refresh_token(self, authenticated_client):
        """Failure: Logout without refresh token"""
        url = reverse(f"{base_auth_url}logout")
        data = {}  # No refresh token

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
