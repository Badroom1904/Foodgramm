from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн-редактирование ингредиентов в рецепте."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-панель для тегов."""

    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-панель для ингредиентов."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
        'recipes_count',  # Добавлено
    )
    search_fields = ('name', 'measurement_unit')  # Добавлен measurement_unit
    list_filter = ('measurement_unit',)  # Добавлено

    def recipes_count(self, obj):
        """Количество рецептов, в которых используется ингредиент."""
        return obj.recipes.count()

    recipes_count.short_description = 'Используется в рецептах'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для рецептов."""

    list_display = ('id', 'name', 'author', 'pub_date', 'favorite_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)

    def favorite_count(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorites.count()

    favorite_count.short_description = 'Добавлений в избранное'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Админ-панель для связи рецептов и ингредиентов."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-панель для избранного."""

    list_display = ('id', 'user', 'recipe', 'created_at')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-панель для списка покупок."""

    list_display = ('id', 'user', 'recipe', 'created_at')
