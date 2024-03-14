from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def validate_slug(slug):
    validator = RegexValidator(regex=r'^[-a-zA-Z0-9_]+$',
                           message='Поле "slug" содержит запрещенный символ')
    return validator(slug)
