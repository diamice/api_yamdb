from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from reviews.models import MyUser, Title, Genre, Category, Reviews, Comments


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Произведений."""
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )

    def to_representation(self, instance):
        """Данные о категории и жанре для ответа."""
        representation = super().to_representation(instance)
        representation['category'] = {
            'name': instance.category.name,
            'slug': instance.category.slug,
        }
        representation['genre'] = [{'name': genre.name,
                                    'slug': genre.slug}
                                   for genre in instance.genre.all()]
        return representation


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Отзывов"""
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
        model = Reviews
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs.get('title_id')
        )
        author = self.context['request'].user
        if Reviews.objects.filter(title_id=title, author=author).exists():
            raise serializers.ValidationError(
                'Отзыв уже оставлен'
            )
        return data


class CommentsSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Комментариев"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True,
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date')


class MyUserSerializer(serializers.ModelSerializer):
    """
    Общая модель для сериализаторов работы с пользователями.
    """
    
    email = serializers.RegexField(
        regex=r'^[\w.\-]{1,25}@[\w.\-]+\.[\w]+',
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

        return value


class MyUserUsersSerializer(MyUserSerializer):
    """
    Сериализирует данные для эндпоинта api/users/.
    """

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        

class MyUserUsersMePatchSerializer(MyUserSerializer):
    """
    Сериализирует данные для эндпоинта api/users/.
    """

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio')


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

    def validate(self, data):
        user = MyUser.objects.get(username=data['username'])
        if data['email'] != user.email:
            raise serializers.ValidationError(
                f'Для пользователя {user.username} зарегистрирована '
                'другая электронная почта.'
            )
        return data
