from django.contrib import admin
from .models import AppUser,Image, Category, Author, Book, Poem, BookReview, PoemReview

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_admin", "created_at")
    readonly_fields = ("created_at",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "genre", "is_paid", "price", "is_active")
    list_filter = ("category", "genre", "is_paid", "is_active")


@admin.register(Poem)
class PoemAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "language", "is_active", "created_at")
    list_filter = ("category", "language", "is_active")
    search_fields = ("title", "content", "author__name")

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("book__title", "user__username", "comment")

@admin.register(PoemReview)
class PoemReviewAdmin(admin.ModelAdmin):
    list_display = ("poem", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("poem__title", "user__username", "comment")




from .models import ShortStory, Audiobook, Video

@admin.register(ShortStory)
class ShortStoryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "user", "genre", "reading_time", "is_active", "created_at")
    list_filter = ("genre", "language", "is_active", "is_approved")
    search_fields = ("title", "content", "author__name", "user__username")

@admin.register(Audiobook)
class AudiobookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "narrator", "genre", "duration", "is_paid", "is_active", "created_at")
    list_filter = ("genre", "language", "is_paid", "is_active")
    search_fields = ("title", "description", "author__name", "narrator")

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "duration", "is_active", "created_at")
    list_filter = ("category", "language", "is_active")
    search_fields = ("title", "description", "author__name")



@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'language', 'is_active', 'created_at')
    list_filter = ('category', 'language', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'tags')
    readonly_fields = ('created_at', 'updated_at')
