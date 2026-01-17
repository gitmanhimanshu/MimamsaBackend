from django.db import models
import random
from datetime import timedelta
from django.utils import timezone

class AppUser(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    profile_photo = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"OTP for {self.email} - {self.otp}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    photo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    GENRE_CHOICES = [
        ('romance', 'Romance'),
        ('drama', 'Drama'),
        ('thriller', 'Thriller'),
        ('mystery', 'Mystery'),
        ('horror', 'Horror'),
        ('comedy', 'Comedy'),
        ('action', 'Action'),
        ('adventure', 'Adventure'),
        ('fantasy', 'Fantasy'),
    ]
    
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('epub', 'EPUB'),
        ('mobi', 'MOBI'),
        ('txt', 'Text'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    content_url = models.URLField(blank=True, null=True)  # Single field for PDF/EPUB/MOBI/any file
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='pdf', blank=True)
    language = models.CharField(max_length=50, default="Hindi", blank=True)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    published_year = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.book_reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def review_count(self):
        return self.book_reviews.count()


class PoemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default="📝")  # Emoji icon
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Poem Categories"

    def __str__(self):
        return self.name


class Poem(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()  # The actual poem text
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="poems")
    category = models.ForeignKey(PoemCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="poems")
    language = models.CharField(max_length=50, default="Hindi")
    background_image_url = models.URLField(blank=True, null=True)  # Optional background image
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.poem_reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def review_count(self):
        return self.poem_reviews.count()


class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_reviews")
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="book_reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('book', 'user')  # One review per user per book
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}★)"


class PoemReview(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, related_name="poem_reviews")
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="poem_reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('poem', 'user')  # One review per user per poem
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.poem.title} ({self.rating}★)"


