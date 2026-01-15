from rest_framework import serializers
from .models import AppUser, Category, Author, Book
from django.contrib.auth.hashers import make_password

class AppUserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ("id", "email", "username", "password", "is_admin", "profile_photo")
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        validated_data["password"] = make_password(
            validated_data["password"]
        )
        return super().create(validated_data)


class AppUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ("id", "email", "username", "profile_photo", "is_admin")
        read_only_fields = ("id", "is_admin")

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    genre_display = serializers.CharField(source="get_genre_display", read_only=True)
    
    class Meta:
        model = Book
        fields = "__all__"
