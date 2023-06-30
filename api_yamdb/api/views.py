from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from api.permissions import (
    ReadOnly,
    SuperUserOrAdmin,
    SuperUserOrAdminOrModeratorOrAuthor)
from api.serializers import (
    SignUpSerializer,
    TokenSerializer,
    UserSerializer,
    UserProfileSerializer)

from users.constants import YAMDB_EMAIL
from users.models import User
from .utils import send_confirmation_code


#def get_token(user):
#    """Запрос токена."""
#    refresh = RefreshToken.for_user(user)
#    return {'token': str(refresh.access_token)}


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


#class TokenView(APIView):

#    def post(self, request):
#        serializer = TokenSerializer(data=request.data)
#        if not serializer.is_valid():
#            return Response(
#                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#        username = serializer.validated_data.get('username')
#        confirmation_code = serializer.validated_data.get('confirmation_code')
#        try:
#            user = User.objects.get(username=username)
#        except ObjectDoesNotExist:
#            return Response(
#                {'username': ['Пользователь не найден']},
#                status=status.HTTP_404_NOT_FOUND)
#        if user.confirmation_code != confirmation_code:
#            return Response(
#                {'confirmation_code': ['Недействительный код подтверждения']},
#                status=status.HTTP_400_BAD_REQUEST)
#        serializer.save()
#        token = serializer.data.get('token')
#        return Response({'token': token}, status=status.HTTP_200_OK)


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

#from django.core.exceptions import ObjectDoesNotExist

#from rest_framework import viewsets, permissions, filters
#from rest_framework import status
#from rest_framework.decorators import action, api_view
#from rest_framework.response import Response
#from rest_framework_simplejwt.tokens import RefreshToken
#from rest_framework_simplejwt.authentication import JWTAuthentication
#from django.utils.crypto import get_random_string
#from rest_framework.views import APIView

#from users.models import User
#from .serializers import UserSerializer, SignUpSerializer, TokenSerializer
#from .utils import send_confirmation_email


#def get_token(user):
    """Запрос токена."""
    #refresh = RefreshToken.for_user(user)
#    return {'token': str(refresh.access_token)}


#class UserViewSet(viewsets.ModelViewSet):
#    queryset = User.objects.all()
#    serializer_class = UserSerializer
#    #authentication_classes = [JWTAuthentication]
#    permission_classes = [permissions.IsAdminUser]
#    filter_backends = [filters.SearchFilter]
#    search_fields = ['username']
#    basename = 'users'


#class SignUpViewSet(viewsets.ViewSet):

#    @action(
#        detail=False,
#        methods=['post'],)
#    def create(self, request):
#        serializer = SignUpSerializer(data=request.data)
#        serializer.is_valid(raise_exception=True)
#        email = serializer.data['email']
#        username = serializer.data['username']
#        user, _ = User.objects.get_or_create(email=email, username=username)
#        confirmation_code = get_random_string(8)
#        user.confirmation_code = confirmation_code
#        user.save()
#        send_confirmation_email(
#            email=user.email,
#            confirmation_code=confirmation_code)
#        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(viewsets.ViewSet):
    serializer_class = TokenSerializer

    def create(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = User.objects.filter(username=username).first()
        #if not user or not user.check_confirmation_code(confirmation_code):
        #    return Response(
        #        {'detail': 'Неверные данные'},
        #        status=status.HTTP_400_BAD_REQUEST)
        if not user:
            return Response(
                {'detail': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND)
        if not user.check_confirmation_code(confirmation_code):
            return Response(
                {'detail': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        return Response({'token': token}, status=status.HTTP_200_OK)
