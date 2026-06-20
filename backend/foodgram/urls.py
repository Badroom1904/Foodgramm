from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),          # Все API-маршруты
    path('api/auth/', include('djoser.urls')),  # Аутентификация
    path('api/auth/', include('djoser.urls.authtoken')),
]
