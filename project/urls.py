from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# ** PROJECT MANAGEMENT **
#     - enpoints:
#            api/projects/ # for admin users
#            api/project/ (post)
#            api/project/<id:pk>/ (get, update, delete)
#            api/project/<id:pk>/contributors/ (get, post)
#            api/project/<project_id:pk>/contributors/<id:pk>/ (delete)
#
#     get project
#     create project
#     delete project
#     update project
#     assigned contributors to project

app_name = "project"
router = DefaultRouter()
router.register(r'', views.ProjectModelViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]
