from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    wallet_address = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="지갑 주소",
    )

    def __str__(self):
        return self.username
