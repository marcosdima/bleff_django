from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST

from .models import Game, HandGuess, Play, Hand, Vote, Word, Guess
from .utils import plays_game, get_game_hand, get_hand_choice_words, remove_fields
from .decorators import play_required, leader_required

def handle_redirection(request):
    # If does not exists a Play with this user and a game unfinished.
    is_playing_something = Play.objects.filter(user=request.user).exclude(game__finished_at__isnull=False)
    if not is_playing_something:
        return redirect('game:index')

    # If exists a game, but does not start yet.
    game = is_playing_something[0].game
    game_start = Hand.objects.filter(game=game).exists()
    if not game_start:
        return redirect('game:waiting', game_id=game.id)
    
    # If the game started, and the user doesn't create a guess yet.
    already_made_guess = Guess.objects.filter(hand=get_game_hand(game_id=game.id), writer=request.user).exists()
    if not already_made_guess:
        return HttpResponseRedirect(reverse("game:hand", args=(game.id,)))
    
    # If the guess was already made.
    return HttpResponseRedirect(reverse("game:guesses", args=(game.id,)))


class IndexView(generic.ListView):
    model = Game
    template_name = "game/index.html"


class WaitingView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = "game/waiting.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        id = self.kwargs.get('game_id') 
        game = Game.objects.get(id=id)
        context['game'] = game
        return context


    def get_queryset(self): 
        id = self.kwargs.get('game_id')
        return [p.user for p in Play.objects.filter(game=id)]
    

class GuessesView(LoginRequiredMixin, generic.ListView):
    model = Guess
    template_name = "game/guesses.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        id = self.kwargs.get('game_id') 
        game = Game.objects.get(id=id)
        context['game'] = game
        return context


    def get_queryset(self): 
        id = self.kwargs.get('game_id')
        guesses = remove_fields(object=Guess, fields=['writer'], filters={'hand': get_game_hand(game_id=id)})
        guesses_ready = len(guesses) == Play.objects.filter(game=id).count()

        return guesses if guesses_ready else []
    

@login_required
@require_POST
def enter_game(request):
    game_id = request.POST['game']
    game = Game.objects.get(id=game_id)

    if plays_game(user=request.user, game_id=game_id):
        return handle_redirection(request=request)
    
    try:
        Play.objects.create(game=game, user=request.user)
    except Exception as e:
        # TODO: message error
        print(e)
        return handle_redirection(request=request)

    return redirect('game:waiting', game_id=game.id)


@login_required
@require_POST
@play_required(handle_redirection)
def start_game(request, game_id):
    game = Game.objects.get(pk=game_id)

    alreadyEnded = game.finished_at != None
    alreadyStarted = Hand.objects.filter(game=game).exists()

    if alreadyEnded:
        # If the game already ended or user does not play 'game_id' game, redirects to index.
        return handle_redirection(request=request)
    
    if not alreadyStarted and (not game.creator or game.creator.id == request.user.id):
        Hand.objects.create(game=game)
        
    return handle_redirection(request=request)


@login_required
@play_required(handle_redirection)
def hand_view(request, game_id):
    hand = get_game_hand(game_id)
    words = []

    if request.user.id == hand.leader.id and not hand.word:
        words = get_hand_choice_words(hand=hand)

    return render(request, 'game/hand.html', {"hand": hand, "words_to_choose": words})


@login_required
@require_POST
@play_required(handle_redirection)
@leader_required(handle_redirection)
def choose_word(request, game_id):
    choice = request.POST['choice']

    # If the chosen word does not exists.
    if not Word.objects.filter(word=choice).exists():
        return handle_redirection(request=request)
    
    hand = get_game_hand(game_id=game_id)
    try:
        hand.word = Word.objects.get(word=choice)
        hand.save()
    except Exception as e:
        # TODO: message error
        print(e)
        return handle_redirection(request=request)

    return HttpResponseRedirect(reverse("game:hand", args=(game_id,)))


# TODO: The leader should check if there is any rigth guess.
@login_required
@require_POST
@play_required(handle_redirection)
def make_guess(request, game_id):
    guess = request.POST['guess']
    hand = get_game_hand(game_id=game_id)

    try:
        Guess.objects.create(hand=hand, writer=request.user, content=guess)
    except Exception as e:
        # TODO: message error
        print(e)
        return handle_redirection(request=request)
    
    return HttpResponseRedirect(reverse("game:guesses", args=(game_id,)))


@login_required
@require_POST
@play_required(handle_redirection)
def vote(request, game_id):
    guess = get_object_or_404(Guess, writer=request.user, hand=get_game_hand(game_id=game_id))
    guess_hand = get_object_or_404(HandGuess, guess=guess)

    try:
        Vote.objects.create(user=request.user, to=guess_hand)
    except Exception as e:
        print(e)

    return HttpResponseRedirect(reverse("game:guesses", args=(game_id,)))