from django.urls import path

from . import views


app_name = "user"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("profile/<int:user_id>/", views.UserProfileView.as_view(), name="profile"),
    path("profile/<int:user_id>/export-data/", views.GDPRExportView.as_view(), name="gdpr-export"),
]
