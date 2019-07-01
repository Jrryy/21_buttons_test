from random import randrange

from game.choices import GUESS_PEG_COLOURS
from game.models import Game, Guess


def create_new_game(player):
    Game.objects.filter(player=player).update(finished=True)
    game = Game.objects.create(player=player)
    solution = [randrange(len(GUESS_PEG_COLOURS)) for _ in range(4)]
    Guess.objects.create(is_solution=True, guess=solution, game=game)
