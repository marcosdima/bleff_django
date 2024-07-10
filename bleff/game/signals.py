from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Game, Play, Hand, Guess, Meaning

@receiver(post_save, sender=Game)
def creator_play_creation(sender, instance, created, **kwargs):
    if created and instance.creator:
        Play.objects.create(game=instance, user=instance.creator)

@receiver(post_save, sender=Hand)
def creator_right_guess(sender, instance, created, **kwargs):
    if created:
        Guess.objects.create(content=Meaning.objects.filter(word=instance.word)[0].text, is_original=True, hand=instance)
