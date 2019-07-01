from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from game import choices
from game.models import Game, Guess


class GuessSerializer(serializers.ModelSerializer):
    guess = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=len(choices.GUESS_PEG_COLOURS)),
        allow_empty=False,
    )
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), write_only=True)
    result_whites = serializers.IntegerField(read_only=True)
    result_blacks = serializers.IntegerField(read_only=True)

    def validate_guess(self, value):
        if len(value) != 4:
            raise ValidationError('This field must have 4 elements.')
        return value

    class Meta:
        model = Guess
        fields = ('guess', 'game', 'result_whites', 'result_blacks')


class GameSerializer(serializers.ModelSerializer):
    guesses_count = serializers.IntegerField(read_only=True)
    finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = Game
        fields = ('guesses_count', 'finished', 'updated')
