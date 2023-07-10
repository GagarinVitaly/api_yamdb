from django.db.models import Avg
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404

from django_filters import CharFilter, FilterSet, NumberFilter
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin, )
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import GenericViewSet

from api.permissions import (
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly,
    SuperUserOrAdmin, )
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    TitleCreateSerializer,
    TokenSerializer,
    UserSerializer,
    UserProfileSerializer)
from reviews.models import (
    Category,
    Genre,
    Review,
    Title, )
from users.models import User
from users.constants import MESSAGE


class SignUpViewSet(viewsets.ViewSet):
    """ViewSet для регистрации пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['post'], )
    def create(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, _ = User.objects.get_or_create(email=email, username=username)
        user.email_user(
            "Confirmation code",
            MESSAGE.format(
                user=user.username,
                token=default_token_generator.make_token(user),
            ),
        ),
        return Response(request.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = TokenSerializer

    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = request.data.get('csrfmiddlewaretoken')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                "Пользователь или код подтверждения - не совпадают",
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
            }
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (SuperUserOrAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'delete', 'patch')

    @action(
        detail=False,
        methods=['patch', 'get'],
        permission_classes=(IsAuthenticated,), )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        serializer = UserProfileSerializer(user)
        if request.method == 'PATCH':
            serializer = UserProfileSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateDestroyListMixin(
    CreateModelMixin, DestroyModelMixin, GenericViewSet, ListModelMixin
):
    """Кастомный класс для жанров и категорий."""

    pass


class CategoryViewSet(CreateDestroyListMixin):
    """Вьюсет для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateDestroyListMixin):
    """Вьюсет для жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('name', 'category', 'genre', 'year',)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.all()
    permission_classes = [IsAdminOrReadOnly, ]
    filterset_class = TitleFilter
    filterset_fields = ('name',)
    ordering = ('name',)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(rating=Avg('review__score'))
        return queryset

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnly, ]

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorModeratorAdminOrReadOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=title)
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=title)
        serializer.save(author=self.request.user, review=review)
