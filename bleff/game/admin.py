from django.contrib import admin

from .models import Game, Word, Meaning, Language, Play

class PlayInLine(admin.TabularInline):
    model = Play
    extra = 2

class MeaningInLine(admin.TabularInline):
    model = Meaning

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [PlayInLine]

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    inlines = [MeaningInLine]

@admin.register(Language)
class PersonAdmin(admin.ModelAdmin):
    pass
