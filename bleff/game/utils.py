from django.contrib.auth.models import User
from django.db.models import Model

from .models import Hand, Play, Choice

class FilteredObject:
    def __init__(self, dictionary: dict) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)

    
    def __str__(self) -> str:
        result = f'Fields: \n'
        for k, v in self.__dict__.items():
            result += f'- {k}: {v} \n'
        return result


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


def remove_fields(object: Model, fields: list[str], filters=dict[str, any]) -> list[FilteredObject]:
    objects_values = object.objects.filter(**filters).values()

    return [FilteredObject(dictionary={ field: value for field, value in object_value.items() if not field in fields }) for object_value in objects_values]
