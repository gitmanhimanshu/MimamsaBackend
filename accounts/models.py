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
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index

    def __str__(self):
        return self.title

    def average_rating(self):
        reviews = self.book_reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def review_count(self):
        return self.book_reviews.count()




class Poem(models.Model):
    GENRE_CHOICES = [
        ('poetry', 'Poetry'),
        ('classical_poetry', 'Classical Poetry'),
        ('modern_poetry', 'Modern Poetry'),
        ('ghazal', 'Ghazal'),
        ('free_verse', 'Free Verse'),
    ]
    
    CATEGORY_CHOICES = [
        ('love', 'प्रेम कविता'),
        ('nature', 'प्रकृति'),
        ('patriotic', 'देशभक्ति'),
        ('spiritual', 'आध्यात्मिक'),
        ('social', 'सामाजिक'),
        ('motivational', 'प्रेरणादायक'),
        ('sad', 'दुःख'),
        ('funny', 'हास्य'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True, help_text="Short description or summary of the poem")
    content = models.TextField()  # The actual poem text
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="poems")  # For admin-added poems
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True, related_name="user_poems")  # For user-created poems
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)  # Changed to CharField
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='poetry')
    language = models.CharField(max_length=50, default="Hindi")
    background_image_url = models.URLField(blank=True, null=True)  # Optional background image
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)  # Admin can approve user poems
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'is_active', 'is_approved']),
        ]

    def __str__(self):
        return self.title

    def get_author_name(self):
        """Returns author name (either from Author model or AppUser)"""
        if self.author:
            return self.author.name
        elif self.user:
            return self.user.username
        return "Unknown"
    
    @property
    def genre_display(self):
        """Returns human-readable genre name"""
        return dict(self.GENRE_CHOICES).get(self.genre, self.genre)
    
    @property
    def category_display(self):
        """Returns human-readable category name"""
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

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




class ShortStory(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
        ('horror', 'Horror'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('fantasy', 'Fantasy'),
        ('thriller', 'Thriller'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField()  # The actual story text
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="short_stories")
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True, related_name="user_stories")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='fiction')
    language = models.CharField(max_length=50, default="Hindi")
    cover_image_url = models.URLField(blank=True, null=True)
    reading_time = models.IntegerField(default=5, help_text="Estimated reading time in minutes")
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Short Stories"
        indexes = [
            models.Index(fields=['-created_at', 'is_active', 'is_approved']),
        ]

    def __str__(self):
        return self.title

    def get_author_name(self):
        """Returns author name (either from Author model or AppUser)"""
        if self.author:
            return self.author.name
        elif self.user:
            return self.user.username
        return "Unknown"


class Audiobook(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('biography', 'Biography'),
        ('self_help', 'Self Help'),
        ('business', 'Business'),
        ('history', 'History'),
        ('science', 'Science'),
        ('poetry', 'Poetry'),
        ('drama', 'Drama'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="audiobooks")
    narrator = models.CharField(max_length=150, blank=True, help_text="Name of the narrator")
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='fiction')
    cover_image_url = models.URLField(blank=True, null=True)
    audio_url = models.URLField(help_text="URL to the audio file")
    duration = models.IntegerField(default=0, help_text="Duration in minutes")
    language = models.CharField(max_length=50, default="Hindi")
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'is_active']),
        ]

    def __str__(self):
        return self.title


class Video(models.Model):
    CATEGORY_CHOICES = [
        ('literature', 'Literature'),
        ('poetry_reading', 'Poetry Reading'),
        ('author_interview', 'Author Interview'),
        ('book_review', 'Book Review'),
        ('writing_tips', 'Writing Tips'),
        ('storytelling', 'Storytelling'),
        ('documentary', 'Documentary'),
        ('educational', 'Educational'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="videos")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='literature')
    thumbnail_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(help_text="URL to the video file or YouTube link")
    duration = models.IntegerField(default=0, help_text="Duration in minutes")
    language = models.CharField(max_length=50, default="Hindi")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added index
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'is_active']),
        ]

    def __str__(self):
        return self.title


class Image(models.Model):
    CATEGORY_CHOICES = [
        ('book_cover', 'Book Cover'),
        ('author_photo', 'Author Photo'),
        ('illustration', 'Illustration'),
        ('artwork', 'Artwork'),
        ('calligraphy', 'Calligraphy'),
        ('manuscript', 'Manuscript'),
        ('historical', 'Historical'),
        ('cultural', 'Cultural'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="images")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    image_url = models.URLField(help_text="URL to the image file")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    language = models.CharField(max_length=50, default="Hindi")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'is_active']),
        ]

    def __str__(self):
        return self.title


class Like(models.Model):
    """Universal Like model for all content types"""
    CONTENT_TYPE_CHOICES = [
        ('book', 'Book'),
        ('poem', 'Poem'),
        ('story', 'Short Story'),
        ('audiobook', 'Audiobook'),
        ('video', 'Video'),
        ('image', 'Image'),
    ]
    
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="likes")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    content_id = models.IntegerField()  # ID of the liked content
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('user', 'content_type', 'content_id')  # One like per user per content
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['user', 'content_type']),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.content_type} #{self.content_id}"


class Comment(models.Model):
    """Universal Comment model for all content types"""
    CONTENT_TYPE_CHOICES = [
        ('book', 'Book'),
        ('poem', 'Poem'),
        ('story', 'Short Story'),
        ('audiobook', 'Audiobook'),
        ('video', 'Video'),
        ('image', 'Image'),
    ]
    
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="comments")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    content_id = models.IntegerField()  # ID of the commented content
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} commented on {self.content_type} #{self.content_id}"
