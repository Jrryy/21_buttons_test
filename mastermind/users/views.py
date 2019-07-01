from django.db import IntegrityError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.serializers import UserSerializer


class UserView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token = Token.objects.get(user=user).key
                return Response({'token': token}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response('This user already exists', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
