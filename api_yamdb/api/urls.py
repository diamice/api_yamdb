from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoriesViewSet, GenresViewSet, ReviewViewSet, TitlesViewSet

router_v1 = DefaultRouter()
router_v1.register('categories', CategoriesViewSet, basename='categories')
router_v1.register('genres', GenresViewSet, basename='genres')
router_v1.register('titles', TitlesViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='title_id',
)

urlpatterns = [
    path('v1/', include(router_v1.urls))
]
