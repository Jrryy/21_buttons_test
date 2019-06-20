from django.urls import path
from users.views import UserView

urlpatterns = [
    path('', UserView.as_view(), name='create-user')
]
