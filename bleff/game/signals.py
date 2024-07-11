from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.forms import ValidationError

from .models import Game, Play, Hand, Guess, Meaning, HandGuess

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
