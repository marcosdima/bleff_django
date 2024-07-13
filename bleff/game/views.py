from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User

from .models import Game, Play

class IndexView(generic.ListView):
    model=Game
    template_name = "game/index.html"


class WaitingView(generic.ListView):
    model=User
    template_name = "game/waiting.html"

    def get_queryset(self): 
        id = self.kwargs.get('game_id')
        return [p.user for p in Play.objects.filter(game=id)]
 