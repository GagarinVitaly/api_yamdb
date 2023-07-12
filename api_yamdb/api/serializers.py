from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,)
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
        """
        Запрет на использование одинакового адреса электронной почты,
        имени пользователя.
        """

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


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'description',
                  'genre',
                  'category',
                  'rating')


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления произведений."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = ('id',
                  'name',
                  'year',
                  'description',
                  'genre',
                  'category',
                  'rating')

    def validate(self, data):
        if data.get('name') == data.get('category'):
            raise serializers.ValidationError(
                'Название не должно совпадать с категорией.')
        return data

    def to_representation(self, instance):
        serializer = TitleSerializer(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            author = self.context.get('request').user
            title_id = self.context.get('view').kwargs.get('title_id')
            title = get_object_or_404(Title, id=title_id)
            if Review.objects.filter(title_id=title.id,
                                     author=author).exists():
                raise ValidationError('Можно сделать только один отзыв.')
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'pub_date')
