from rest_framework import serializers

from reviews.models import Titles, Genres, Categories


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Категорий."""

    class Meta:
        model = Categories
        exclude = ('id',)


class GenresSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Жанров."""

    class Meta:
        model = Genres
        exclude = ('id',)


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
        fields = '__all__'
