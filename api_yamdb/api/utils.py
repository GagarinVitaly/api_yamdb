from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


def send_confirmation_code(user: User) -> str:
    confirmation_code = default_token_generator.make_token(user)
    email_message = (
        f'токен подтверждения пользователя {user.username} -'
        f'{confirmation_code}')
    user.email_user(email_message)
    return confirmation_code


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"token": str(refresh.access_token)}
