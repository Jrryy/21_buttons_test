from rest_framework import serializers

from game.models import Game, Move


class MoveSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), write_only=True)
    result_whites = serializers.IntegerField(read_only=True)
    result_blacks = serializers.IntegerField(read_only=True)

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
