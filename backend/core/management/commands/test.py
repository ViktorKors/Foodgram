from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from recipes.models import Tag

User = get_user_model()


class Command(BaseCommand):
    """Command for testing and debugging."""

    help = "Command to import ingredients"

    def handle(self, *args, **options):
        Tag.objects.get_or_create(name="name", slug="slug", color="#121111")
        Tag.objects.get_or_create(name="food", slug="food", color="#EB344c")
