from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from reviews.models import MyUser, Titles, Genres, Categories, Reviews


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Категорий."""

    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Жанров."""

    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Произведений."""
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all()
    )
    genres = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genres.objects.all(), many=True
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Titles
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        many=False,
        read_only=True,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Reviews


class MyUserSerializer(serializers.ModelSerializer):
    """
    Общая модель для сериализаторов работы с пользователями.
    """
    
    email = serializers.CharField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(
                queryset=MyUser.objects.all(),
                message=(
                    'Пользователь с данной электронной почтой '
                    'уже зарегистрирован.'
                )
            )
        ]
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(
                queryset=MyUser.objects.all(),
                message='Пользователь с данным username уже зарегистрирован.'
            )
        ]
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве "username"')

        if (
            not self.context['request'].data.get('username')
            or self.context['request'].data.get('username') == ''
            or self.context['request'].data.get('username') == None
        ):
            return Response(
                {"username": ["Это поле не может быть пустым."]},
                status=status.HTTP_400_BAD_REQUEST
                # 'Поле "username" не может быть пустым.'
                # 'оно не соответствует требованиям'
            )

        return value

    def validate_email(self, value):
        if (
            not self.context['request'].data.get('email')
            or self.context['request'].data.get('email') == ''
            or self.context['request'].data.get('email') == None
        ):
            return Response(
                {"email": ["Это поле не может быть пустым."]},
                status=status.HTTP_400_BAD_REQUEST
            )
            # raise serializers.ValidationError(
            #     'Поле "email" не можеты быть пустым.'
            #     # 'оно не соответствует требованиям'
            # )

        return value


class MyUserUsersSerializer(MyUserSerializer):
    """
    Сериализирует данные для эндпоинта api/users/.
    """

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class MyUserRegistration(MyUserSerializer):
    """
    Сериализует данные для эндпоинта api/v1/auth/signup/.
    """

    class Meta:
        model = MyUser
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=MyUser.objects.all(),
                fields=('email', 'username'),
                message='Пользователь уже зарегистрирован.'
            )
        ]


class MyUserRegistered(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ('email', 'username')

    def validate_email(self, value):
        username = self.context['request'].data.get('username')
        user = MyUser.objects.get(username=username)
        if value != user.email:
            raise serializers.ValidationError(
                f'Для пользователя {username} зарегистрирована '
                'другая электронная почта.'
            )
