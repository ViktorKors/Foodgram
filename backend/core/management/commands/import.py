import json
import os
from io import open

from django.core.management.base import BaseCommand

from recipes.models import Ingredient as Ingrt


DATA_PATH = 'data/'

class Command(BaseCommand):
    """Import of ingredients."""

    help = "Command to import ingredients"

    def ingredient_import_json(self):
        """Importing ingredient objects from a json file."""
        with open(DATA_PATH + r"/ingredients.json", encoding="utf-8") as f:
            data = json.load(f)
            for object in data:
                try:
                    name = object["name"]
                    mu = object["measurement_unit"]
                    ingredient = Ingrt.objects.get_or_create(
                        name=name, measurement_unit=mu
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Object imported: {ingredient},"))

                except SystemError:
                    self.stdout.write("Import error")

    def handle(self, *args, **options):
        self.ingredient_import_json()
