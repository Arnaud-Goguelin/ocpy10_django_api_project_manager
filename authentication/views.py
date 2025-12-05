import logging

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    """
    User login endpoint - returns access and refresh tokens.
    POST /api/auth/login/
    Body: {"username": "...", "password": "..."}
    """

    permission_classes = [AllowAny]


class LogoutView(APIView):
    """
    User logout endpoint - blacklists the refresh token.
    POST /api/auth/logout/
    Body: {"refresh": "..."}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response("Refresh token is required", status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=200)

        except Exception as error:
            logger.error(f"Unexpected error during logout: {error}")
            return Response(
                str(error),
                status=400,
            )


class TokenRefreshView(TokenRefreshView):
    """
    Refresh access token using refresh token.
    POST /api/auth/token/refresh/
    Body: {"refresh": "..."}
    """

    permission_classes = [AllowAny]
