from django.db import IntegrityError
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST

from .models import Game, Play, Hand
from .utils import plays_game

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
    

@login_required
@require_POST
def enter_game(request):
    game_id = request.POST['game']

    try:
        game = Game.objects.get(id=game_id)
        Play.objects.create(game=game, user=request.user)
        return redirect('game:waiting', game_id=game.id)
    except IntegrityError as e:
        if plays_game(user=request.user, game_id=game_id):
            return redirect('game:waiting', game_id=game.id)
    except Exception as e:
        # TODO: message error and validation of 'user is already playin another game'.
        print(e)

    return redirect('game:index')


def start_game(request, game_id):
    game = Game.objects.get(pk=game_id)
    
    alreadyEnded = game.finished_at != None
    alreadyStarted = Hand.objects.filter(game=game).exists()

    if alreadyEnded:
        return redirect('game:index')
    elif alreadyStarted:
        # TODO: In this case it should send the user to the actual hand.
        pass
    elif not game.creator or game.creator.id == request.user.id:
        # TODO: The creator says 'START THE GAME!', so it should start.
        pass

    return redirect('game:waiting', game_id=game_id)
 