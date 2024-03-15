from rest_framework import mixins, viewsets, filters
from rest_framework.pagination import LimitOffsetPagination

from .permissions import ReadOrAdminOnly


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class ListCreateViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class RetievePatchViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    pass


class CreateDestroyListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                               mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (ReadOrAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'
