from django.contrib import admin

from .models import Game, Word, Meaning, Language


@admin.register(Game, Word, Meaning, Language)
class PersonAdmin(admin.ModelAdmin):
    pass
