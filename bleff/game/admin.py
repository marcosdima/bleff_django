from django.contrib import admin

from .models import Game, HandGuess, Vote, Word, Meaning, Language, Play, Hand, Guess, Condition, ConditionTag

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


class ConditionInLine(admin.TabularInline):
    model = Condition
    extra = 2

class VoteInLine(admin.TabularInline):
    model = Vote
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [ConditionInLine, PlayInLine, HandInLine]


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    inlines = [MeaningInLine]


@admin.register(Hand)
class HandAdmin(admin.ModelAdmin):
    inlines = [GuessInLine]


@admin.register(Language)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(ConditionTag)
class ConditionTagAdmin(admin.ModelAdmin):
    pass


@admin.register(HandGuess)
class ConditionTagAdmin(admin.ModelAdmin):
    inlines = [VoteInLine]