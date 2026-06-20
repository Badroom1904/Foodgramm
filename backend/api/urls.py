from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    FollowViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

router = DefaultRouter()
# UserViewSet не регистрируем через router — используем ручные маршруты
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),

    # Ручные маршруты для пользователей
    path(
        'users/<int:id>/',
        UserViewSet.as_view({'get': 'retrieve'}),
        name='user-detail'
    ),
    path(
        'users/subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'}),
        name='users-subscriptions'
    ),
    path(
        'users/<int:author_id>/subscribe/',
        FollowViewSet.as_view({'post': 'create'}),
        name='subscribe'
    ),
    path(
        'users/<int:author_id>/unsubscribe/',
        FollowViewSet.as_view({'delete': 'delete'}),
        name='unsubscribe'
    ),
]
