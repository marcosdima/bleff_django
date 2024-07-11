from django.shortcuts import render
from django.views import generic
from .models import Game

class IndexView(generic.ListView):
    model=Game
    template_name = "game/index.html"
