from rest_framework import status, viewsets
from rest_framework.response import Response

from game.choices import GUESS_PEG_COLOURS
from game.models import Game
from game.serializers import GameSerializer, GuessSerializer
from game.utils import create_new_game


class GameAPIView(viewsets.GenericViewSet):
    """
    Viewset related to the Games
    """
    def list(self, request, *args, **kwargs):
        """
        View that retrieves a list of all the Games the user that has made the request has
        played, ordered from most recent to oldest.
        """
        user = request.user
        queryset = user.games.all()
        serializer = GameSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        View that creates a new Game for the user that has made the request.
        """
        create_new_game(request.user)

        return Response('New game created.', status=status.HTTP_201_CREATED)


class GuessAPIView(viewsets.GenericViewSet):
    """
    Viewset related to the Guesses
    """
    serializer_class = GuessSerializer

    def list(self, request, *args, **kwargs):
        """
        View that retrieves a list of all the Guesses the user has made for their currently
        unfinished Game. Returns a 400 error if they have no started games.
        """
        user = request.user
        try:
            game = user.games.get(finished=False)
            serializer = self.serializer_class(
                game.guesses.filter(is_solution=False),
                many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Game.DoesNotExist:
            return Response('You have no started games yet.', status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        View that creates a new Guess for the user's currently unfinished Game. Returns a 400
        error if they have no started games. Also sets the game as finished and returns an extra
        message in case the user guessed the solution.
        """
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
            return Response('You have no started games yet.', status=status.HTTP_400_BAD_REQUEST)

    def list_peg_colours(self, request, *args, **kwargs):
        """
        View that returns the different integers and strings of the colours, for the purpose of
        showing them in a user friendly form.
        """
        return Response(GUESS_PEG_COLOURS, status=status.HTTP_200_OK)
