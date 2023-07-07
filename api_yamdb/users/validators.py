import datetime

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

username_validator = UnicodeUsernameValidator()


def forbidden_usernames_validator(value):
    """Определение списка запрещенных имен."""
    forbidden_usernames = ['me', ]
    if value.lower() in forbidden_usernames:
        raise ValidationError(
            _('Это имя нельзя использовать.'),
            params={'value': value},)


def current_year():
    """Определение текущего года."""
    return datetime.date.today().year
