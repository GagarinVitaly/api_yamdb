from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import (
    ReadOnly,
    SuperUserOrAdmin,
    SuperUserOrAdminOrModeratorOrAuthor)
from api.serializers import (
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    UserProfileSerializer)

from users.models import User
from .utils import send_confirmation_code


class SignUpViewSet(viewsets.ViewSet):
    """ViewSet для регистрации пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=['post'],)
    def create(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        username = serializer.data['username']
        user, _ = User.objects.get_or_create(email=email, username=username)
        confirmation_code = get_random_string(8)
        user.confirmation_code = confirmation_code
        user.save()
        send_confirmation_code(
            email=user.email,
            confirmation_code=confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        permission_classes=(IsAuthenticated,),)
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        serializer = UserProfileSerializer(user)
        if request.method == 'PATCH':
            serializer = UserProfileSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = TokenSerializer

    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Код подтверждения невалиден'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)
