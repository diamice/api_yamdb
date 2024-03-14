from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CreateUserViewSet, GenreViewSet, get_token,
    ReviewsViewSet, TitleViewSet, UsersViewSet, UsersMeViewSet, CommentsViewSet
)

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet,
    basename='comments',
)
router_v1.register('users', UsersViewSet, basename='users')


urlpatterns = [
    path('v1/users/me/', UsersMeViewSet.as_view(
        {'get': 'retrieve', 'patch': 'update'})
    ),
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', CreateUserViewSet.as_view({'post': 'create'})),
    path('v1/auth/token/', get_token)
]
