from django.urls import path
from game.views import GameAPIView, MoveAPIView

urlpatterns = [
    path('new_game/', GameAPIView.as_view(), name='new-game'),
    path('make_guess/', MoveAPIView.as_view({'post': 'create'}), name='make-guess'),
    path('guesses/', MoveAPIView.as_view({'get': 'list'}), name='list-guess'),
]
