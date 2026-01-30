import pytest

from django.urls import reverse
from rest_framework import status

from config.factories import CommentFactory, IssueFactory, ProjectFactory, UserFactory, fake
from issue.models import Comment


base_url = "issue:comment-"


@pytest.mark.django_db
class TestCommentList:
    """Tests for listing comments (GET /projects/{project_id}/issues/{issue_id}/comments/)"""

    def test_list_comments_success(self, authenticated_client, create_project):
        """Success: List all comments for an issue where user is contributor"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        comment = CommentFactory(issue=issue, author=authenticated_client.user)
        url = reverse(f"{base_url}list", kwargs={"project_id": create_project.pk, "issue_id": issue.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data.get("results", response.data)
        assert len(data) >= 1
        assert any(item["title"] == comment.title for item in data)

    def test_list_comments_not_contributor_failure(self, authenticated_client):
        """Failure: Cannot list comments if not a project contributor"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)
        issue = IssueFactory(project=other_project, author=other_author)
        CommentFactory(issue=issue, author=other_author)

        url = reverse(f"{base_url}list", kwargs={"project_id": other_project.pk, "issue_id": issue.pk})

        response = authenticated_client.get(url)

        data = response.data.get("results", response.data)

        assert data == []


@pytest.mark.django_db
class TestCommentRetrieve:
    """Tests for retrieving a single comment (GET /projects/{project_id}/issues/{issue_id}/comments/{id}/)"""

    def test_retrieve_comment_success(self, authenticated_client, create_project):
        """Success: Retrieve a comment where user is contributor"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        comment = CommentFactory(issue=issue, author=authenticated_client.user)
        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": create_project.pk, "issue_id": issue.pk, "pk": comment.pk},
        )

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == comment.title
        assert response.data["content"] == comment.content
        assert response.data["author"] == authenticated_client.user.pk

    def test_retrieve_comment_not_contributor_failure(self, authenticated_client):
        """Failure: Cannot retrieve comment if not a project contributor"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)
        issue = IssueFactory(project=other_project, author=other_author)
        comment = CommentFactory(issue=issue, author=other_author)

        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": other_project.pk, "issue_id": issue.pk, "pk": comment.pk},
        )

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCommentCreate:
    """Tests for creating a comment (POST /projects/{project_id}/issues/{issue_id}/comments/)"""

    def test_create_comment_success(self, authenticated_client, create_project):
        """Success: Contributor can create a comment"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        url = reverse(f"{base_url}list", kwargs={"project_id": create_project.pk, "issue_id": issue.pk})
        data = {
            "title": fake.sentence(),
            "content": fake.text(),
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == data["title"]
        assert response.data["content"] == data["content"]
        # Verify author and issue are set automatically
        comment = Comment.objects.get(title=data["title"])
        assert comment.author == authenticated_client.user
        assert comment.issue == issue

    def test_create_comment_not_contributor_failure(self, authenticated_client):
        """Failure: Non-contributor cannot create a comment"""
        other_author = UserFactory()
        other_project = ProjectFactory(author=other_author)
        issue = IssueFactory(project=other_project, author=other_author)

        url = reverse(f"{base_url}list", kwargs={"project_id": other_project.pk, "issue_id": issue.pk})
        data = {
            "title": fake.sentence(),
            "content": fake.text(),
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCommentUpdate:
    """Tests for updating a comment (PUT /projects/{project_id}/issues/{issue_id}/comments/{id}/)"""

    def test_update_comment_success(self, authenticated_client, create_project):
        """Success: Author can update their comment"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        comment = CommentFactory(issue=issue, author=authenticated_client.user)
        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": create_project.pk, "issue_id": issue.pk, "pk": comment.pk},
        )
        data = {
            "title": fake.sentence(),
            "content": fake.text(),
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == data["title"]
        assert response.data["content"] == data["content"]

    def test_update_comment_not_author_failure(self, authenticated_client, create_project):
        """Failure: Non-author contributor cannot update comment"""
        other_contributor = UserFactory()
        create_project.contributors.add(other_contributor)
        issue = IssueFactory(project=create_project, author=other_contributor)
        comment = CommentFactory(issue=issue, author=other_contributor)

        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": create_project.pk, "issue_id": issue.pk, "pk": comment.pk},
        )
        data = {
            "title": fake.sentence(),
            "content": fake.text(),
        }

        response = authenticated_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCommentPatch:
    """Tests for partially updating a comment (PATCH /projects/{project_id}/issues/{issue_id}/comments/{id}/)"""

    def test_patch_comment_success(self, authenticated_client, create_project):
        """Success: Author can partially update their comment"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        comment = CommentFactory(issue=issue, author=authenticated_client.user)
        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": create_project.pk, "issue_id": issue.pk, "pk": comment.pk},
        )
        data = {
            "title": fake.sentence(),
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == data["title"]
        # Other fields should remain unchanged
        assert response.data["content"] == comment.content

    def test_patch_comment_not_author_failure(self, authenticated_client, create_project):
        """Failure: Non-author contributor cannot partially update comment"""
        other_contributor = UserFactory()
        create_project.contributors.add(other_contributor)
        issue = IssueFactory(project=create_project, author=other_contributor)
        comment = CommentFactory(issue=issue, author=other_contributor)

        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": create_project.pk, "issue_id": issue.pk, "pk": comment.pk},
        )
        data = {
            "title": fake.sentence(),
        }

        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCommentDelete:
    """Tests for deleting a comment (DELETE /projects/{project_id}/issues/{issue_id}/comments/{id}/)"""

    def test_delete_comment_success(self, authenticated_client, create_project):
        """Success: Author can delete their comment"""
        issue = IssueFactory(project=create_project, author=authenticated_client.user)
        comment = CommentFactory(issue=issue, author=authenticated_client.user)
        comment_id = comment.pk
        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": create_project.pk, "issue_id": issue.pk, "pk": comment_id},
        )

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(pk=comment_id).exists()

    def test_delete_comment_not_author_failure(self, authenticated_client, create_project):
        """Failure: Non-author contributor cannot delete comment"""
        other_contributor = UserFactory()
        create_project.contributors.add(other_contributor)
        issue = IssueFactory(project=create_project, author=other_contributor)
        comment = CommentFactory(issue=issue, author=other_contributor)

        url = reverse(
            f"{base_url}detail",
            kwargs={"project_id": create_project.pk, "issue_id": issue.pk, "pk": comment.pk},
        )

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.filter(pk=comment.pk).exists()
