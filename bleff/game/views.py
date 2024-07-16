from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST

from .models import Game, Play, Hand
from .utils import plays_game, get_game_hand

class IndexView(generic.ListView):
    model=Game
    template_name = "game/index.html"


class WaitingView(LoginRequiredMixin, generic.ListView):
    model=User
    template_name = "game/waiting.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        context['game_id'] = self.kwargs.get('game_id') 
        return context


    def get_queryset(self): 
        id = self.kwargs.get('game_id')
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


@login_required
@require_POST
def start_game(request, game_id):
    game = Game.objects.get(pk=game_id)
    
    alreadyEnded = game.finished_at != None
    alreadyStarted = Hand.objects.filter(game=game).exists()

    if alreadyEnded or not plays_game(user=request.user, game_id=game_id):
        # If the game already ended or user does not play 'game_id' game, redirects to index.
        return redirect('game:index')
    elif alreadyStarted:
        return HttpResponseRedirect(reverse("game:hand", args=(game.id,)))
    elif not game.creator or game.creator.id == request.user.id:
        Hand.objects.create(game=game)
        return HttpResponseRedirect(reverse("game:hand", args=(game.id,)))
        
    return redirect('game:waiting', game_id=game_id)


@login_required
def hand_view(request, game_id):
    hand = get_game_hand(game_id)
    return render(request, 'game/hand.html', {"hand": hand})
