from django.core.exceptions import ValidationError

from core import constants


def time_validator(value):
    """Recipe cooking time validator."""
    if value < constants.MIN_TIME:
        raise ValidationError(
            f"Cooking time cannot be less than {constants.MIN_TIME} minute"
        )


def amount_validator(value):
    """Quantity Validator for an Ingredient in a Recipe."""
    if value < constants.MIN_INGREDIENTS_COUNT:
        raise ValidationError(
            f"Quantity cannot be less than {constants.MIN_INGREDIENTS_COUNT}"
        )
