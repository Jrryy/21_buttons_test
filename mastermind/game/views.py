from rest_framework import status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from game.serializers import GameSerializer, MoveSerializer
from game.models import Game, Move
from game.utils import create_new_game


class GameAPIView(viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = user.games.all()
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        create_new_game(request.user)

        return Response('New game created.', status=status.HTTP_201_CREATED)


class MoveAPIView(viewsets.ModelViewSet):
    serializer_class = MoveSerializer

    def list(self, request, *args, **kwargs):
        user = request.user
        try:
            game = user.games.get(finished=False)
            serializer = self.serializer_class(
                game.moves.filter(is_solution=False),
                many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Game.DoesNotExist:
            return Response('You have no started games yet', status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            game = user.games.get(finished=False).pk
            data = request.data
            data['game'] = game
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                guess = serializer.save()
                response_data = self.serializer_class(guess).data
                if response_data['result_blacks'] == 4:
                    response_data['message'] = 'You win!'
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Game.DoesNotExist:
            return Response('You have no started games yet', status=status.HTTP_400_BAD_REQUEST)
