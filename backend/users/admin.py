from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Follow

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """Admin panel of the User model"""

    list_display = (
        "username",
        "email",
    )
    search_fields = (
        "username",
        "email",
    )


class FollowAdmin(admin.ModelAdmin):
    """Admin panel of the Subscription model."""

    list_display = (
        "follower",
        "author",
    )


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, CustomUserAdmin)
