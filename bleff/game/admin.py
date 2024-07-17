from django.contrib import admin

from .models import Game, Word, Meaning, Language, Play, Hand, Guess, Vote

class PlayInLine(admin.TabularInline):
    model = Play
    extra = 2


class MeaningInLine(admin.TabularInline):
    model = Meaning


class HandInLine(admin.TabularInline):
    model = Hand
    extra = 0


class GuessInLine(admin.TabularInline):
    model = Guess
    extra = 2

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [PlayInLine, HandInLine]


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    inlines = [MeaningInLine]


@admin.register(Hand)
class HandAdmin(admin.ModelAdmin):
    inlines = [GuessInLine]


@admin.register(Language)
class PersonAdmin(admin.ModelAdmin):
    pass


