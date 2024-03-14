from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, Title, Genre, MyUser
from .permissions import (IsAdmin, IsUAuthenticatedAndPatchMethod,
                          IsAuthorAdminModeratorOrReadOnly, ReadOrAdminOnly)
from .serializers import (
    CategorySerializer, TitleSerializer, GenreSerializer,
    MyUserRegistered, MyUserRegistration, MyUserUsersSerializer,
    ReviewsSerializer, CommentsSerializer)
from .filters import TitleFilter
from .viewsets import CreateViewSet, ListCreateViewSet, RetievePatchViewSet, CreateDestroyListViewSet
from .permissions import IsAuthorAdminModeratorOrReadOnly


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


class ReviewsViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Отзывов."""
    serializer_class = ReviewsSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Комментариев."""
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(Reviews, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class CreateUserViewSet(CreateViewSet):
    """
    Создает нового пользователя через API (эндпоинт api/v1/auth/signup/).
    """

    queryset = MyUser.objects.all()
    serializer_class = MyUserRegistration
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        username = self.request.data.get('username')
        if MyUser.objects.filter(username=username).exists():
            return MyUserRegistered
        return MyUserRegistration

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        username = request.data.get('username')
        email = request.data.get('email')

        if not MyUser.objects.filter(username=username).exists():
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        else:
            serializer.is_valid(raise_exception=True)

        headers = self.get_success_headers(serializer.data)
        user = get_object_or_404(MyUser.objects.all(), username=username)
        code = default_token_generator.make_token(user)

        send_mail(
            subject='Код аутентификации для yamdb',
            message=f'username: {username}, confirmation_code:{code}',
            from_email='registration@yamdb.not',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            role='user',
            is_active=False
        )


class UsersViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = MyUserUsersSerializer
    permission_classes = (IsAdmin,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


class UsersMeViewSet(RetievePatchViewSet):
    serializer_class = MyUserUsersSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(MyUser.objects.all(),
                                 username=self.request.user.username)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """
    Генерирует токен через эндпоинт api/v1/auth/token/.
    """

    username = request.data.get('username')
    code = request.data.get('confirmation_code')
    user = get_object_or_404(MyUser, username=username)

    if default_token_generator.check_token(user, code):
        token = AccessToken.for_user(user)
        user.is_active = True
        user.save()
        return Response({"token": f"{token}"}, status.HTTP_200_OK)

    return Response(status.HTTP_400_BAD_REQUEST)
