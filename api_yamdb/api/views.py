from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import IsAuthorAdminModeratorOrReadOnly
from reviews.models import Categories, Titles, Genres
from .serializers import ReviewSerializer


class CategoriesViewSet(viewsets.ModelViewSet):
    pass


class GenresViewSet(viewsets.ModelViewSet):
    pass


class TitlesViewSet(viewsets.ModelViewSet):
    pass


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(
            Titles,
            id=title_id,
        )
        return title.reviews.all()
    
    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(
            Titles,
            id=title_id,
        )
        serializer.save(author=self.request.user, title=title)
