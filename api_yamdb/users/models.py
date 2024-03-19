from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES_CHOICES = (
    ('admin', 'администратор'),
    ('moderator', 'модератор'),
    ('user', 'пользователь')
)
ADMIN = 'admin'
MODERATOR = 'moderator'


class User(AbstractUser):
    email = models.EmailField(
        ('email address',),
        unique=True,
        error_messages={
            'unique': ('This email has already been registered.'),
        },
    )
    role = models.CharField(
        'Роль',
        max_length=16,
        choices=ROLES_CHOICES,
        default='user'
    )
    bio = models.TextField(
        'Биография',
        null=True,
        blank=True
    )

    def is_admin(self):
        return self.role == ADMIN

    def is_moderator(self):
        return self.role == MODERATOR
