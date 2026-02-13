from django.core.management.base import BaseCommand

from user.models import User


class Command(BaseCommand):
    help = "Create test users"

    def handle(self, *args, **options):
        users_data = [
            {"username": "Bob", "password": "softdesk_api"},
            {"username": "Tom", "password": "softdesk_api"},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(username=user_data["username"], defaults={"is_active": True})
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'User "{user.username}" created successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'User "{user.username}" already exists'))
