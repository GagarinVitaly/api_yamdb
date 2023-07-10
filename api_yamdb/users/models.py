from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models

from .validators import forbidden_usernames_validator, username_validator
from .constants import (
    ADMIN,
    MAX_LEN_CODE,
    MAX_LEN_EMAIL,
    MAX_LEN_ROLE,
    MAX_LEN_USERNAME,
    MODERATOR,
    USER,
    YAMDB_EMAIL,)

CHOICES_ROLE = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),)


class User(AbstractUser):
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль пользователя',
        default=USER,
        max_length=MAX_LEN_ROLE,
        choices=CHOICES_ROLE,)
    confirmation_code = models.CharField(
        'Код подтверждения', blank=True, max_length=MAX_LEN_CODE)
    username = models.CharField(
        unique=True,
        validators=[forbidden_usernames_validator, username_validator],
        max_length=MAX_LEN_USERNAME,)
    email = models.EmailField(
        max_length=MAX_LEN_EMAIL,
        blank=False,
        unique=True,)

    def email_user(
        self,
        message,
        subject='Регистрация',
        from_email=YAMDB_EMAIL,
        **kwargs
    ):
        send_mail(
            subject,
            message,
            from_email,
            [self.email],
            fail_silently=False,
            **kwargs)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', )

    def __str__(self):
        return self.username
