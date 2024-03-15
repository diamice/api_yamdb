from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from .validators import validate_slug

ROLES_CHOICES = (
    ('admin', 'администратор'),
    ('moderator', 'модератор'),
    ('user', 'пользователь')
)


class MyUser(AbstractUser):
    role = models.CharField(
        'Роль', max_length=16, choices=ROLES_CHOICES, default='user')
    bio = models.TextField('Биография', null=True, blank=True)


User = get_user_model()


class Category(models.Model):
    """Категории (типы) произведений."""
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(validators=[validate_slug],
                            unique=True, max_length=50,
                            verbose_name='slug категории')

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Категории жанров."""
    name = models.CharField(max_length=256, verbose_name='Жанр')
    slug = models.CharField(validators=[validate_slug],
                            unique=True, max_length=50,
                            verbose_name='slug жанра')

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Произведения, к которым пишут отзывы
    (определённый фильм, книга или песенка).
    """
    name = models.CharField(max_length=256,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    genre = models.ManyToManyField(Genre, through='TitleGenre',
                                   verbose_name='slug жанра')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True,
                                 null=True, related_name='titles',
                                 verbose_name='slug категории')

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Связующая модель для произведений и жанров"""
    title = models.ForeignKey(Title, on_delete=models.CASCADE, verbose_name='название произведения')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, verbose_name='название жанра')

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    """Модель отзывов"""
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        verbose_name='Оценка',
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text