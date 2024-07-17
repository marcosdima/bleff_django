from django.contrib.auth.models import User

from .models import Hand, Play, Choice

def plays_game(user: User, game_id: int) -> bool:
    return Play.objects.filter(game=game_id, user=user).exists()


def is_leader(user: User, game_id: int) -> bool:
    return Hand.objects.get(game=game_id, finished_at=None).leader.id == user.id


def get_game_hand(game_id: int):
    # Check if exists a hand
    if Hand.objects.all().exists():
        return Hand.objects.get(game=game_id, finished_at=None)

def get_hand_choice_words(hand: Hand) -> list:
    return [c.word for c in Choice.objects.filter(hand=hand)]