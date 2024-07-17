from django.urls import path

from . import views

app_name = "game"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("enter/", views.enter_game, name="enter_game"),
    path("<int:game_id>/", views.WaitingView.as_view(), name="waiting"),
    path("start/<int:game_id>/", views.start_game, name="start_game"),
    path("<int:game_id>/hand/", views.hand_view, name="hand"),
    path("<int:game_id>/hand/choose/", views.choose_word, name="choose"),
    path("<int:game_id>/hand/guess/", views.make_guess, name="make_guess"),
    path("<int:game_id>/hand/guesses/", views.GuessesView.as_view(), name="guesses"),
]