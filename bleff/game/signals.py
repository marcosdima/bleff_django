from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Game, Play

@receiver(post_save, sender=Game)
def creator_play_creation(sender, instance, created, **kwargs):
    if created and instance.creator:
        Play.objects.create(game=instance, user=instance.creator)
