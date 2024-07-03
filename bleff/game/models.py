from django.core.validators import MinLengthValidator
from django.db import models

class Word(models.Model):
    word = models.CharField(max_length=40, unique=True, validators=[MinLengthValidator(3)])

    def __str__(self):
        return self.word


class Language(models.Model):
    tag = models.CharField(max_length=3, primary_key=True, validators=[MinLengthValidator(1)])
    name = models.CharField(max_length=20, unique=True)


class Meaning(models.Model):
    text = models.CharField(max_length=200)
    word_translation = models.CharField(max_length=40)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
