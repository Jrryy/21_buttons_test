from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, validators=[UnicodeUsernameValidator])
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
        fields = ('username', 'password', )


