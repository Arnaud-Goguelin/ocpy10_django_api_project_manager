from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("profile/<int:pk>/", views.UserProfileView.as_view(), name="profile"),
]
