import random
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.conf import settings

from .models import Game, Play, Hand, Guess, Meaning, HandGuess, Vote, Choice, Word

@receiver(post_save, sender=Game)
def play_creation_creator(sender, instance, created, **kwargs):
    if created and instance.creator:
        Play.objects.create(game=instance, user=instance.creator)


@receiver(post_save, sender=Hand)
def right_guess_creator(sender, instance, created, **kwargs):
    if instance.word:
        Guess.objects.create(content=Meaning.objects.filter(word=instance.word)[0].text, is_original=True, hand=instance)


@receiver(post_save, sender=Guess)
def handguess_creator(sender, instance, created, **kwargs):
    if created:
        HandGuess.objects.create(hand=instance.hand, guess=instance)


@receiver(pre_save, sender=HandGuess)
def handguess_update_restriction(sender, instance, **kwargs):
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
def vote_creator_restriction(sender, instance, **kwargs):
    if not instance.pk:
        if instance.to.hand.finished_at:
            raise ValidationError("You can't vote in a finished hand")
        elif Vote.objects.filter(to__hand=instance.to.hand, user=instance.user).exists():
            raise ValidationError("You can't vote again in the same hand")
        

@receiver(pre_save, sender=Hand)
def hand_set_leader(sender, instance, **kwargs):
    if not instance.leader:
        # Gets game players.
        players = [p.user for p in Play.objects.filter(game=instance.game)]

        # Gets te last n (number of players - 1) leaders.
        last_n_leaders = [h.leader for h in Hand.objects.filter(game=instance.game).order_by('-created_at')][:len(players)-1]

        # If any of them does not apper in last_n_leaders, we got the leader.
        for p in players:
            if not p in last_n_leaders:
                instance.leader = p


@receiver(post_save, sender=Hand)
def hand_create_default_choice(sender, instance: Hand, created, **kwargs):
    if created:
        word_counter = 0
        words_played_ids = [w.id for w in instance.game.words_played()]
        possible_words = list(Word.objects.exclude(id__in=words_played_ids))
        n_words = len(possible_words)

        while word_counter < settings.CHOICES_PER_HAND and word_counter < n_words:
            random_word = random.choice(possible_words)
            Choice.objects.create(hand=instance, word=random_word)
            possible_words.remove(random_word)
            word_counter += 1


@receiver(pre_save, sender=Hand)
def hand_word_change(sender, instance, **kwargs):
    if instance.id:
        previus = Hand.objects.get(id=instance.id)

        if previus.word != instance.word and not Choice.objects.filter(hand=instance, word=instance.word):
            raise ValidationError('Should exists a choice for this word to set it')
        elif previus.word != None and previus.word != instance.word:
            raise ValidationError('Hand word can not be changed')


@receiver(pre_save, sender=Hand)
def hand_creation_restriction(sender, instance, **kwargs):
    game = instance.game if hasattr(instance, 'game') else None
    unfinished_hand = Hand.objects.filter(game=game, finished_at=None).exclude(id=instance.id).exists()

    if unfinished_hand and instance.id == None:
        raise ValidationError('The previus hand must finish before another its created!')


@receiver(pre_save, sender=Game)
def user_already_playing(sender, instance, **kwargs):
    if not instance.pk and instance.creator:
        if Play.objects.filter(user=instance.creator).exclude(game__finished_at__isnull=False).exists():
            raise ValidationError('User is already playing something')