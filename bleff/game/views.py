from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Model

from .models import Game, HandGuess, Language, Play, Hand, Vote, Word, Guess, ConditionTag, Condition
from .utils import plays_game, get_game_hand, get_hand_choice_words, remove_fields, conditions_are_met, is_leader, votes_remaining, already_vote, last_hand
from .decorators import play_required, leader_required, conditions_met

def handle_redirection(request):
    # If does not exists a Play with this user and a game unfinished.
    is_playing_something = Play.objects.filter(user=request.user).exclude(game__finished_at__isnull=False)
    if not is_playing_something:
        return redirect('game:index')

    # If exists a game, but does not met the conditions.
    game = is_playing_something[0].game
    if len(conditions_are_met(game_id=game.id)) > 0:
        # TODO: If the game has already a hand unfinished, an infinte loop appears. 
        return redirect('game:waiting', game_id=game.id)

    # If exists a game, but does not start yet.
    game_start = Hand.objects.filter(game=game).exists()
    if not game_start:
        return redirect('game:waiting', game_id=game.id)

    # If the game exists and there is no current hand, then the user should go to detail.
    hand = get_game_hand(game_id=game.id)
    if not hand:
        return HttpResponseRedirect(reverse("game:hand_detail", args=(last_hand(game_id=game.id).id,)))

    # If the game started, and the user doesn't create a guess yet.
    already_made_guess = Guess.objects.filter(hand=hand, writer=request.user).exists()
    if not already_made_guess:
        return HttpResponseRedirect(reverse("game:hand", args=(game.id,)))
  
    # If the guess was already made and you are the leader, then you must check.
    is_leader_var = is_leader(request.user, game_id=game.id)
    if is_leader_var and HandGuess.objects.filter(is_correct=None).exists():
        return HttpResponseRedirect(reverse("game:check_guesses", args=(game.id,)))

    # If the guess was already made and you are not the leader, or leader already checked.
    if not is_leader_var and not already_vote(user=request.user, game_id=game.id):
        return HttpResponseRedirect(reverse("game:guesses", args=(game.id,)))

    # If you already vote, then go to the end.
    return HttpResponseRedirect(reverse("game:hand_detail", args=(hand.id,)))


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

        context['conditions'] = [(c.tag, range(c.min, c.max + 1)) for c in ConditionTag.objects.all()]

        return context


@login_required
@require_GET
def waiting(request, game_id):
    game = Game.objects.get(id=game_id)
    conditions = Condition.objects.filter(game=game)
    users = [p.user.username for p in Play.objects.filter(game=game_id)]

    return render(
        request, 
        'game/waiting.html', 
        {
            'users': users, 
            'conditions': conditions, 
            'game': game
        }
    )


@login_required
@require_POST
def enter_game(request):
    key = 'game'
    if not key in request.POST:
        return handle_redirection(request=request)

    game_id = request.POST[key]
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
    language_tag = request.POST['language']
    language = get_object_or_404(Language, tag=language_tag)

    game = create_or_none(model=Game, fields={'creator': request.user, 'idiom': language})

    if game:
        condition_tags = ConditionTag.objects.all()

        copy = request.POST.copy()

        # TODO: This should work now, but it's not the best solution.
        if copy['MAX_PLAYERS'] < copy['MIN_PLAYERS']:
            copy['MAX_PLAYERS'] = copy['MIN_PLAYERS']

        for tag in condition_tags:
            if tag.tag in copy:
                create_or_none(model=Condition, fields={'game': game, 'tag': tag, 'value': int(copy[tag.tag])})

    return redirect('game:waiting', game_id=game.id) if game else handle_redirection(request=request)


@login_required
@require_POST
@play_required(handle_redirection)
@conditions_met(handle_redirection)
def start_game(request, game_id):
    game = Game.objects.get(pk=game_id)

    # Creates hand if there is no game-hand and the player is the creator
    start_hand = create_or_none(model=Hand, fields={'game': game}) if not game.creator or request.user == game.creator else None

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
    if is_leader(user=request.user, game_id=game_id):
        return HttpResponseRedirect(reverse("game:check_guesses", args=(game_id,)))
    elif already_vote(user=request.user, game_id=game_id):
        return handle_redirection(request=request)

    template_name = "game/guesses.html"
    hand = get_game_hand(game_id=game_id)
    game = Game.objects.get(id=game_id)

    guesses_ready = not HandGuess.objects.filter(hand=hand, is_correct=None).exists()

    hand_guesses = remove_fields(object=HandGuess, fields=['writer'], filters={'hand': get_game_hand(game_id=game_id), 'is_correct': False})

    guesses = [Guess.objects.get(pk=hg.guess_id) for hg in hand_guesses] if guesses_ready else []

    context = {
        'hand': hand,
        'game': game,
        'guesses': guesses
    }
        
    return render(request=request, template_name=template_name, context=context)
    

@login_required
@play_required(handle_redirection)
@leader_required(handle_redirection)
@conditions_met(handle_redirection)
def check_guesses(request, game_id):
    hand = get_game_hand(game_id=game_id)
    guesses = [hg.guess for hg in HandGuess.objects.filter(hand=hand, is_correct=None)]

    if len(guesses) == 0:
        return handle_redirection(request=request)

    if request.method == 'POST':
        for g in guesses:
            set_as = request.POST[str(g.id)]

            if set_as:
                hand_guess = get_object_or_404(HandGuess, hand=hand, guess=g)
                hand_guess.is_correct = True if set_as == 'True' else False
                update_or_none(hand_guess)

        return handle_redirection(request=request)

    context = { 'guesses': guesses, 'game_id': game_id }

    return render(request=request, template_name='game/check_guesses.html', context=context)
    

@login_required
@require_POST
@play_required(handle_redirection)
@conditions_met(handle_redirection)
def vote(request, game_id):
    guess = get_object_or_404(Guess, writer=request.user, hand=get_game_hand(game_id=game_id))
    guess_hand = get_object_or_404(HandGuess, guess=guess)

    create_or_none(model=Vote, fields={'to': guess_hand, 'user':request.user})

    if not votes_remaining(game_id=game_id):
        hand = get_game_hand(game_id=game_id)
        if hand: 
            hand.end()

    return handle_redirection(request=request)


@require_GET
def hand_detail(request, hand_id):
    hand = get_object_or_404(Hand, id=hand_id)

    hand_guesses = [hg.id for hg in HandGuess.objects.filter(hand=hand)]
    votes = Vote.objects.filter(to_id__in=hand_guesses)

    if not hand.finished_at:
        return render(request=request, template_name='game/hand_detail.html', context={'hand': hand, 'votes': votes})

    guesses = [hg.guess for hg in HandGuess.objects.filter(hand=hand, guess__writer__isnull=False)]

    for guess in guesses:
        guess.votes = Vote.objects.filter(to__guess=guess).count()

    context = {
        'hand': hand,
        'votes': Vote.objects.filter(to_id__in=hand_guesses),
        'guesses': guesses,
    }

    return render(request=request, template_name='game/hand_detail.html', context=context)
