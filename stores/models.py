from django.db import models

from common.models import TimeStampMixin


class Store(TimeStampMixin, models.Model):
    class StoreType(models.TextChoices):
        PRIVATE = "private", "개인"
        PUBLIC = "public", "공개"

    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="상점 이름",
    )
    store_type = models.CharField(
        max_length=16,
        choices=StoreType.choices,
        default=StoreType.PUBLIC,
        verbose_name="상점 종류",
    )
    wallet_address = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="지갑 주소",
    )


class UserStoreRelease(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="사용자",
    )
    store = models.ForeignKey(
        "Store",
        on_delete=models.CASCADE,
        verbose_name="상점",
    )
