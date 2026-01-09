from datetime import date, datetime

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "date_of_birth",
            "consent",
            "age",
        ]

    @staticmethod
    def validate_date_of_birth(value: datetime) -> datetime:
        """Ensure date of birth is not in the future"""
        # reminder, with DRF a method name validate_{field_name} is automatically called
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def create(self, validated_data):
        """
        Create user with automatic consent based on age.
        If age < 15, consent is forced to False.
        """
        # Calculate age and set consent accordingly
        date_of_birth = validated_data.get("date_of_birth")

        if date_of_birth:
            age = User.calculate_age(date_of_birth)

            if age < 15 or "consent" not in validated_data:
                validated_data["consent"] = False

        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance: User, validated_data):
        """
        Update user, re-check consent if date_of_birth is updated.
        """
        # Re-check age if date_of_birth is being updated
        date_of_birth = validated_data.get("date_of_birth", instance.date_of_birth)

        if date_of_birth and date_of_birth != instance.date_of_birth:
            age = User.calculate_age(date_of_birth)

            # Force consent to False if user becomes under 15
            if age < 15:
                validated_data["consent"] = False

        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # hash password
        password = validated_data.pop("password")
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class GDPRExportSerializer(UserSerializer):
    """Serializer for GDPR data export - extends UserSerializer with additional data"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            "id",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
        ]
