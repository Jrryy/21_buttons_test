from django.contrib import admin

from game.models import Game, Guess


class GuessInlineAdmin(admin.TabularInline):
    model = Guess
    readonly_fields = ('guess', 'is_solution', 'result_whites', 'result_blacks', 'created',
                       'updated', 'game')
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    readonly_fields = ('finished', 'guesses_count', 'created', 'updated', 'player', 'created',
                       'updated')
    list_display = ('__str__', 'player', 'finished', 'guesses_count', 'created', 'updated')
    inlines = (GuessInlineAdmin,)

    class Meta:
        model = Game
