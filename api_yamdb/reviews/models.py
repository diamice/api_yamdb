from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('admin', 'администратор'),
    ('moderator', 'модератор'),
    ('user', 'пользователь')
)


class MyUser(AbstractUser):
    role = models.CharField(
        'Роль', max_length=16, choices=CHOICES, default='user')
    bio = models.TextField('Биография',null=True, blank=True)


class Categories(models.Model):
    pass


class Genres(models.Model):
    pass


class Titles(models.Model):
    pass
