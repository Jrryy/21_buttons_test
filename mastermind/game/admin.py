from django.contrib import admin

from game.models import Game, Guess


class GuessInlineAdmin(admin.TabularInline):
    """
    Inline admin for the Guesses of a game. The data is not modifiable by any means, just for
    visualization.
    """
    model = Guess
    readonly_fields = ('guess', 'is_solution', 'result_whites', 'result_blacks', 'created',
                       'updated', 'game')
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """
    Admin for the games. No data should be modified or added, so there are no modifiable fields,
    the only possible action is deletion.
    """
    readonly_fields = ('finished', 'guesses_count', 'created', 'updated', 'player', 'created',
                       'updated')
    list_display = ('__str__', 'player', 'finished', 'guesses_count', 'created', 'updated')
    inlines = (GuessInlineAdmin,)

    def has_add_permission(self, request):
        return False

    class Meta:
        model = Game
