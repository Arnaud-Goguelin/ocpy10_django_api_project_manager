import pytest

from django.urls import reverse
from rest_framework import status

from config.factories import ProjectFactory, UserFactory, fake
from project.models import Project


base_project_url = "project:"


# ==================== ProjectModelViewSet Tests ====================


@pytest.mark.django_db
class TestProjectList:
    """Tests for listing projects (GET /projects/)"""

    def test_list_projects_success(self, authenticated_client, create_project):
        """Success: List all projects where user is author or contributor"""
        url = reverse(f"{base_project_url}project-list")

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        data = response.data.get("results", response.data)
        print(data)
        assert len(data) >= 1
        assert any(project["name"] == create_project.name for project in data)
        assert any(project["author"] == authenticated_client.user.pk for project in data)

    def test_list_projects_unauthenticated_failure(self, api_client):
        """Failure: Unauthenticated user cannot list projects"""
        url = reverse(f"{base_project_url}project-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProjectRetrieve:
    """Tests for retrieving a single project (GET /projects/{id}/)"""

    def test_retrieve_project_success(self, authenticated_client, create_project):
        """Success: Retrieve a project where user is contributor"""
        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": create_project.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == create_project.name
        assert response.data["description"] == create_project.description
        assert response.data["author"] == authenticated_client.user.pk

    def test_retrieve_project_not_contributor_failure(self, authenticated_client, create_project):
        """Failure: Cannot retrieve project where user is not a contributor"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)

        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": other_project.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProjectCreate:
    """Tests for creating a project (POST /projects/)"""

    def test_create_project_success(self, authenticated_client):
        """Success: Create a new project"""
        url = reverse(f"{base_project_url}project-list")
        data = {
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "type": fake.random_element([*Project.ProjectTypes]),
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == data["name"]
        assert response.data["description"] == data["description"]
        assert response.data["type"] == data["type"]
        # Verify author is set to authenticated user
        project = Project.objects.get(name=data["name"])
        assert project.author == authenticated_client.user

    def test_create_project_missing_required_fields_failure(self, authenticated_client):
        """Failure: Cannot create project without required fields"""
        url = reverse(f"{base_project_url}project-list")
        data = {
            "description": fake.text(max_nb_chars=200),
            # Missing name and type
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProjectUpdate:
    """Tests for updating a project (PUT /projects/{id}/)"""

    def test_update_project_success(self, authenticated_client, create_project):
        """Success: Author can update their project"""
        other_author = UserFactory()
        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": create_project.pk})
        data = {
            "author": other_author.pk,
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "type": fake.random_element([*Project.ProjectTypes]),
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]
        assert response.data["description"] == data["description"]
        assert response.data["author"] == other_author.pk

    def test_update_project_not_author_failure(self, authenticated_client):
        """Failure: Contributor (non-author) cannot update project"""
        other_author = UserFactory()
        project = ProjectFactory(author=other_author)
        # Add authenticated user as contributor
        project.contributors.add(authenticated_client.user)

        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": project.pk})
        data = {
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "type": fake.random_element([*Project.ProjectTypes]),
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProjectPatch:
    """Tests for partially updating a project (PATCH /projects/{id}/)"""

    def test_patch_project_success(self, authenticated_client, create_project):
        """Success: Author can partially update their project"""
        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": create_project.pk})
        data = {
            "name": fake.catch_phrase(),
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == data["name"]
        # Other fields should remain unchanged
        assert response.data["description"] == create_project.description
        assert response.data["author"] == authenticated_client.user.pk

    def test_patch_project_not_author_failure(self, authenticated_client):
        """Failure: Contributor (non-author) cannot partially update project"""
        other_author = UserFactory()
        project = ProjectFactory(author=other_author)
        project.contributors.add(authenticated_client.user)

        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": project.pk})
        data = {
            "name": fake.catch_phrase(),
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProjectDelete:
    """Tests for deleting a project (DELETE /projects/{id}/)"""

    def test_delete_project_success(self, authenticated_client, create_project):
        """Success: Author can delete their project"""
        project_id = create_project.pk
        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": project_id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(pk=project_id).exists()

    def test_delete_project_not_author_failure(self, authenticated_client):
        """Failure: Contributor (non-author) cannot delete project"""
        other_author = UserFactory()
        project = ProjectFactory(author=other_author)
        project.contributors.add(authenticated_client.user)

        url = reverse(f"{base_project_url}project-detail", kwargs={"pk": project.pk})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Project.objects.filter(pk=project.pk).exists()
