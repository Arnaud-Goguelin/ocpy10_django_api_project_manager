import pytest

from django.urls import reverse
from rest_framework import status

from config.factories import IssueFactory, ProjectFactory, UserFactory, fake
from issue.models import Issue


base_url = "issue:"


# ==================== IssueModelViewSet Tests ====================


@pytest.mark.django_db
class TestIssueList:
    """Tests for listing issues (GET /projects/{project_id}/issues/)"""

    def test_list_issues_success(self, authenticated_client, create_project):
        """Success: List all issues for a project where user is contributor"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        url = reverse(f"{base_url}issue-list", kwargs={"project_id": create_project.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data.get("results", response.data)
        assert len(data) >= 1
        assert any(item["title"] == issue.title for item in data)

    def test_list_issues_not_contributor_failure(self, authenticated_client):
        """Failure: Cannot list issues if not a project contributor"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)
        IssueFactory(project=other_project, author=other_author)

        url = reverse(f"{base_url}issue-list", kwargs={"project_id": other_project.pk})

        response = authenticated_client.get(url)

        data = response.data.get("results", response.data)
        assert data == []


@pytest.mark.django_db
class TestIssueRetrieve:
    """Tests for retrieving a single issue (GET /projects/{project_id}/issues/{id}/)"""

    def test_retrieve_issue_success(self, authenticated_client, create_project):
        """Success: Retrieve an issue where user is contributor"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": create_project.pk, "pk": issue.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == issue.title
        assert response.data["content"] == issue.content
        assert response.data["author"] == authenticated_client.user.pk

    def test_retrieve_issue_not_contributor_failure(self, authenticated_client):
        """Failure: Cannot retrieve issue if not a project contributor"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)
        issue = IssueFactory(project=other_project, author=other_author)

        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": other_project.pk, "pk": issue.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestIssueCreate:
    """Tests for creating an issue (POST /projects/{project_id}/issues/)"""

    def test_create_issue_success(self, authenticated_client, create_project):
        """Success: Contributor can create an issue"""
        url = reverse(f"{base_url}issue-list", kwargs={"project_id": create_project.pk})
        data = {
            "title": fake.sentence(),
            "content": fake.text(),
            "status": fake.random_element([*Issue.Status]),
            "priority": fake.random_element([*Issue.Priority]),
            "tags": fake.random_element([*Issue.Tags]),
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == data["title"]
        assert response.data["content"] == data["content"]
        # Verify author and project are set automatically
        issue = Issue.objects.get(title=data["title"])
        assert issue.author == authenticated_client.user
        assert issue.project == create_project

    def test_create_issue_not_contributor_failure(self, authenticated_client):
        """Failure: Non-contributor cannot create an issue"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)

        url = reverse(f"{base_url}issue-list", kwargs={"project_id": other_project.pk})

        data = {
            "title": fake.sentence(),
            "content": fake.text(),
            "status": fake.random_element([*Issue.Status]),
            "priority": fake.random_element([*Issue.Priority]),
            "tags": fake.random_element([*Issue.Tags]),
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestIssueUpdate:
    """Tests for updating an issue (PUT /projects/{project_id}/issues/{id}/)"""

    def test_update_issue_success(self, authenticated_client, create_project):
        """Success: Author can update their issue"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": create_project.pk, "pk": issue.pk})
        data = {
            "title": fake.sentence(),
            "content": fake.text(),
            "status": fake.random_element([*Issue.Status]),
            "priority": fake.random_element([*Issue.Priority]),
            "tags": fake.random_element([*Issue.Tags]),
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == data["title"]
        assert response.data["content"] == data["content"]

    def test_update_issue_not_author_failure(self, authenticated_client, create_project):
        """Failure: Non-author contributor cannot update issue"""
        other_contributor = UserFactory()
        create_project.contributors.add(other_contributor)
        issue = IssueFactory(project=create_project, author=other_contributor)

        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": create_project.pk, "pk": issue.pk})
        data = {
            "title": fake.sentence(),
            "content": fake.text(),
            "status": fake.random_element([*Issue.Status]),
            "priority": fake.random_element([*Issue.Priority]),
            "tags": fake.random_element([*Issue.Tags]),
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestIssuePatch:
    """Tests for partially updating an issue (PATCH /projects/{project_id}/issues/{id}/)"""

    def test_patch_issue_success(self, authenticated_client, create_project):
        """Success: Author can partially update their issue"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": create_project.pk, "pk": issue.pk})
        data = {
            "title": fake.sentence(),
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == data["title"]
        # Other fields should remain unchanged
        assert response.data["content"] == issue.content

    def test_patch_issue_not_author_failure(self, authenticated_client, create_project):
        """Failure: Non-author contributor cannot partially update issue"""
        other_contributor = UserFactory()
        create_project.contributors.add(other_contributor)
        issue = IssueFactory(project=create_project, author=other_contributor)

        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": create_project.pk, "pk": issue.pk})
        data = {
            "title": fake.sentence(),
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestIssueDelete:
    """Tests for deleting an issue (DELETE /projects/{project_id}/issues/{id}/)"""

    def test_delete_issue_success(self, authenticated_client, create_project):
        """Success: Author can delete their issue"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        issue_id = issue.pk
        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": create_project.pk, "pk": issue_id})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Issue.objects.filter(pk=issue_id).exists()

    def test_delete_issue_not_author_failure(self, authenticated_client, create_project):
        """Failure: Non-author contributor cannot delete issue"""
        other_contributor = UserFactory()
        create_project.contributors.add(other_contributor)
        issue = IssueFactory(project=create_project, author=other_contributor)

        url = reverse(f"{base_url}issue-detail", kwargs={"project_id": create_project.pk, "pk": issue.pk})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Issue.objects.filter(pk=issue.pk).exists()
