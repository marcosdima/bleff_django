from django.contrib.auth.models import User
from django.db.models import Model

from .models import Hand, Play, Choice, Game, Condition, HandGuess, Vote

class FilteredObject:
    def __init__(self, dictionary: dict) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)

    
    def __str__(self) -> str:
        result = f'Fields: \n'
        for k, v in self.__dict__.items():
            result += f'- {k}: {v} \n'
        return result


class ConditionsResult:
    def __init__(self, label: str, value_required: int) -> None:
        self.label = label
        self.value_required = value_required

    
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
        exists = Hand.objects.filter(game=game_id, finished_at=None).exists() 
        return Hand.objects.get(game=game_id, finished_at=None) if exists else None 


def get_hand_choice_words(hand: Hand) -> list:
    return [c.word for c in Choice.objects.filter(hand=hand)]


def remove_fields(object: Model, fields: list[str], filters=dict[str, any]) -> list[FilteredObject]:
    objects_values = object.objects.filter(**filters).values()

    return [FilteredObject(dictionary={ field: value for field, value in object_value.items() if not field in fields }) for object_value in objects_values]


def conditions_are_met(game_id: int) -> list[ConditionsResult]:
    game = Game.objects.get(id=game_id)
    conditions = Condition.objects.filter(game=game)
    cant_players = Play.objects.filter(game=game).count()
    result = []
    
    for condition in conditions:
        tag = condition.tag.tag
        value = condition.value

        if tag == 'MAX_PLAYERS' and cant_players > value:
            result.append(ConditionsResult(tag, value))
        elif tag == 'MIN_PLAYERS' and cant_players < value:
            result.append(ConditionsResult(tag, value))

    return result


def is_leader(user: User, game_id: int) -> bool:
    '''
        Check if user is the actual hand leader.
    '''
    hand = get_game_hand(game_id=game_id)
    return user.id == hand.leader.id if hand else False


def there_are_guesses_to_check(game_id: int) -> bool:
    return HandGuess.objects.filter(hand=get_game_hand(game_id=game_id), is_correct=None).exists()


def votes_remaining(game_id: int) -> int:
    hand = get_game_hand(game_id=game_id)
    hand_guesses = [hg.id for hg in HandGuess.objects.filter(hand=hand, is_correct=False)]
    users_count = Play.objects.filter(game__id=game_id).count() - 1
    users_who_guessed_right = HandGuess.objects.filter(hand=hand, is_correct=True).count()
    
    return users_count - users_who_guessed_right - Vote.objects.filter(to_id__in=hand_guesses).count()


def already_vote(user: User, game_id: int) -> bool:
    return Vote.objects.filter(user=user, to__hand=get_game_hand(game_id=game_id)).exists()


def last_hand(game_id: int) -> Hand | None:
    hands = Hand.objects.filter(game_id=game_id)
    return hands.latest('created_at') if hands.exists() else None


def guesses_ready(game_id: int) -> bool:
    hand = get_game_hand(game_id=game_id)
    return not HandGuess.objects.filter(hand=hand, is_correct=None).exists()


def points_in_game(user: User, game_id: int) -> int:
    played = Play.objects.filter(user=user, game__id=game_id)

    # If played does not exists, then the player didn't play this game.
    if not played:
        return 0
    
    game = played[0].game
    
    # TODO: Every pointing area could be customized.
    
    # Points for votes to your guesses. +1 for each
    your_guesses = HandGuess.objects.filter(guess__writer=user, is_correct=False, hand__game=game).exclude(hand__leader=user)
    votes_to_your_guesses = Vote.objects.filter(to__in=your_guesses).count()

    # Points for guessing right. CUSTOM
    right_guesses = HandGuess.objects.filter(guess__writer=user, is_correct=True, hand__game=game).count()

    # Points for being the leader and nobody voted the right one. CUSTOM
    definitions = HandGuess.objects.filter(guess__is_original=True, hand__leader=user)
    clean_leader_play = definitions.exclude(id__in=[hg['to'] for hg in Vote.objects.filter(to__in=definitions).values('to')]).count()

    # Points for your votes to the right definition. +1
    right_votes = Vote.objects.filter(user=user, to__guess__is_original=True).count()

    # Sets the custom points values.
    for condition in Condition.objects.filter(game=game):
        tag = str(condition.tag)
        if tag == 'POINTS_FOR_GUESSING_RIGHT':
            right_guesses *= condition.value
        elif tag == 'POINTS_FOR_CLEAN_LEADER':
            clean_leader_play *= condition.value

    return votes_to_your_guesses + right_guesses + clean_leader_play + right_votes
    

def get_game_users(game_id: int) -> list[User]:
    return [p.user for p in Play.objects.filter(game__id=game_id)]


def guessed_right(user: User, hand: Hand):
    hg = HandGuess.objects.get(hand=hand, guess__writer=user)
    return hg.is_correct
