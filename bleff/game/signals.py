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
            elif not hasattr(previus.hand, 'writer'):
                raise ValidationError("You can't modify 'by default Guess' HandGuess")