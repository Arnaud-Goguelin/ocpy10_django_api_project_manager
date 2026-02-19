from django.core.management.base import BaseCommand

from user.models import User


class Command(BaseCommand):
    help = "Create test users"

    def handle(self, *args, **options):
        users_data = [
            {"username": "Bob", "password": "softdesk_api", "date_of_birth": "1990-01-01", "consent": True},
            {
                "username": "Tom",
                "password": "softdesk_api",
                "date_of_birth": "2023-01-01",
                "consent": False,
            },
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                date_of_birth=user_data.get("date_of_birth"),
                consent=user_data.get("consent"),
                defaults={"is_active": True},
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'User "{user.username}" created successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'User "{user.username}" already exists'))
