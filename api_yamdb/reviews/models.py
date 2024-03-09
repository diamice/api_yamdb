from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class Categories(models.Model):
    """Категории (типы) произведений."""
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(unique=True, max_length=50,
                            verbose_name='slug категории')

    def __str__(self):
        return self.name


class Genres(models.Model):
    """Категории жанров."""
    name = models.CharField(max_length=256, verbose_name='Жанр')
    slug = models.CharField(unique=True, max_length=50,
                            verbose_name='slug жанра')

    def __str__(self):
        return self.name


class Titles(models.Model):
    """
    Произведения, к которым пишут отзывы
    (определённый фильм, книга или песенка).
    """
    name = models.CharField(max_length=256,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(verbose_name='Описание')
    genre = models.ManyToManyField(Genres, related_name='titles',
                                   verbose_name='slug жанра')
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL,
                                 null=True, related_name='titles',
                                 verbose_name='slug категории')

    def __str__(self):
        return self.name


class Reviews(models.Model):
    """Модель отзывов"""
    text = models.TextField(
        verbose_name='Текст отзыва',
    )
    title = models.ForeignKey(
        Titles,
        max_length=200,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )
    author = models.ForeignKey(
        User,
        max_length=200,
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
        ordering = ['-pub_date'],
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            )
        ]

    def __str__(self):
        return self.text
