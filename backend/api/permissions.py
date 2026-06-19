from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: только автор может изменять/удалять объект.
    Остальные могут только читать.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Изменять/удалять может только автор
        return obj.author == request.user


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Разрешение: неавторизованные могут только читать.
    Авторизованные — всё остальное.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
