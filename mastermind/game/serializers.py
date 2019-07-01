from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from game import choices
from game.models import Game, Move


class MoveSerializer(serializers.ModelSerializer):
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
        model = Move
        fields = ('guess', 'game', 'result_whites', 'result_blacks')


class GameSerializer(serializers.ModelSerializer):
    moves_count = serializers.IntegerField(read_only=True)
    finished = serializers.BooleanField(read_only=True)
    moves = MoveSerializer(read_only=True, many=True)

    class Meta:
        model = Game
        fields = ('moves_count', 'finished', 'moves')
