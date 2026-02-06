import pytest

from django.urls import reverse
from rest_framework import status

from config.factories import ProjectFactory, UserFactory
from project.models import Contributor


base_contributor_url = "project:contributor-"


# ==================== ContributorModelViewSet Tests ====================


@pytest.mark.django_db
class TestContributorList:
    """Tests for listing contributors (GET /projects/{project_id}/contributors/)"""

    def test_list_contributors_success(self, authenticated_client, create_project):
        """Success: List all contributors of a project"""
        url = reverse(f"{base_contributor_url}list", kwargs={"project_id": create_project.pk})

        response = authenticated_client.get(url)

        contributors_lists = response.data.get("results", response.data)

        assert len(contributors_lists) >= 1
        assert any(authenticated_client.user.id == contributor["user"] for contributor in contributors_lists)

    def test_list_contributors_not_member_failure(self, authenticated_client):
        """Failure: Cannot list contributors if not a project member"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)

        url = reverse(f"{base_contributor_url}list", kwargs={"project_id": other_project.pk})

        response = authenticated_client.get(url)
        contributors_lists = response.data.get("results", response.data)

        assert contributors_lists == []


@pytest.mark.django_db
class TestContributorRetrieve:
    """Tests for retrieving a single contributor (GET /projects/{project_id}/contributors/{id}/)"""

    def test_retrieve_contributor_success(self, authenticated_client, create_project):
        """Success: Retrieve a contributor from a project"""
        # set a new contributor as auth user is automatically set as contributor
        other_user = UserFactory()
        create_project.contributors.add(other_user)
        contributor = Contributor.objects.filter(project=create_project, user=other_user).first()

        url = reverse(
            f"{base_contributor_url}detail", kwargs={"project_id": create_project.pk, "contributor_id": contributor.pk}
        )

        response = authenticated_client.get(url)

        results = response.get("results", response.data)

        assert other_user.pk == results["user"]

    def test_retrieve_contributor_not_member_failure(self, authenticated_client):
        """Failure: Cannot retrieve contributor if not a project member"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)
        contributor = Contributor.objects.get(project=other_project, user=other_author)

        url = reverse(
            f"{base_contributor_url}detail", kwargs={"project_id": other_project.pk, "contributor_id": contributor.pk}
        )

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestContributorCreate:
    """Tests for adding a contributor (POST /projects/{project_id}/contributors/)"""

    def test_add_contributor_success(self, authenticated_client, create_project):
        """Success: Author can add a contributor to their project"""
        new_contributor = UserFactory()
        url = reverse(f"{base_contributor_url}list", kwargs={"project_id": create_project.pk})
        data = {
            "user_id": new_contributor.pk,
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert create_project.contributors.filter(id=new_contributor.pk).exists()

    def test_add_contributor_not_author_failure(self, authenticated_client):
        """Failure: Non-author cannot add contributors"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)
        other_project.contributors.add(authenticated_client.user)

        new_contributor = UserFactory()

        url = reverse(f"{base_contributor_url}list", kwargs={"project_id": other_project.pk})
        data = {
            "user_id": new_contributor.pk,
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestContributorDelete:
    """Tests for removing a contributor (DELETE /projects/{project_id}/contributors/{id}/)"""

    def test_remove_contributor_success(self, authenticated_client, create_project):
        """Success: Author can remove a contributor from their project"""
        contributor_user = UserFactory()
        create_project.contributors.add(contributor_user)
        contributor = Contributor.objects.get(project=create_project, user=contributor_user)

        url = reverse(
            f"{base_contributor_url}detail", kwargs={"project_id": create_project.pk, "contributor_id": contributor.pk}
        )

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not create_project.contributors.filter(id=contributor_user.id).exists()

    def test_remove_contributor_not_author_failure(self, authenticated_client):
        """Failure: Non-author cannot remove contributors"""
        other_author = UserFactory()
        project = ProjectFactory(author=other_author)
        project.contributors.add(authenticated_client.user)

        contributor_user = UserFactory()
        project.contributors.add(contributor_user)
        contributor = Contributor.objects.get(project=project, user=contributor_user)

        url = reverse(
            f"{base_contributor_url}detail", kwargs={"project_id": project.pk, "contributor_id": contributor.pk}
        )

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert project.contributors.filter(id=contributor_user.id).exists()
