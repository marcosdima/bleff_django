from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Model

from .models import Game, HandGuess, Language, Play, Hand, Vote, Word, Guess
from .utils import plays_game, get_game_hand, get_hand_choice_words, remove_fields, conditions_are_met, is_leader
from .decorators import play_required, leader_required, conditions_met

def handle_redirection(request):
    # If does not exists a Play with this user and a game unfinished.
    is_playing_something = Play.objects.filter(user=request.user).exclude(game__finished_at__isnull=False)
    if not is_playing_something:
        return redirect('game:index')

    # If exists a game, but does not met the conditions.
    game = is_playing_something[0].game
    if len(conditions_are_met(game_id=game.id)) > 0:
        return redirect('game:waiting', game_id=game.id)

    # If exists a game, but does not start yet.
    game_start = Hand.objects.filter(game=game).exists()
    if not game_start:
        return redirect('game:waiting', game_id=game.id)
    
    # If the game started, and the user doesn't create a guess yet.
    already_made_guess = Guess.objects.filter(hand=get_game_hand(game_id=game.id), writer=request.user).exists()
    if not already_made_guess:
        return HttpResponseRedirect(reverse("game:hand", args=(game.id,)))
    
    # If the guess was already made.
    return HttpResponseRedirect(reverse("game:guesses", args=(game.id,)))


def create_or_none(model: Model, fields):
    try:
        creation = model.objects.create(**fields)
        creation.full_clean()
        return creation
    except Exception as e:
        # TODO: message error
        print(e)
        return None


def update_or_none(model: Model):
    try:
        model.save()
        model.full_clean()
    except Exception as e:
        # TODO: message error
        print(e)
        return None


class IndexView(generic.ListView):
    model = Game
    template_name = "game/index.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        context['languages'] = Language.objects.all()
        return context


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
def create_game(request):
    language_tag = request.POST['language_tag']
    language = get_object_or_404(Language, tag=language_tag)
    game = create_or_none(model=Game, fields={'creator': request.user, 'idiom': language})
    return redirect('game:waiting', game_id=game.id) if game else handle_redirection(request=request)


@login_required
@require_POST
@play_required(handle_redirection)
@conditions_met(handle_redirection)
def start_game(request, game_id):
    game = Game.objects.get(pk=game_id)

    start_hand = create_or_none(model=Hand, fields={'game': game})

    return HttpResponseRedirect(reverse("game:hand", args=(game_id,))) if start_hand else handle_redirection(request=request)


@login_required
@play_required(handle_redirection)
@conditions_met(handle_redirection)
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
@conditions_met(handle_redirection)
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


@login_required
@require_POST
@play_required(handle_redirection)
@conditions_met(handle_redirection)
def make_guess(request, game_id):
    guess = request.POST['guess']
    hand = get_game_hand(game_id=game_id)

    guess = create_or_none(model=Guess, fields={'hand': hand, 'writer':request.user, 'content': guess})

    if guess and request.user.id == hand.leader.id:
        return HttpResponseRedirect(reverse("game:check_guesses", args=(game_id,)))

    return HttpResponseRedirect(reverse("game:guesses", args=(game_id,))) if guess else handle_redirection(request=request)


@login_required
@require_GET
@play_required(handle_redirection)
@conditions_met(handle_redirection)
def guesses_view(request, game_id):

    if is_leader(user=request.user, game_id=game_id) and HandGuess.objects.filter(is_correct=None).exists():
        return HttpResponseRedirect(reverse("game:check_guesses", args=(game_id,)))

    template_name = "game/guesses.html"
    hand = get_game_hand(game_id=game_id)
    game = Game.objects.get(id=game_id)
    guesses = remove_fields(object=Guess, fields=['writer'], filters={'hand': get_game_hand(game_id=game_id)})

    # +1 because there is a default guess that was not writed by an user.
    guesses_ready = len(guesses) == Play.objects.filter(game=game_id).count() + 1

    context = {
        'hand': hand,
        'game': game,
        'guesses': guesses if guesses_ready else []
    }
        
    return render(request=request, template_name=template_name, context=context)
    

@login_required
@play_required(handle_redirection)
@leader_required(handle_redirection)
@conditions_met(handle_redirection)
def check_guesses(request, game_id):
    if request.method == 'post':
        guess_id = request.POST['guess_id']
        mark_as = request.POST['status']

        guess = get_object_or_404(HandGuess, id=guess_id)

        guess.is_correct = mark_as
        guess_updated = update_or_none(model=guess)

        return HttpResponseRedirect(reverse("game:check_guesses", args=(game_id,))) if guess_updated else handle_redirection(request=request)

    guesses = HandGuess.objects.filter(game=game_id)
    if len(guesses) == 0:
        return HttpResponseRedirect(reverse("game:guesses", args=(game_id,)))

    context = { 'guesses': guesses }

    return render(request, 'game:check_guesses', context)
    

@login_required
@require_POST
@play_required(handle_redirection)
@conditions_met(handle_redirection)
def vote(request, game_id):
    guess = get_object_or_404(Guess, writer=request.user, hand=get_game_hand(game_id=game_id))
    guess_hand = get_object_or_404(HandGuess, guess=guess)

    vote = create_or_none(model=Vote, fields={'to': guess_hand, 'user':request.user})

    return HttpResponseRedirect(reverse("game:guesses", args=(game_id,))) if vote else handle_redirection(request=request)
