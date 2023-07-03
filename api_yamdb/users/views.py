from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .models import User
from ..api.serializers import TokenSerializer


class SingUpSerializer:
    pass


class SignUp(APIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SingUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, created = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
        )
        confirmation_code = default_token_generator.make_token(user)
        email_text = (
            f'text {confirmation_code}'
        )
        data = {
            'email_info': email_text,
            'to_email': user.email,
            'mail_subject': 'Код подтверждения'
        }
        self.send_email(data)
        return Response(request.data, status=status.HTTP_200_OK)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['mail_subject'],
            body=data['email_info'],
            to=[data['to_email']]
        )
        email.send()


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.validated_data.get('confirmation_code')
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения!'},
                    status=status.HTTP_400_BAD_REQUEST)


class UsersViewSerializer:
    pass


class IsAdmin:
    pass


class MeSerializer:
    pass


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersViewSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('username',)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete', 'patch']

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, serializer=None):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
