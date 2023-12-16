from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from core import constants


class CustomUser(AbstractUser):
    """Custom User Model."""

    email = models.EmailField(
        _("Email address"),
        max_length=constants.MAX_EMAIL_LEN,
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        _("First name"),
        max_length=constants.MAX_USER_LEN,
        blank=False,
    )
    last_name = models.CharField(
        _("Last name"),
        max_length=constants.MAX_USER_LEN,
        blank=False,
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Author Subscription Model."""

    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="author",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "follower",
                    "author",
                ],
                name="unique_following",
            )
        ]
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
