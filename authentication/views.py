import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


logger = logging.getLogger(__name__)


@extend_schema_view(
    post=extend_schema(
        summary="Obtain Obtain JWT token pair",
        description="Takes a set of user credentials and returns an access and refresh JSON web token "
        "pair. "
        "<br>Returns a `200` response code on success. "
        "<br>Raises a `400` error code if the request body is not valid. "
        "<br>Raises a `401` error code if the user credentials are invalid."
        "<br>"
        "<br>**Authentification required**: No"
        "<br>**Permissions required**: None ",
        tags=["Auth"],
    )
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema_view(
    post=extend_schema(
        summary="Refresh JWT token",
        description="Takes a refresh type JSON web token and returns an access type JSON web token if the refresh "
        "token is valid. "
        "<br>Returns a `200` response code on success."
        "<br>Raises a `400` error code if the request body is not valid."
        "<br>Raises a `401` error code if the refresh token is invalid."
        "<br>"
        "<br>**Authentification required**: No"
        "<br>**Permissions required**: None",
        tags=["Auth"],
    )
)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass


@extend_schema_view(post=extend_schema(summary="Logout user and invalidate refresh token", tags=["Auth"]))
class LogoutView(APIView):
    """
    Represents the user view for logout.
    <br>Returns a `200` response code on success.
    <br>Raises a `400` error code if no refresh token is provided in the request body.
    <br>
    <br>**Authentification required**: Yes
    <br>**Permissions required**: `IsAuthenticated`,
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
