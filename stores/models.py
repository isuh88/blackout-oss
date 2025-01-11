from django.db import models

from common.models import TimeStampMixin


class Store(TimeStampMixin, models.Model):
    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="상점 이름",
    )
    wallet_address = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="지갑 주소",
    )
    address = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="주소",
    )


class UserPrepayRelease(TimeStampMixin, models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="사용자",
    )
    prepay = models.ForeignKey(
        "Prepay",
        on_delete=models.CASCADE,
        verbose_name="선결제",
    )


class Prepay(TimeStampMixin, models.Model):
    class PrepayType(models.TextChoices):
        PRIVATE = "private", "개인"
        PUBLIC = "public", "공개"

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="사용자",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.CASCADE,
        verbose_name="상점",
    )
    credit = models.BigIntegerField(
        null=False,
        blank=False,
        verbose_name="금액",
    )
    code = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name="결제 코드",
    )
    type = models.CharField(
        max_length=16,
        choices=PrepayType.choices,
        default=PrepayType.PUBLIC,
        verbose_name="공개 종류",
    )
