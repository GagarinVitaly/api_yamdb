from django.core.mail import send_mail
from users.constants import YAMDB_EMAIL


def send_confirmation_code(email, confirmation_code):
    """Отправка кода подтвержления на электроную почту."""
    send_mail(
        subject='Код подтверждения',
        message=f'Код подтверждения регистрации: {confirmation_code}',
        from_email=YAMDB_EMAIL,
        recipient_list=(email,),
        fail_silently=False,)
