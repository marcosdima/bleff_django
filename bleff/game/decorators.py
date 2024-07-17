from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse

from .utils import plays_game

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