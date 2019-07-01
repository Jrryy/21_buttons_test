from django.urls import path
from game.views import GameAPIView, MoveAPIView

urlpatterns = [
    path('new_game/', GameAPIView.as_view({'post': 'create'}), name='new-game'),
    path('historic/', GameAPIView.as_view({'get': 'list'}), name='view-historic'),
    path('make_guess/', MoveAPIView.as_view({'post': 'create'}), name='make-guess'),
    path('guesses/', MoveAPIView.as_view({'get': 'list'}), name='list-guess'),
]
