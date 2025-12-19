from django.urls import path

from .views import DecoratedTokenObtainPairView, DecoratedTokenRefreshView, LogoutView


app_name = "auth"

urlpatterns = [
    path("login/", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", DecoratedTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
