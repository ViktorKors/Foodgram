from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShoppingCart,
    Tag,
)

User = get_user_model()


class TagAdmin(admin.ModelAdmin):
    """Admin panel of the Tags model."""

    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )
    list_editable = (
        "name",
        "color",
        "slug",
    )


class IngredientAdmin(admin.ModelAdmin):
    """Admin panel of the Ingredients model."""

    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)


class RecipeIngredientAdmin(admin.ModelAdmin):
    """Admin panel of the Recipes/Ingredients model."""

    list_display = (
        "ingredient",
        "recipe",
        "amount",
    )


class TagInlineAdmin(admin.TabularInline):
    """Class for displaying Tags."""

    model = Recipe.tags.through
    min_num = 1


class IngredientInlineAdmin(admin.TabularInline):
    """Class for displaying Ingredients."""

    model = Recipe.ingredients.through
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """Admin panel of the Recipe model."""

    inlines = (
        IngredientInlineAdmin,
        TagInlineAdmin,
    )
    list_display = (
        "name",
        "author",
        "text",
        "cooking_time",
        "get_tag",
        "pub_date",
        "get_favorite_counter",
    )

    search_fields = (
        "name",
        "author__username",
        "tags__name",
    )
    list_filter = (
        "author",
        "tags",
    )
    readonly_fields = ("get_favorite_counter",)

    def get_tag(self, obj):
        """Allows to see all added Tags."""
        return ", ".join([p.name for p in obj.tags.all()])

    get_tag.short_description = "Tags"

    def get_favorite_counter(self, obj):
        """Allows to see the number of additions to Favorites."""
        return Favorite.objects.filter(recipe=obj).count()

    get_favorite_counter.short_description = "In Favorites"


class FavoriteAdmin(admin.ModelAdmin):
    """Admin panel of the Favorites model.."""

    list_display = (
        "user",
        "recipe",
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin panel of the Shopping List model."""

    list_display = (
        "user",
        "recipe",
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeTag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart)
