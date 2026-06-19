import logging

from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User

logger = logging.getLogger(__name__)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для пользователей (наследуется от Djoser)."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        """Просмотр конкретного пользователя."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'patch'],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Обновление аватара пользователя (принимает base64)."""
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {'error': 'Необходимо авторизоваться'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            serializer = AvatarSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.avatar = serializer.validated_data['avatar']
            user.save()

            user_serializer = self.get_serializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            error_msg = (
                f"Ошибка при загрузке аватара: {str(e)}\n"
                f"{traceback.format_exc()}"
            )
            logger.error(error_msg)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(
        detail=False,
        methods=['delete'],
        url_path='me/avatar'
    )
    def delete_avatar(self, request):
        """Удаление аватара пользователя."""
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Необходимо авторизоваться'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user.avatar = None
        user.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        """Получение списка авторов, на которых подписан пользователь."""
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Необходимо авторизоваться'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        follows = Follow.objects.filter(user=user).select_related('author')

        page = self.paginate_queryset(follows)
        if page is not None:
            serializer = FollowSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(
            follows,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюсет для подписок."""

    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Подписка на автора."""
        author_id = kwargs.get('author_id') or request.data.get('author')

        if not author_id:
            return Response(
                {'error': 'Не указан ID автора'},
                status=status.HTTP_400_BAD_REQUEST
            )

        author = get_object_or_404(User, id=author_id)

        if request.user == author:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Follow.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'error': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow = Follow.objects.create(
            user=request.user,
            author=author
        )

        serializer = self.get_serializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        """Отписка от автора."""
        author = get_object_or_404(User, id=author_id)
        follow = Follow.objects.filter(user=request.user, author=author)

        if not follow.exists():
            return Response(
                {'error': 'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [IngredientSearchFilter]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date',)
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = self.get_object()
        link = f"/recipes/{recipe.id}/"
        return Response({'short_link': link}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное."""
        recipe = self.get_object()

        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if created:
                serializer = FavoriteSerializer(favorite)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепта нет в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в список покупок."""
        recipe = self.get_object()

        if request.method == 'POST':
            cart, created = ShoppingCart.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if created:
                serializer = ShoppingCartSerializer(cart)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Рецепт уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if cart.exists():
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепта нет в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        user = request.user
        cart_items = ShoppingCart.objects.filter(user=user)

        if not cart_items.exists():
            return Response(
                {'error': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Оптимизированный запрос через ORM
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in_cart__user=user)
            .values(
                ingredient_name=F('ingredient__name'),
                unit=F('ingredient__measurement_unit')
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient_name')
        )

        if not ingredients:
            return Response(
                {'error': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lines = ['Список покупок:\n']
        for item in ingredients:
            lines.append(
                f"{item['ingredient_name']} ({item['unit']}) — "
                f"{item['total_amount']}"
            )

        text = '\n'.join(lines)
        response = Response(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
