from rest_framework import serializers

from users.constants import (
    MAX_LEN_EMAIL,
    MAX_LEN_USERNAME,)
from users.models import User
from users.validators import (
    username_validator,
    forbidden_usernames_validator,)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',)


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""
    username = serializers.CharField(
        max_length=MAX_LEN_USERNAME,
        required=True,
        validators=[forbidden_usernames_validator, username_validator],)
    email = serializers.EmailField(
        max_length=MAX_LEN_EMAIL,
        required=True,)

    def validate(self, data):
        """Запрет на использование одинакового адреса электронной почты,
        имени пользователя."""
        if not User.objects.filter(
                username=data.get('username'),
                email=data.get('email')).exists():
            if User.objects.filter(username=data.get('username')):
                raise serializers.ValidationError(
                    'Пользователь с таким именем уже существует.')
            if User.objects.filter(email=data.get('email')):
                raise serializers.ValidationError(
                    'Указанный адрес электронной почты уже существует.')
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(
        max_length=MAX_LEN_USERNAME,
        required=True,
        validators=[forbidden_usernames_validator, username_validator],)
    confirmation_code = serializers.CharField(
        required=True,)


class UserProfileSerializer(UserSerializer):
    """Сериализатор профиля пользователя."""
    role = serializers.CharField(read_only=True)
