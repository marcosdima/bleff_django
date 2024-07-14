from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.forms import ValidationError

from .models import Game, Play, Hand, Guess, Meaning, HandGuess, Vote

@receiver(post_save, sender=Game)
def creator_play_creation(sender, instance, created, **kwargs):
    if created and instance.creator:
        Play.objects.create(game=instance, user=instance.creator)


@receiver(post_save, sender=Hand)
def creator_right_guess(sender, instance, created, **kwargs):
    if created:
        Guess.objects.create(content=Meaning.objects.filter(word=instance.word)[0].text, is_original=True, hand=instance)


@receiver(post_save, sender=Guess)
def creator_handguess(sender, instance, created, **kwargs):
    if created:
        HandGuess.objects.create(hand=instance.hand, guess=instance)


@receiver(pre_save, sender=HandGuess)
def update_handguess_restriction(sender, instance, **kwargs):
    if instance.pk:
            previus = HandGuess.objects.get(pk=instance.pk)
        
            '''
            This means that was modified to True before.
            TODO: Should check if there are any votes, in that case updating is forbidden.
            '''
            if previus.is_correct:
                raise ValidationError("You can update HandGuess just one time")
            elif not previus.guess.writer:
                raise ValidationError("You can't modify 'by default Guess' HandGuess")
            

@receiver(pre_save, sender=Vote)
def play_creator_restriction(sender, instance, **kwargs):
    if not instance.pk:
        if instance.to.hand.finished_at:
            raise ValidationError("You can't vote in a finished hand")
        elif Vote.objects.filter(to__hand=instance.to.hand, user=instance.user).exists():
            raise ValidationError("You can't voto again in the same hand")
        

@receiver(pre_save, sender=Hand)
def hand_set_leader(sender, instance, **kwargs):
    if not hasattr(instance, 'leader'):
        # Gets game players.
        players = [p.user for p in Play.objects.filter(game=instance.game)]

        # Gets te last n (number of players - 1) leaders.
        last_n_leaders = [h.leader for h in Hand.objects.filter(game=instance.game).order_by('-started_at')][:len(players)-1]

        # If any of them does not apper in last_n_leaders, we got the leader.
        for p in players:
            if not p in last_n_leaders:
                instance.leader = p


@receiver(pre_save, sender=Hand)
def hand_creation_restriction(sender, instance, **kwargs):
    game = instance.game if hasattr(instance, 'game') else None
    unfinished_hand = Hand.objects.filter(game=game, finished_at=None).exclude(id=instance.id).exists()

    if unfinished_hand and instance.id == None:
        raise ValidationError('The previus hand must finish before another its created!')

