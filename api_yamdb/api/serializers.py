from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from reviews.models import Title, Genre, Category, Review, Comment
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Категорий."""

    class Meta:
        model = Category
        exclude = ('id', )


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Жанров."""

    class Meta:
        model = Genre
        exclude = ('id', )


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
        fields = '__all__'

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


class ReviewSerializer(serializers.ModelSerializer):
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
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title = get_object_or_404(
            Title, pk=self.context['view'].kwargs.get('title_id')
        )
        author = self.context['request'].user
        if Review.objects.filter(title_id=title, author=author).exists():
            raise serializers.ValidationError(
                'Отзыв уже оставлен'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Комментариев"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    """
    Общая модель для сериализаторов работы с пользователями.
    """
    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в качестве "username"')

        return value


class UsersSerializer(UserSerializer):
    """
    Сериализатор для управления информацией о пользователе.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UsersMePatchSerializer(UserSerializer):
    """
    Сериализатор для редактирования своих данных пользователем.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio')


class UserRegistration(UserSerializer):
    """
    Сериализатор для создания пользователя.
    """

    class Meta:
        model = User
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('email', 'username'),
                message='Пользователь уже зарегистрирован.'
            )
        ]


class UserRegistered(serializers.Serializer):
    """
    Сериализатор для получения кода подтверждения зарегистрированным 
    ранее пользователем.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate(self, data):
        user = User.objects.get(username=data['username'])
        if data['email'] != user.email:
            raise serializers.ValidationError(
                f'Для пользователя {user.username} зарегистрирована '
                'другая электронная почта.'
            )
        return data
