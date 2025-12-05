import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


logger = logging.getLogger(__name__)


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
