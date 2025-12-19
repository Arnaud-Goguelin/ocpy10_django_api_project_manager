from django.urls import path

from .views import LogoutView, DecoratedTokenRefreshView, DecoratedTokenObtainPairView

app_name = "auth"

urlpatterns = [
    path("login/", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", DecoratedTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
