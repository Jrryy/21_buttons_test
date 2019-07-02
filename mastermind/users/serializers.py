from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import ASCIIUsernameValidator
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer to create a user given their username and password.
    """
    username = serializers.CharField(max_length=150, validators=[ASCIIUsernameValidator()])
    password = serializers.CharField(
        max_length=128,
        write_only=True,
        validators=[validate_password]
    )

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']

        return User.objects.create_user(username, password=password)

    class Meta:
        model = User
        fields = ('username', 'password',)
