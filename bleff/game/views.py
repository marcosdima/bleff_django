from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Game, Play, Hand

class IndexView(generic.ListView):
    model=Game
    template_name = "game/index.html"


class WaitingView(LoginRequiredMixin, generic.ListView):
    model=User
    template_name = "game/waiting.html"
    game_id = ''


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['game_id'] = self.kwargs.get('game_id')
        
        return context


    def get_queryset(self): 
        id = self.kwargs.get('game_id')
        self.game_id = id
        return [p.user for p in Play.objects.filter(game=id)]
    

def start_game(request, game_id):
    game = Game.objects.get(pk=game_id)
    
    alreadyStarted = Hand.objects.filter(game=game).exists()

    if alreadyStarted:
        # TODO: In this case it should send the user to the actual hand.
        pass
    elif not game.creator:
        # TODO: If the game has no creator recorded, then it should start.
        pass
    elif game.creator.id == request.user.id:
        # TODO: The creator says 'START THE GAME!', so it should start.
        pass

    return redirect('game:waiting', game_id=game_id)
 