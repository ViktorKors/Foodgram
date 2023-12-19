import base64
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile

from core import constants
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueValidator
from users.models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User Mapping Serializer."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(follower=user, author=obj).exists()


class UserMeSerializer(UserSerializer):
    """Serializer of your page."""

    def get_is_subscribed(self, obj):
        return False


class UserCreateSerializer(UserSerializer):
    """User creation serializer."""

    email = serializers.EmailField(
        required=True,
        max_length=constants.MAX_EMAIL_LEN,
    )
    username = serializers.CharField(
        required=True,
        max_length=constants.MAX_USER_LEN,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    first_name = serializers.CharField(
        required=True,
    )
    last_name = serializers.CharField(
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        read_only_fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, email):
        """Mail validation."""
        if User.objects.filter(email=email):
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return email

    def validate_username(self, username):
        """Validation username."""
        if re.search(constants.USERNAME_PATTERN, username):
            return username
        raise serializers.ValidationError(
            "Name cannot contain special characters."
        )

    def validate_first_name(self, first_name):
        """Validation firstname."""
        if len(first_name) > constants.MAX_USER_LEN:
            raise serializers.ValidationError(
                f"Firstname cannot be longer {constants.MAX_USER_LEN}."
            )
        return first_name

    def validate_last_name(self, last_name):
        """Validation lastname."""
        if len(last_name) > constants.MAX_USER_LEN:
            raise serializers.ValidationError(
                f"Lastname cannot be longer {constants.MAX_USER_LEN}"
            )
        return last_name

    def create(self, validated_data):
        """Override create for password hashing."""
        validated_data["password"] = make_password(validated_data["password"])
        return super(UserSerializer, self).create(validated_data)


class TagSerializer(serializers.ModelSerializer):
    """Tag Serializer."""

    name = serializers.CharField(
        max_length=constants.MAX_TAG_LEN,
        min_length=constants.MIN_LEN,
        allow_blank=False,
    )
    slug = serializers.SlugField(
        max_length=constants.MAX_TAG_LEN,
        min_length=constants.MIN_LEN,
        allow_blank=False,
    )

    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag

        def validate_slug(self, slug):
            """Slug field validation."""
            if re.search(constants.TAG_SLUG_PATTERN, slug):
                return slug

        def validate_color(self, color):
            """Validation of the Color field."""
            if re.search(constants.COLOR_PATTERN, color):
                return color


class Base64ImageField(serializers.ImageField):
    """Serializer of images in HEX."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Recipe/Ingredient creation helper serializer."""

    id = serializers.PrimaryKeyRelatedField(
        source="ingredient.id",
        queryset=Ingredient.objects.all(),
        required=True,
    )
    name = serializers.CharField(
        source="ingredient.name",
        required=False,
    )
    amount = serializers.IntegerField(
        required=True,
        allow_null=False,
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        required=False,
    )

    unique_set = set()

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )

    def validate_amount(self, amount):
        """Ingredient Quantity Validation."""
        if amount < constants.MIN_INGREDIENTS_COUNT:
            self.unique_set.clear()
            raise serializers.ValidationError(
                f"Quantity cannot be less {constants.MIN_INGREDIENTS_COUNT}"
            )
        return amount

    def validate(self, attrs):
        ingredient = attrs.get("ingredient").get("id").id
        if ingredient in self.unique_set:
            self.unique_set.clear()
            raise serializers.ValidationError(
                "Ingredients should not be repeated."
            )
        self.unique_set.add(ingredient)
        return attrs


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe display serializer."""

    ingredients = RecipeIngredientCreateSerializer(
        source="recipeingredient",
        many=True,
    )
    tags = TagSerializer(
        many=True,
    )
    image = Base64ImageField(
        required=False,
        allow_null=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)
        model = Recipe

    def get_is_favorited(self, obj):
        """Getting placed in Favorites."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        favorite = Favorite.objects.filter(
            user=user,
            recipe=obj,
        )
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        """To check a recipe in the shopping cart."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        favorite = ShoppingCart.objects.filter(
            user=user,
            recipe=obj,
        )
        return favorite.exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Recipe creation serializer."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientCreateSerializer(
        source="recipeingredient",
        many=True,
        required=True,
        allow_null=False,
    )
    image = Base64ImageField(
        required=True,
        allow_null=False,
    )
    author = UserSerializer(
        required=False,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "author",
        )
        model = Recipe

    def validate_ingredients(self, ingredients):
        """Validation of ingredients."""
        RecipeIngredientCreateSerializer.unique_set.clear()
        if not ingredients:
            raise serializers.ValidationError(
                "You cant cook a dish out of nothing. "
                "Add at least one ingredient."
            )
        return ingredients

    def validate_tags(self, tags):
        """Tag Validation."""
        unique = set()
        for tag in tags:
            if tag.id in unique:
                raise serializers.ValidationError("Tags must be unique.")
            unique.add(tag.id)
        if not tags:
            raise serializers.ValidationError(
                "You must add at least one tag to the recipe."
            )
        return tags

    def validate(self, attrs):
        if "tags" not in attrs:
            raise serializers.ValidationError(
                "You must add at least one tag to the recipe."
            )

        if "recipeingredient" not in attrs:
            raise serializers.ValidationError("Add at least one ingredient.")
        return attrs

    def get_is_favorited(self, obj):
        """To check a recipe in the shopping cart."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        favorite = Favorite.objects.filter(
            user=user,
            recipe=obj,
        )
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        """To check a recipe in the shopping cart."""
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        favorite = ShoppingCart.objects.filter(
            user=user,
            recipe=obj,
        )
        return favorite.exists()

    def create_ingredient(self, items, instance):
        ingredients = []
        for item in items:
            ingredients.append(
                RecipeIngredient(
                    recipe=instance,
                    ingredient=item.get("ingredient").get("id"),
                    amount=item["amount"],
                )
            )
        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        """Recipe creation function."""
        items = validated_data.pop("recipeingredient")
        instance = super().create(validated_data)
        self.create_ingredient(items, instance)
        return instance

    def update(self, instance, validated_data):
        """Recipe update function."""
        items = validated_data.pop("recipeingredient")
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance = super().update(instance, validated_data)
        self.create_ingredient(items, instance)
        return instance

    def to_representation(self, instance):
        """Recipe representation function."""
        representation = super().to_representation(instance)
        representation["tags"] = TagSerializer(
            instance.tags,
            many=True,
        ).data
        return representation


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Serializer for adding a Recipe and Subscription link."""

    image = Base64ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for adding a Recipe to Favorites."""

    name = serializers.StringRelatedField(source="recipe.name")
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time", read_only=True
    )
    image = Base64ImageField(
        required=False, allow_null=True, source="recipe.image"
    )
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=CurrentUserDefault(),
    )

    class Meta:
        fields = (
            "user",
            "recipe",
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        model = Favorite

    def validate(self, attrs):
        """Recipe validation in favorites"""
        recipe_id = (
            self.context.get("request")
            .parser_context.get("kwargs")
            .get("title_id")
        )
        recipe = Recipe.objects.filter(id=recipe_id)
        if not recipe.exists():
            raise serializers.ValidationError("The recipe does not exist.")
        user = self.context.get("request").user
        is_exists = Favorite.objects.filter(
            user=user, recipe=int(recipe_id)
        ).exists()
        if is_exists:
            raise serializers.ValidationError(
                "The recipe is already in favorites."
            )
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for adding an Author to a Subscription."""

    id = serializers.PrimaryKeyRelatedField(
        source="author",
        read_only=True,
    )
    username = serializers.StringRelatedField(
        source="author.username",
    )
    first_name = serializers.StringRelatedField(
        source="author.first_name",
    )
    last_name = serializers.StringRelatedField(
        source="author.last_name",
    )
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    email = serializers.StringRelatedField(
        source="author.email",
    )

    class Meta:
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes_count",
            "recipes",
        )

        read_only_fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

        model = Follow

    def get_is_subscribed(self, obj):
        """Getting a subscription."""
        return Follow.objects.filter(
            follower=self.context.get("request").user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """Getting a recipes."""
        limit = self.context.get("request").query_params.get("recipes_limit")
        recipes = obj.author.recipe.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeFollowSerializer(
            recipes,
            read_only=True,
            many=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """Getting the number of recipes."""
        return obj.author.recipe.all().count()

    def validate(self, attrs):
        """Subscription Validation"""
        author_id = int(
            self.context.get("request")
            .parser_context.get("kwargs")
            .get("title_id")
        )
        user_id = self.context.get("request").user.id
        if author_id == user_id:
            raise serializers.ValidationError(
                "You cant subscribe to yourself."
            )
        if Follow.objects.filter(follower=user_id, author=author_id).exists():
            raise serializers.ValidationError(
                "You are already subscribed to the author"
            )
        return attrs


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer of Ingredients."""

    class Meta:
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        model = Ingredient


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for adding a Recipe to the Shopping List."""

    id = serializers.PrimaryKeyRelatedField(
        source="recipe",
        read_only=True,
    )
    name = serializers.StringRelatedField(
        source="recipe.name",
        read_only=True,
    )
    cooking_time = serializers.IntegerField(
        source="recipe.cooking_time",
        required=False,
        read_only=True,
    )
    image = Base64ImageField(
        source="recipe.image",
        required=False,
        allow_null=True,
    )

    class Meta:
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        model = ShoppingCart

    def validate(self, attrs):
        """Validation of recipes in the shopping cart."""
        recipe_id = (
            self.context.get("request")
            .parser_context.get("kwargs")
            .get("title_id")
        )
        recipes = Recipe.objects.filter(id=recipe_id)
        if not recipes.exists():
            raise serializers.ValidationError("The recipe does not exist.")
        user = self.context.get("request").user
        recipe = recipes.first()
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "The recipe is already on the shopping list."
            )
        return attrs
