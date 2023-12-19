from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Exists, OuterRef, Value
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    UserMeSerializer,
    UserSerializer,
)

User = get_user_model()


class UsersViewSet(mixins.ListModelMixin, mixins.CreateModelMixin):
    """ViewSet for viewing and editing user data."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class BaseViewset(viewsets.ModelViewSet):
    """Basic model for Subscriptions, Favorites, Shopping List."""

    def _get_title_id(self):
        return self.kwargs.get("title_id")

    def _get_title(self, title_model):
        return get_object_or_404(title_model, id=self._get_title_id())

    def perform_create(self, serializer):
        recipe = self._get_title(self.title_model)
        serializer.save(
            user=self.request.user,
            recipe=recipe,
        )

    @action(
        methods=[
            "delete",
        ],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def delete(self, request, *args, **kwargs):
        recipe = self._get_title(self.title_model)
        model_items = self.model.objects.filter(
            recipe=recipe,
            user=self.request.user,
        )
        if model_items.exists():
            model_items.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            "The object does not exist.", status=status.HTTP_400_BAD_REQUEST
        )


class UserMe(APIView):
    """A viewset for your page."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserMeSerializer(
            user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        serializer.save()
        return self.get(request)


class TagsViewSet(viewsets.ModelViewSet):
    """Viewset for Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "id"
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    http_method_names = [
        "get",
    ]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for recipes."""

    serializer_class = RecipeSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.prefetch_related(
            "tags",
            "ingredients",
        ).select_related("author")

        if user.is_authenticated:
            return queryset.annotate(
                favorite_field=Exists(
                    Favorite.objects.filter(
                        user=user, recipe__id=OuterRef("id")
                    )
                ),
                shoppingcart_field=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe__id=OuterRef("id")
                    )
                ),
            ).order_by("-id")

        return queryset.annotate(
            favorite_field=Value(False, output_field=BooleanField()),
            shoppingcart_field=Value(False, output_field=BooleanField()),
        ).order_by("-id")

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            return RecipeSerializer
        if self.action in (
            "create",
            "update",
            "partial_update",
        ):
            return RecipeCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(BaseViewset):
    """Add to Favorites viewset."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    model = Favorite
    title_model = Recipe
    permission_classes = (IsAuthenticated,)
    http_method_names = [
        "post",
        "delete",
    ]
    lookup_field = "id"


class ShoppingCartViewSet(BaseViewset):
    """Viewset for adding to the Shopping List."""

    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = [
        "post",
        "delete",
    ]
    model = ShoppingCart
    title_model = Recipe


class FollowViewSet(BaseViewset):
    """Viewset for adding to Subscriptions."""

    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = [
        "post",
        "delete",
    ]
    model = Follow
    title_model = User

    def perform_create(self, serializer):
        author = self._get_title(self.title_model)
        serializer.save(
            follower=self.request.user,
            author=author,
        )

    @action(
        methods=[
            "delete",
        ],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def delete(self, request, *args, **kwargs):
        author = self._get_title(self.title_model)
        model_items = self.model.objects.filter(
            author=author,
            follower=self.request.user,
        )
        if model_items.exists():
            model_items.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            "Object does not exist.", status=status.HTTP_400_BAD_REQUEST
        )


class FollowListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Viewset for viewing the list of Subscriptions."""

    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(
            follower=self.request.user
        ).prefetch_related("author__recipe")


class IngredientViewSet(viewsets.ModelViewSet):
    """Ingredients View Viewset."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("name",)
    http_method_names = [
        "get",
    ]
