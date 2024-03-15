from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Categories, Titles, Genres, MyUser
from .permissions import IsAdmin, IsUAuthenticatedAndPatchMethod
from .serializers import (MyUserRegistered, MyUserRegistration,
                          MyUserUsersSerializer, MyUserUsersMePatchSerializer)
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
            serializer.validate(data=serializer.initial_data)
            serializer._validated_data = serializer.initial_data

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
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']


class UsersMeViewSet(RetievePatchViewSet):
    serializer_class = MyUserUsersSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'update':
            return MyUserUsersMePatchSerializer
        return MyUserUsersSerializer

    def get_object(self):
        return get_object_or_404(MyUser.objects.all(),
                                 username=self.request.user.username)
    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(
    #         instance, data=request.data, partial=partial)
    #     serializer.initial_data['username'] = instance.username
    #     serializer.initial_data['email'] = instance.email
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)

    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         instance._prefetched_objects_cache = {}

    #     return Response(serializer.data)


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
            {"username": "Обязательное поле"},
            status=status.HTTP_400_BAD_REQUEST
    )

    user = get_object_or_404(MyUser, username=username)

    if default_token_generator.check_token(user, code):
        token = AccessToken.for_user(user)
        user.is_active = True
        user.save()
        return Response(
            {"token": f"{token}"}, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_400_BAD_REQUEST)
