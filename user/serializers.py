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
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    @staticmethod
    def calculate_age(date_of_birth: datetime) -> int:
        today = date.today()
        return (
            today.year
            - date_of_birth.year
            - (
                # check if a birthday is passed or not on current year
                # if True, bool is convert to 1
                # if False, bool is convert to 0 in arithemetic operation
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )
        )

    def get_age(self, obj: User) -> int:
        return self.calculate_age(obj.date_of_birth)

    def create(self, validated_data):
        """
        Create user with automatic consent based on age.
        If age < 15, consent is forced to False.
        """
        # Calculate age and set consent accordingly
        date_of_birth = validated_data.get("date_of_birth")

        if date_of_birth:
            age = self.calculate_age(date_of_birth)

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
            age = self.calculate_age(date_of_birth)

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
