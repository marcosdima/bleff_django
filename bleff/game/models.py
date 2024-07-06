from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models


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

    def __str__(self):
        return f'{self.word_translation}: {self.text}'


class Game(models.Model):
    # TODO: a function to determinate who wins (winner) and another one to gets the words played (words_played). 
    started_at = models.DateTimeField(default=timezone.now)
    idiom = models.ForeignKey(Language, on_delete=models.PROTECT)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Game {self.id}: created by {self.creator.username if self.creator else "SECRET"}'
    