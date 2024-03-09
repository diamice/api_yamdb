from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class Categories(models.Model):
    pass


class Genres(models.Model):
    pass


class Titles(models.Model):
    pass


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
