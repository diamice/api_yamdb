from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Avg

from .permissions import IsAuthorAdminModeratorOrReadOnly
from reviews.models import Categories, Titles, Genres
from .serializers import ReviewsSerializer
from .serializers import (CategoriesSerializer,TitlesSerializer,
                          GenresSerializer, ReviewsSerializer)


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


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Titles, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())
