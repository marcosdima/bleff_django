import random

from .models import Hand, Play, Game, Word, Meaning

def plays_game(user, game_id) -> bool:
    return Play.objects.filter(game=game_id, user=user).exists()


def is_leader(user, game_id) -> bool:
    return Hand.objects.get(game=game_id, finished_at=None).leader.id == user.id


def get_game_hand(game_id):
    # Check if exists a hand
    if Hand.objects.all().exists():
        return Hand.objects.get(game=game_id, finished_at=None)
