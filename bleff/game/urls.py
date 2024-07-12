from django.urls import path

from . import views

app_name = "game"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:game_id>/", views.WaitingView.as_view(), name="waiting"),
]