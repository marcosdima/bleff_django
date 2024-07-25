from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('menu.urls')),
    path("game/", include("game.urls")),
    path('users/', include('users.urls')),
    path("admin/", admin.site.urls),
]
