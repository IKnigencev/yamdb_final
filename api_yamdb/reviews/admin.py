from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import User, Title, Genre, Category, Review, Comment


admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Comment)

admin.site.register(User, UserAdmin)
