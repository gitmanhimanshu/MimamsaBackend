from django.db import models

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
