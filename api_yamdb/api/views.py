from rest_framework import viewsets, permissions, filters
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import User
from .serializers import UserSerializer, SignUpSerializer, TokenSerializer
from .utils import send_confirmation_email


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    #authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    basename = 'users'


class SignUpViewSet(viewsets.ViewSet):
    serializer_class = SignUpSerializer

    @action(
        detail=False,
        methods=['post'],)
    def create(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        username = serializer.data['username']
        user, _ = User.objects.get_or_create(email=email, username=username)
        if not user:
            return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        confirmation_code = user.generate_confirmation_code()
        send_confirmation_email(email, confirmation_code)
        return Response(
            {'detail': 'Письмо с кодом подтверждения отправлено'},
            status=status.HTTP_200_OK)

    basename = 'signup'


class TokenViewSet(viewsets.ViewSet):
    serializer_class = TokenSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = User.objects.filter(username=username).first()
        if not user or not user.check_confirmation_code(confirmation_code):
            return Response(
                {'detail': 'Неверные данные'},
                status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        return Response({'token': token}, status=status.HTTP_200_OK)

    basename = 'token'
