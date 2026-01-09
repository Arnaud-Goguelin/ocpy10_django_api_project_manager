from datetime import date, datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    consent = models.BooleanField(default=False)

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
