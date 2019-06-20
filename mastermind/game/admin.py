from django.contrib import admin

from game.models import Game, Move


class MoveInlineAdmin(admin.TabularInline):
    model = Move
    readonly_fields = ('guess', 'is_solution', 'result_whites', 'result_blacks', 'created',
                       'updated', 'game')
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    readonly_fields = ('finished', 'moves_count', 'created', 'updated', 'player', 'created',
                       'updated')
    list_display = ('__str__', 'player', 'finished', 'moves_count', 'created', 'updated')
    inlines = (MoveInlineAdmin, )

    class Meta:
        model = Game
