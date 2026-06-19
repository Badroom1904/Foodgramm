from django.contrib import admin
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
# UserViewSet регистрируем вручную, чтобы избежать конфликтов
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Ручные маршруты для пользователей (приоритет выше)
    path(
        'api/users/<int:id>/',
        UserViewSet.as_view({'get': 'retrieve'}),
        name='user-detail'
    ),
    path(
        'api/users/subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'}),
        name='users-subscriptions'
    ),
    path(
        'api/users/<int:author_id>/subscribe/',
        FollowViewSet.as_view({'post': 'create'}),
        name='subscribe'
    ),
    path(
        'api/users/<int:author_id>/unsubscribe/',
        FollowViewSet.as_view({'delete': 'delete'}),
        name='unsubscribe'
    ),

    # Djoser
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

    # Остальные роуты (tags, ingredients, recipes)
    path('api/', include(router.urls)),
]
