from django.contrib import admin
from .models import AppUser, Category, Author, Book

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
