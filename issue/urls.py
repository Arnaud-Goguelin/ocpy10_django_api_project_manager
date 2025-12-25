from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


# ** ISSUE
# MANAGEMENT **
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

app_name = "issue"
issue_router = DefaultRouter()
issue_router.register(r"(?P<project_id>\d+)/issue", views.IssueModelViewSet, basename="issue")


urlpatterns = [
    path("", include(issue_router.urls)),
]
