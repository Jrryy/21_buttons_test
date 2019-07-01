from django.urls import path

from game.views import GameAPIView, GuessAPIView

urlpatterns = [
    path('new_game/', GameAPIView.as_view({'post': 'create'}), name='new-game'),
    path('historic/', GameAPIView.as_view({'get': 'list'}), name='view-historic'),
    path('make_guess/', GuessAPIView.as_view({'post': 'create'}), name='make-guess'),
    path('guesses/', GuessAPIView.as_view({'get': 'list'}), name='list-guess'),
    path('colours/', GuessAPIView.as_view({'get': 'list_peg_colours'}), name='list-colours'),
]
