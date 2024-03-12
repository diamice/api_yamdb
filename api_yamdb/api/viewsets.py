from rest_framework import mixins, viewsets


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class ListCreateViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class RetievePatchViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    pass
