from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


# ** ISSUE MANAGEMENT **
# - enpoints:
#       api / issues /  # for admin users
#       api / projects / < project_id: pk > / issues / (get, post)
#       api / projects / < project_id: pk > / issues / < id: pk > / (update, delete)
#
# get issue -> OK
# create issue -> OK
# delete issue -> OK
# update issue -> OK
# assigned an other contributor to issue
# create a link automatically to related project

# ** COMMENT MANAGEMENT **
# - enpoints:
#       api / comments /
#       api / projects / < project_id: pk > / issues / < issue_id: pk > / comments(get, post)
#       api / projects / < project_id: pk > / issues / < issue_id: pk > / comments / < id: pk > (update, delete)
#
# get comment
# create comment
# delete comment
# update comment
# create a link automatically to related issue

app_name = "issue"

issue_router = DefaultRouter()
issue_router.register(r"(?P<project_id>\d+)/issue", views.IssueModelViewSet, basename="issue")

comment_router = DefaultRouter()
comment_router.register(
    r"(?P<project_id>\d+)/issue/(?P<issue_id>\d+)/comment", views.CommentModelViewSet, basename="comment"
)

urlpatterns = [
    path("", include(issue_router.urls)),
    path("", include(comment_router.urls)),
]
