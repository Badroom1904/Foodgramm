from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для кастомной модели пользователя."""

    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_staff')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админ-панель для подписок."""

    list_display = ('id', 'user', 'author', 'created_at')
    search_fields = ('user__username', 'author__username')
