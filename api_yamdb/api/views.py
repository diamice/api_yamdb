from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Avg

from reviews.models import Categories, Titles, Genres
from .serializers import (CategoriesSerializer,
                          TitlesSerializer, GenresSerializer)


class CategoriesViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Категорий."""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = []  # will fix it after classes will added
    pagination_class = LimitOffsetPagination


class GenresViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Жанров."""
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = []  # will fix it after classes will added
    pagination_class = LimitOffsetPagination


class TitlesViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Произведений."""
    serializer_class = TitlesSerializer
    permission_classes = []  # will fix it after classes will added
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Titles.objects.annotate(rating=Avg('reviews__score'))
