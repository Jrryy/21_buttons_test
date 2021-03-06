from random import randrange

from game.choices import GUESS_PEG_COLOURS
from game.models import Game, Guess


def create_new_game(player):
    """
    Creates a new game for the player passed as parameter by updating the unfinished games of it
    as finished, creating a new game, and creating a solution for it with a random 4 peg
    combination.
    """
    Game.objects.filter(player=player).update(finished=True)
    game = Game.objects.create(player=player)
    solution = [randrange(len(GUESS_PEG_COLOURS)) for _ in range(4)]
    Guess.objects.create(is_solution=True, guess=solution, game=game)
