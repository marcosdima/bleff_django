from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse

from .utils import plays_game, get_game_hand, conditions_are_met

def play_required(handler):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            game_id = kwargs.get('game_id')

            if not plays_game(user=request.user, game_id=game_id):
                return handler(request)
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


def leader_required(handler):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            game_id = kwargs.get('game_id')

            hand = get_game_hand(game_id=game_id)

            if not hand or not hand.leader.id == request.user.id:
                return handler(request)
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


def conditions_met(handler):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            game_id = kwargs.get('game_id')

            if len(conditions_are_met(game_id=game_id)) > 0:
                return handler(request)
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator