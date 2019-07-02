from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from game.choices import GUESS_PEG_COLOURS


class Game(models.Model):
    """
    The model that represents a game of mastermind. Fields:
    finished: Boolean that indicates if the game is finished or not.
    guesses_count: Amount of guesses the player has made.
    created: Date and time when the game was created.
    updated: Date and time when the game was last updated.
    player: The user this game belongs to.
    """
    # Fields
    finished = models.BooleanField(default=False)
    guesses_count = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    # Relations
    player = models.ForeignKey(
        User,
        related_name='games',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return (f"{self.player.username}'s game "
                f"({self.updated.strftime(settings.DATETIME_FORMAT)}), "
                f"{'finished' if self.finished else 'unfinished'}.")

    class Meta:
        ordering = ('-updated',)


class Guess(models.Model):
    """
    The model that represents a solution to a game or a guess made by the player. Fields:
    is_solution: boolean that indicates if the guess represents the solution of the game or has
    been made by the player.
    guess: List of 4 integers (according to the official rules) that represent a Mastermind code.
    result_whites: Integer indicating the amount of white pegs given to a user's guess (Null if
    is_solution is True)
    result_whites: Integer indicating the amount of black pegs given to a user's guess (Null if
    is_solution is True)
    created: Date and time when the peg was created.
    updated: Date and time when the peg was last updated (which should happen only once for guess).
    game: Game instance for which this guess was made.
    """
    # Fields
    is_solution = models.BooleanField(default=False)
    guess = ArrayField(models.SmallIntegerField(choices=GUESS_PEG_COLOURS))
    result_whites = models.SmallIntegerField(blank=True, null=True)
    result_blacks = models.SmallIntegerField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    # Relations
    game = models.ForeignKey(
        'Game',
        related_name='guesses',
        on_delete=models.CASCADE
    )

    def clean(self):
        """
        Check for validation errors that are not in the fields' parameters: guesses of length 4
        and uniqueness of a solution per Game instance.
        """
        if self.guess and len(self.guess) != 4:
            raise ValidationError('This guess has an incorrect number of pegs. Please select 4.')
        if self.is_solution and self.game.guesses.filter(is_solution=True):
            raise ValidationError('This game already has a solution')
        super(Guess, self).clean()

    def __str__(self):
        if self.is_solution:
            return (
                f"Solution for {self.game}\n"
                f"{[GUESS_PEG_COLOURS[peg_colour][1] for peg_colour in self.guess]}"
            )
        else:
            return (
                f"Guess in {self.game}\n"
                f"{[GUESS_PEG_COLOURS[peg_colour][1] for peg_colour in self.guess]}, "
                f"{self.result_whites} whites, {self.result_blacks} blacks"
            )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Overrided save method because before saving a Guess instance, in case it is not the
        solution, the white and black pegs have to be computed and saved too. This could be done
        somewhere else. However, this way we ensure that every single guess that has been made
        has its result too.
        """
        self.full_clean()
        if not self.is_solution:
            self.result_whites = 0
            self.result_blacks = 0

            solution = self.game.guesses.get(is_solution=True).guess.copy()
            player_guess = self.guess.copy()
            # We loop over the pegs twice here.
            # There should be a more efficient way to check blacks and whites,
            # but since there are only 4 of them we can do this at no cost
            for position in range(len(player_guess) - 1, -1, -1):
                if solution[position] == player_guess[position]:
                    self.result_blacks += 1
                    solution.pop(position)
                    player_guess.pop(position)
            for peg in player_guess:
                if peg in solution:
                    self.result_whites += 1
                    solution.remove(peg)
            self.game.guesses_count += 1
            if self.result_blacks == 4:
                self.game.finished = True
            self.game.save()
        super(Guess, self).save()

    class Meta:
        ordering = ('-game', '-created')
