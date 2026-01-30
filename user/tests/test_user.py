from datetime import date, timedelta

import pytest

from django.urls import reverse
from rest_framework import status

from config.factories import UserFactory, fake

from ..models import User


base_user_url = "user:"


@pytest.mark.django_db
class TestSignupView:
    """Tests for user signup endpoint (POST)"""

    def test_signup_success(self, api_client):
        """Success: Create a new user account"""
        url = reverse(f"{base_user_url}signup")
        data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
            "date_of_birth": "1990-01-15",
            "consent": True,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        assert response.data["username"] == data["username"]
        assert response.data["email"] == data["email"]
        # Id and Password should not be returned
        assert "password" not in response.data
        assert "id" not in response.data
        # verify user was created in DB
        assert User.objects.filter(username=data["username"]).exists()

    def test_signup_failure_missing_required_fields(self, api_client):
        """Failure: Missing required fields"""
        url = reverse(f"{base_user_url}signup")
        data = {
            "username": fake.user_name(),
            # Missing email, password, date_of_birth, consent
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserProfileViewGet:
    """Tests for user profile GET endpoint"""

    def test_get_auth_user_profile_success(self, authenticated_client):
        """Success: Get own user profile"""
        url = reverse(f"{base_user_url}profile", kwargs={"pk": authenticated_client.user.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == authenticated_client.user.username
        assert response.data["email"] == authenticated_client.user.email
        # Id and Password should not be returned
        assert "password" not in response.data
        assert "id" not in response.data

    def test_get_profile_other_user_failure(self, authenticated_client):
        """Failure: Cannot get another user's profile"""
        other_user = UserFactory()
        url = reverse(f"{base_user_url}profile", kwargs={"pk": other_user.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserProfileViewPut:
    """Tests for user profile PUT endpoint"""

    def test_put_profile_success(self, authenticated_client):
        """Success: Update entire user profile"""
        url = reverse(f"{base_user_url}profile", kwargs={"pk": authenticated_client.user.pk})
        data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": "NewPass456!@#",
            "date_of_birth": "1995-05-20",
            "consent": True,
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == data["username"]
        assert response.data["email"] == data["email"]
        assert response.data["date_of_birth"] == data["date_of_birth"]

    def test_put_profile_failure_other_user(self, authenticated_client):
        """Failure: Cannot update another user's profile"""
        other_user = UserFactory()
        url = reverse(f"{base_user_url}profile", kwargs={"pk": other_user.pk})
        data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": "NewPass456!@#",
            "date_of_birth": "1995-05-20",
            "consent": True,
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserProfileViewPatch:
    """Tests for user profile PATCH endpoint"""

    @staticmethod
    def _get_date_of_birth_for_age(age: int) -> str:
        """
        Helper function to generate a date of birth that results in a specific age.
        Returns date in YYYY-MM-DD format.
        """
        today = date.today()
        birth_date = today - timedelta(days=age * 365 + age // 4)
        return birth_date.strftime("%Y-%m-%d")

    def test_patch_profile_success(self, authenticated_client):
        """Success: Partially update user profile"""
        url = reverse(f"{base_user_url}profile", kwargs={"pk": authenticated_client.user.pk})
        new_email = fake.email()
        data = {
            "email": new_email,
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == new_email
        # Other fields should remain unchanged
        assert response.data["username"] == authenticated_client.user.username

    def test_patch_profile_failure_unauthenticated(self, api_client):
        """Failure: Unauthenticated user cannot update profile"""
        test_user = UserFactory()
        url = reverse(f"{base_user_url}profile", kwargs={"pk": test_user.pk})
        data = {
            "email": fake.email(),
        }

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_profile_consent_forced_false_under_15(self, authenticated_client):
        """Success: Consent is forced to False when updating date_of_birth to under 15"""
        url = reverse(f"{base_user_url}profile", kwargs={"pk": authenticated_client.user.pk})
        data = {
            "date_of_birth": self._get_date_of_birth_for_age(13),
            # User tries to keep consent, but should be forced to False
            "consent": True,
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        # Consent forced to False
        assert response.data["consent"] is False
        assert response.data["age"] == 13

    def test_put_profile_consent_allowed_15_and_over(self, authenticated_client):
        """Success: Consent is preserved when updating to 15 or older"""
        url = reverse(f"{base_user_url}profile", kwargs={"pk": authenticated_client.user.pk})
        data = {
            "date_of_birth": self._get_date_of_birth_for_age(16),
            "consent": True,
        }

        response = authenticated_client.patch(url, data, format="json")

        # Consent is preserved
        assert response.status_code == status.HTTP_200_OK
        assert response.data["consent"] is True
        assert response.data["age"] == 16


@pytest.mark.django_db
class TestUserProfileViewDelete:
    """Tests for user profile DELETE endpoint"""

    def test_delete_profile_success(self, authenticated_client):
        """Success: Delete own user account"""
        user_id = authenticated_client.user.pk
        url = reverse(f"{base_user_url}profile", kwargs={"pk": user_id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Verify user is actually deleted
        assert not User.objects.filter(pk=user_id).exists()

    def test_delete_profile_other_user_failure(self, authenticated_client):
        """Failure: Cannot delete another user's account"""

        other_user = UserFactory()
        url = reverse(f"{base_user_url}profile", kwargs={"pk": other_user.pk})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Verify user still exists
        assert User.objects.filter(pk=other_user.pk).exists()


@pytest.mark.django_db
class TestGDPRExportView:
    """Tests for GDPR data export endpoint (GET)"""

    def test_gdpr_export_success(self, authenticated_client):
        """Success: Export own personal data"""
        url = reverse(f"{base_user_url}gdpr-export", kwargs={"pk": authenticated_client.user.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"].startswith("text/csv")
        # Verify CSV content contains user data
        content = response.content.decode("utf-8")
        assert authenticated_client.user.username in content
        assert authenticated_client.user.email in content

    def test_gdpr_export_other_user_failure(self, authenticated_client):
        """Failure: Cannot export another user's data"""
        other_user = UserFactory()
        url = reverse(f"{base_user_url}gdpr-export", kwargs={"pk": other_user.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
