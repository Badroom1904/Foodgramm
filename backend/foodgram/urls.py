from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import FollowViewSet, UserViewSet
from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/users/<int:id>/',
        UserViewSet.as_view({'get': 'retrieve'}),
        name='user-detail'),
    path(
        'api/users/<int:author_id>/subscribe/',
        FollowViewSet.as_view({'post': 'create'}), name='subscribe'),
    path(
        'api/users/subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'}),
        name='users-subscriptions'),
    path(
        'api/users/<int:author_id>/unsubscribe/',
        FollowViewSet.as_view({'delete': 'delete'}), name='unsubscribe'),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include(router.urls)),
]
