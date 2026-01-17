from django.contrib import admin
from .models import AppUser, Category, Author, Book, PoemCategory, Poem, BookReview, PoemReview

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

@admin.register(PoemCategory)
class PoemCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "is_active", "created_at")
    list_filter = ("is_active",)

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


