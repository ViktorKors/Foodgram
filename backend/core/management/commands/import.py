import json
import os
from io import open

from django.core.management.base import BaseCommand

from recipes.models import Ingredient as Ingrt


def ingredient_import_json():
    """Importing ingredient objects from a json file."""
    os.chdir("data")
    full_path = os.getcwd()
    with open(full_path + r"/ingredients.json", encoding="utf-8") as f:
        data = json.load(f)
        for object in data:
            try:
                name = object["name"]
                mu = object["measurement_unit"]
                ingredient = Ingrt.objects.get_or_create(
                    name=name, measurement_unit=mu
                )
                print(f"Object imported: {ingredient},")

            except SystemError:
                print("Import error")


class Command(BaseCommand):
    """Import of ingredients."""

    help = "Command to import ingredients"

    def handle(self, *args, **options):
        ingredient_import_json()
