from django.core.exceptions import ValidationError

from game.choices import GUESS_PEG_COLOURS

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class Game(models.Model):
    # Fields
    finished = models.BooleanField(default=False)
    moves_count = models.IntegerField(default=0)
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
        return (f"{self.player.username}'s game ({self.updated.strftime('%Y-%m-%d, %H:%M')}), "
                f"{'finished' if self.finished else 'unfinished'}.")

    class Meta:
        ordering = ('-updated', )


class Move(models.Model):
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
        related_name='moves',
        on_delete=models.CASCADE
    )

    def clean(self):
        if self.guess and len(self.guess) != 4:
            raise ValidationError('This guess has an incorrect number of pegs. Please select 4.')
        if self.is_solution and self.game.moves.filter(is_solution=True):
            raise ValidationError('This game already has a solution')
        super(Move, self).clean()

    def __str__(self):
        if self.is_solution:
            return (
                f"Solution for {self.game}\n"
                f"{[GUESS_PEG_COLOURS[peg_colour][1] for peg_colour in self.guess]}"
            )
        else:
            return (
                f"Move in {self.game}\n"
                f"{[GUESS_PEG_COLOURS[peg_colour][1] for peg_colour in self.guess]}, "
                f"{self.result_whites} whites, {self.result_blacks} blacks"
            )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.is_solution:
            self.result_whites = 0
            self.result_blacks = 0

            solution = self.game.moves.get(is_solution=True).guess.copy()
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
            self.game.moves_count += 1
            if self.result_blacks == 4:
                self.game.finished = True
            self.game.save()
        super(Move, self).save()

    class Meta:
        ordering = ('-game', '-created')
