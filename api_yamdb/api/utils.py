from django.core.mail import send_mail
from django.conf import settings


def send_confirmation_email(email, confirmation_code):
    subject = 'Код подтверждения для регистрации'
    message = f'Ваш код подтверждения: {confirmation_code}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
