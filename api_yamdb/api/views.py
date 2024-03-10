from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Categories, Titles, Genres, MyUser
from .permissions import IsAdmin, IsUAuthenticatedAndPatchMethod
from .serializers import MyUserRegistration, MyUserUsersSerializer
from .viewsets import CreateViewSet, ListCreateViewSet, RetievePatchViewSet


class CategoriesViewSet(viewsets.ModelViewSet):
    pass


class GenresViewSet(viewsets.ModelViewSet):
    pass


class TitlesViewSet(viewsets.ModelViewSet):
    pass


class CreateUserViewSet(CreateViewSet):
    """
    Создает нового пользователя через API (эндпоинт api/v1/auth/signup/).
    """

    queryset = MyUser.objects.all()
    serializer_class = MyUserRegistration
    permission_classes = (AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        username = request.data.get('username')
        email = request.data.get('email')
        user = get_object_or_404(MyUser, username=username)
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
