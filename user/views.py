from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
from jsonschema import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import GDPRExportSerializer, UserSerializer
from.renderers import CSVRenderer

from .models import User
from .permissions import IsUserSelf


@extend_schema(summary="Create a user account", tags=["User"])
class SignupView(CreateAPIView):
    """
    Represents a view for handling user signup operations in order to create a new account.
    <br>It creates a User object in DB.
    <br>Returns a `201 Created` response code on success.
    <br>
    <br>**Authentification required**: No
    <br>**Permissions required**: None
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    get=extend_schema(
        summary="Get user profile",
        tags=["User"],
    ),
    put=extend_schema(
        summary="Update entirely user's profile",
        tags=["User"],
    ),
    patch=extend_schema(
        summary="Update one or many user's profile fields",
        tags=["User"],
    ),
    delete=extend_schema(
        summary="Delete user's account",
        tags=["User"],
    ),
)
class UserProfileView(RetrieveUpdateDestroyAPIView):
    """
    Represents the user profile view for interacting with authenticated user data.
    <br>Provides endpoints for:
     <br>GET a User object in DB,
     <br>PUT a User object in DB,
     <br>PATCH a User object in DB,
     <br>DELETE a User object in DB.
    <br>
    <br>Returns a `200` response code on success.
    <br>Raises a `400` error code if the request body is not valid.
    <br>Raises a `403` error code if the user is not authenticated.
    <br>Raises a `403` error code if the user is not the owner of the profile manipulated.
    <br>Raises a `404` error code if the user is not found.
    <br>
    <br>**Authentification required**: Yes
    <br>**Permissions required**: `IsAuthenticated`, `IsUserSelf` (User is the owner of the profile manipulated)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsUserSelf]

    def perform_destroy(self, instance: "User"):
        # delete() handles the HTTP request/response logic,
        # while perform_destroy() is specifically meant for the database deletion logic.
        if instance.projects.exists():
            raise ValidationError(
                "You cannot delete your account while you are the author of active projects."
                "Please transfer ownership of your projects first."
            )
        instance.delete()


@extend_schema(
    summary="Export user's personal data (GDPR)",
    description="Returns all personal data associated with the user account in JSON format. "
    "<br>Returns a `200` response code on success."
    "<br>Raises a `403` error code if the user is not authenticated."
    "<br>Raises a `403` error code if the user tries to access another user's data."
    "<br>"
    "<br>**Authentification required**: Yes"
    "<br>**Permissions required**: `IsAuthenticated`, `IsUserSelf`",
    tags=["User"],
    responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description="CSV file containing user's personal data",
                examples=[
                    OpenApiExample(
                        name="GDPR CSV Export",
                        value='username,email,date_of_birth,consent,age,id,first_name,last_name,date_joined,last_login\n'
                              'john_doe,john@example.com,1990-01-15,true,36,1,John,Doe,2024-01-01T10:00:00Z,2026-01-09T08:00:00Z',
                        media_type='text/csv',
                        )
                    ]
                )
        }
    )
class GDPRExportView(RetrieveAPIView):
    """
    Endpoint for GDPR-compliant data export.
    Allows users to download all their personal data.
    """

    queryset = User.objects.all()
    serializer_class = GDPRExportSerializer
    permission_classes = [IsAuthenticated, IsUserSelf]
    renderer_classes = [CSVRenderer]
