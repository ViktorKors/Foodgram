from django.contrib.auth import get_user_model
from django.db import models

from .validators import amount_validator, time_validator
from django.utils.translation import gettext_lazy as _
from core import constants

User = get_user_model()


class Tag(models.Model):
    """Model Tag."""

    name = models.CharField(
        _("Name"),
        max_length=constants.MAX_CHARFIELD_LEN,
        unique=True,
    )
    color = models.CharField(
        _("Color"),
        max_length=constants.MAX_TAG_LEN,
        null=True,
        default=None,
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=constants.MAX_CHARFIELD_LEN,
        unique=True,
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Model Ingredient."""

    name = models.CharField(
        _("Ingredient name"),
        max_length=constants.MAX_CHARFIELD_LEN,
    )
    measurement_unit = models.CharField(
        _("Measurement unit"),
        max_length=constants.MAX_CHARFIELD_LEN,
    )

    class Meta:
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe model."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Author"),
        related_name="recipe",
    )
    tags = models.ManyToManyField(
        Tag,
        through="RecipeTag",
    )
    image = models.ImageField(
        _("Image"),
    )
    name = models.CharField(
        _("Recipe name"),
        max_length=constants.MAX_CHARFIELD_LEN,
    )
    text = models.TextField(
        _("Description"),
    )
    cooking_time = models.IntegerField(
        _("Cooking time"),
        validators=[
            time_validator,
        ],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        blank=False,
    )
    pub_date = models.DateTimeField(
        _("Publication date"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Connection of Tags and Recipes."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name=_("Tag"),
        related_name="recipetag",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name=_("Recipe"),
        related_name="recipetag",
    )

    class Meta:
        verbose_name = _("Recipe/Tag")
        verbose_name_plural = _("Recipes/Tags")
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tag",
                    "recipe",
                ],
                name="unique_recipe_tag",
            )
        ]

    def __str__(self):
        return f"{self.recipe}  {self.tag}"


class RecipeIngredient(models.Model):
    """Linking recipes with ingredients."""

    amount = models.IntegerField(
        _("Count"),
        validators=[
            amount_validator,
        ],
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name=_("Ingredient"),
        related_name="recipeingredient",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name=_("Recipe"),
        related_name="recipeingredient",
    )

    class Meta:
        verbose_name = _("Ingredient/Recipe")
        verbose_name_plural = _("Ingredients/Recipes")
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "ingredient",
                    "recipe",
                ],
                name="unique_recipe_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.ingredient} {self.recipe} {self.amount}"


class Favorite(models.Model):
    """Favorite Model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        related_name="favorite",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "recipe",
                ],
                name="unique_favorite",
            )
        ]
        verbose_name = _("Featured Recipe")
        verbose_name_plural = _("Featured Recipes")

    def __str__(self):
        return f"{self.user} {self.recipe}"


class ShoppingCart(models.Model):
    """ShoppingCart Model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoppingcart",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoppingcart",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "recipe",
                ],
                name="unique_shopping_card",
            )
        ]
        verbose_name = _("On the shopping list")
        verbose_name_plural = _("Shopping lists")

    def __str__(self):
        return f"{self.user} {self.recipe}"
