from django.contrib import admin

from reviews.models import Category, Genre, Title, Review, Comment
from users.models import User

admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(User)
