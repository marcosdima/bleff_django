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


def get_game_words_choice(game_id, n_words) -> list:
    game = Game.objects.get(id=game_id)
    result = []
    possible_words = [m.word.id for m in Meaning.objects.filter(language=game.idiom)]
    played_words = [h.word.id for h in Hand.objects.filter(game=game)]

    while len(possible_words) > 0 and len(result) < n_words:
        word = random.choice(possible_words)

        if not word in played_words:
            result.append(Word.objects.get(id=word))

        possible_words.remove(word)

    return result
