from rest_framework import mixins, viewsets, filters

from .permissions import ReadOrAdminOnly


class CreateDestroyListViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (ReadOrAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
