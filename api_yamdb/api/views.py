from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Avg

from reviews.models import Categories, Titles, Genres
from .serializers import (CategoriesSerializer,
                          TitlesSerializer, GenresSerializer)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = []
    pagination_class = LimitOffsetPagination


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = []
    pagination_class = LimitOffsetPagination


class TitlesViewSet(viewsets.ModelViewSet):
    serializer_class = TitlesSerializer
    permission_classes = []
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Titles.objects.annotate(rating=Avg('reviews__score'))
