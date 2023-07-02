from django.shortcuts import get_object_or_404

from rest_framework import serializers
# from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
# from api_yamdb.users.models import User

from reviews.models import Category, Genre, Title, Review, Comment


class UniqueSlugMixin(serializers.Serializer):
    slug = serializers.SlugField(
        validators=[UniqueValidator(queryset=None)]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].validators[0].queryset = self.Meta.model.objects.all()


class CategoriesSerializer(UniqueSlugMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenresSerializer(UniqueSlugMixin, serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_genres(self, obj):
        genres = obj.genres.all()
        serializer = self.get_serializer(genres, many=True)
        return serializer.data

    def get_category(self, obj):
        category = obj.category
        serializer = self.get_serializer(category)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        user = self.context['request'].user

        if self.context['request'].method == 'POST':
            if Review.objects.filter(title=title, author=user).exists():
                raise serializers.ValidationError('Нельзя оставить более одного отзыва')

        return data


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    review_text = serializers.SerializerMethodField()

    def get_author_username(self, obj):
        return obj.author.username

    def get_review_text(self, obj):
        return obj.review.text

    class Meta:
        model = Comment
        fields = '__all__'
