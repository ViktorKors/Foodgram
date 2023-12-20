import django_filters
from django_filters.rest_framework import BooleanFilter
from recipes.models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    """
    Filter for queries to Recipe model objects.
    Filtering is carried out by slug tag, author id
    being in the user's Favorites and Shopping List.
    """

    tags = django_filters.AllValuesMultipleFilter(
        field_name="tags__slug",
        lookup_expr="iexact",
    )

    is_in_shopping_cart = BooleanFilter(
        field_name="is_in_shopping_cart",
    )

    is_favorited = BooleanFilter(
        field_name="is_favorited",
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "is_in_shopping_cart",
            "is_favorited",
            "author",
        )


class IngredientFilter(django_filters.FilterSet):
    """To filter by Ingredients."""

    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="istartswith",
    )

    class Meta:
        model = Ingredient
        fields = ("name",)
