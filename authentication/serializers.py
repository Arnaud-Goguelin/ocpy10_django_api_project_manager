from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout endpoint
    Only used to complete docs
    """

    refresh = serializers.CharField(help_text="Refresh token to blacklist")
