from rest_framework import serializers
from .models import AppUser, Category, Author, Book, Poem, BookReview, PoemReview
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
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = "__all__"
    
    def get_average_rating(self, obj):
        return obj.average_rating()
    
    def get_review_count(self, obj):
        return obj.review_count()




class PoemSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_photo = serializers.SerializerMethodField()
    category_display = serializers.ReadOnlyField()
    genre_display = serializers.ReadOnlyField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)
    is_user_poem = serializers.SerializerMethodField()
    
    class Meta:
        model = Poem
        fields = "__all__"
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    
    def get_author_photo(self, obj):
        if obj.author:
            return obj.author.photo_url
        elif obj.user:
            return obj.user.profile_photo
        return None
    
    def get_is_user_poem(self, obj):
        return obj.user is not None
    
    def get_average_rating(self, obj):
        return obj.average_rating()
    
    def get_review_count(self, obj):
        return obj.review_count()




class BookReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    user_photo = serializers.URLField(source="user.profile_photo", read_only=True)
    
    class Meta:
        model = BookReview
        fields = "__all__"
        read_only_fields = ('created_at', 'updated_at')


class PoemReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    user_photo = serializers.URLField(source="user.profile_photo", read_only=True)
    
    class Meta:
        model = PoemReview
        fields = "__all__"
        read_only_fields = ('created_at', 'updated_at')



from .models import ShortStory, Audiobook, Video

class ShortStorySerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author_photo = serializers.SerializerMethodField()
    is_user_story = serializers.SerializerMethodField()
    user_name = serializers.CharField(source="user.username", read_only=True)
    
    class Meta:
        model = ShortStory
        fields = "__all__"
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    
    def get_author_photo(self, obj):
        if obj.author:
            return obj.author.photo_url
        elif obj.user:
            return obj.user.profile_photo
        return None
    
    def get_is_user_story(self, obj):
        return obj.user is not None


class AudiobookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    author_photo = serializers.URLField(source="author.photo_url", read_only=True)
    
    class Meta:
        model = Audiobook
        fields = "__all__"


class VideoSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    author_photo = serializers.URLField(source="author.photo_url", read_only=True)
    
    class Meta:
        model = Video
        fields = "__all__"



from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    author_photo = serializers.URLField(source="author.photo_url", read_only=True)
    
    class Meta:
        model = Image
        fields = "__all__"


from .models import Like, Comment

class LikeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    user_photo = serializers.URLField(source="user.profile_photo", read_only=True)
    
    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = ('created_at',)


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    user_photo = serializers.URLField(source="user.profile_photo", read_only=True)
    
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ('created_at', 'updated_at')
