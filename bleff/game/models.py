from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.db import models

from .validators import FieldNull

class Word(models.Model):
    word = models.CharField(max_length=40, unique=True, validators=[MinLengthValidator(3)])

    def __str__(self):
        return self.word


class Language(models.Model):
    tag = models.CharField(max_length=3, primary_key=True, validators=[MinLengthValidator(1)])
    name = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(4)])

    def __str__(self):
        return f'{self.tag}-{self.name}'


class Meaning(models.Model):
    text = models.CharField(max_length=200, validators=[MinLengthValidator(10)])
    word_translation = models.CharField(max_length=40, validators=[MinLengthValidator(3)])
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['word', 'language'], name='unique_word_language_combination')
        ]


    def __str__(self):
        return f'{self.word_translation}: {self.text}'


class Game(models.Model):
    # TODO: a function to determinate who wins (winner). 
    created_at = models.DateTimeField(default=timezone.now)
    idiom = models.ForeignKey(Language, on_delete=models.PROTECT)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    finished_at = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return f'Game {self.id}: created by {self.creator.username if self.creator else "SECRET"}'
    

    def end(self):
        if self.finished_at:
            raise ValidationError("Can't end a game more than one time")
        self.finished_at = timezone.now()
        self.save()


    def words_played(self):
        return [hand.word for hand in Hand.objects.filter(game=self).exclude(word=None)]


class Play(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game', 'user'], name='user_can_play_this_game_only_one_time')
        ]


    def __str__(self):
        return f'User {self.user.username} plays/ed Game nro°{self.game.id}'
    

class Hand(models.Model):
    # TODO: a function to determinate who is the hand winner (winner)
    created_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True, default=None)
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, validators=[FieldNull(model=Game, field='finished_at')])
    word = models.ForeignKey(Word, on_delete=models.PROTECT, null=True, blank=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['word', 'game'], name='word_unique_per_game'),
        ]


    def save(self, *args, **kwargs):
        if self.leader and not Play.objects.filter(game=self.game, user=self.leader).exists():
            raise ValidationError("Leader can't be an User that does not belong")
        elif self.finished_at and self.finished_at < self.created_at:
            raise ValidationError('A Hand can not be finished before it starts')

        super().save(*args, **kwargs)


    def __str__(self):
        return f'Hand {self.id}'
    
    
    def end(self):
        if self.finished_at:
            raise ValidationError("Can't end a hand more than one time")

        self.finished_at = timezone.now()
        self.save()


class Guess(models.Model):
    content = models.CharField(max_length=200, validators=[MinLengthValidator(1)])
    created_at = models.DateTimeField(default=timezone.now)
    is_original = models.BooleanField(default=False)
    hand = models.ForeignKey(Hand, on_delete=models.CASCADE, validators=[FieldNull(model=Hand, field='finished_at')])
    writer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['hand', 'writer'], name='user_can_write_one_guess_per_hand')
        ]


    def save(self, *args, **kwargs):
        if hasattr(self, 'hand') and not self.id:
            is_original = Guess.objects.filter(hand=self.hand, is_original=True)

            if self.is_original and is_original.exists() and is_original[0].id != self.id:
                raise ValidationError('Just can exists one "is_original" Guess')
            elif not self.writer and Guess.objects.filter(hand=self.hand, writer=None).exists():
                raise ValidationError('Just one Guess can have writer as None, the one that has the right answer.')

        super().save(*args, **kwargs)


    def __str__(self):
        return f'Guess by {self.writer.username if self.writer else "GAME"}'
    

class HandGuess(models.Model):
    hand = models.ForeignKey(Hand, on_delete=models.CASCADE)
    guess = models.ForeignKey(Guess, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=None, blank=None, null=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['hand', 'guess'], name='hand_guess_combinations_are_unique')
        ]


    def __str__(self):
        return f'{self.hand} -> {self.guess}'
    

class Vote(models.Model):
    to = models.ForeignKey(HandGuess, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT) # TODO: Think about on delete and update.
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['to', 'user'], name='unique_user_guess_vote')
        ]


class Choice(models.Model):
    hand = models.ForeignKey(Hand, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['word', 'hand'], name='choice_word_unique_per_game'),
        ]


    def save(self, *args, **kwargs):
        if self.word in self.hand.game.words_played():
            raise ValidationError('Word already played in this game')
        elif self.word and self.hand and not Meaning.objects.filter(word=self.word, language=self.hand.game.idiom):
            raise ValidationError("Word must have a Meaning in Game idiom")
        
        super().save(*args, **kwargs)


class ConditionTag(models.Model):
    tag = models.CharField(max_length=70, validators=[MinLengthValidator(7)]) # TODO: Think if instead of modify save function, create validators like MinLengthValidator


class Condition(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    tag = models.ForeignKey(ConditionTag, on_delete=models.CASCADE)
    value = models.IntegerField()


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game', 'tag'], name='unique_tag_per_game')
        ]
