from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Title, Genre, Review
from users.models import User
from .permissions import (IsAdmin,
                          IsAuthorAdminModeratorOrReadOnly, ReadOrAdminOnly)
from .serializers import (CategorySerializer, TitleSerializer,
                          GenreSerializer, UserRegistered,
                          UserRegistration, UsersSerializer,
                          ReviewSerializer, CommentSerializer,
                          UsersMePatchSerializer)
from .filters import TitleFilter
from .viewsets import CreateDestroyListViewSet


class CategoryViewSet(CreateDestroyListViewSet):
    """ViewSet для модели Категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination


class GenreViewSet(CreateDestroyListViewSet):
    """ViewSet для модели Жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Произведений."""
    serializer_class = TitleSerializer
    permission_classes = [ReadOrAdminOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_queryset(self):
        return Title.objects.annotate(rating=Avg('reviews__score'))


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Комментариев."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User.objects.all(),
                                    username=request.user.username)
        if request._request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = UsersMePatchSerializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """
    Генерирует токен через эндпоинт api/v1/auth/token/.
    """

    username = request.data.get('username')
    code = request.data.get('confirmation_code')

    if username is None:
        return Response(
            {'username': 'Обязательное поле'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, code):
        token = AccessToken.for_user(user)
        user.is_active = True
        user.save()
        return Response(
            {'token': f'{token}'}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """
    Создает нового пользователя через API (эндпоинт api/v1/auth/signup/).
    """
    username = request.data.get('username')
    email = request.data.get('email')
    if User.objects.filter(username=username).exists():
        serializer = UserRegistered(data=request.data)
        serializer.is_valid(raise_exception=True)
    else:
        serializer = UserRegistration(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(
                role='user',
                is_active=False
            )

    user = get_object_or_404(User.objects.all(), username=username)
    code = default_token_generator.make_token(user)

    send_mail(
        subject='Код аутентификации для yamdb',
        message=f'username: {username}, confirmation_code:{code}',
        from_email='registration@yamdb.not',
        recipient_list=[email],
        fail_silently=False,
    )

    if serializer.errors:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data, status=status.HTTP_200_OK)
