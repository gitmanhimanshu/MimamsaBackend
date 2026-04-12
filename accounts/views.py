from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import cloudinary.uploader
from datetime import datetime

from .models import AppUser, Category, Author, Book, PasswordResetOTP, Poem, BookReview, PoemReview, ShortStory, Audiobook, Video, Image, Like, Comment
from .serializers import (
    AppUserRegisterSerializer,
    AppUserUpdateSerializer,
    CategorySerializer, 
    AuthorSerializer, 
    BookSerializer,
    LikeSerializer,
    CommentSerializer
)
from django.db import models


class HealthCheckView(APIView):
    """
    Health check endpoint to verify server is running
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ Health Check - Server is running! Time: {current_time}")
        
        return Response({
            "status": "success",
            "message": "Server is running successfully! 🚀",
            "timestamp": current_time,
            "server": "Mimanasa Backend API"
        }, status=status.HTTP_200_OK)


class AppRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AppUserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registered successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_admin": user.is_admin
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = AppUser.objects.get(email=email)
        except AppUser.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=400)

        if not check_password(password, user.password):
            return Response({"error": "Invalid credentials"}, status=400)

        return Response({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin,
            "profile_photo": user.profile_photo
        })


# Category Views
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Check if user is admin
        user_id = request.data.get("user_id")
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Author Views
class AuthorListView(APIView):
    def get(self, request):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        user_id = request.data.get("user_id")
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AuthorDetailView(APIView):
    def put(self, request, pk):
        user_id = request.data.get("user_id")
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response({"error": "Author not found"}, status=404)
        
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        user_id = request.data.get("user_id")
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            author = Author.objects.get(pk=pk)
            author.delete()
            return Response({"message": "Author deleted"}, status=200)
        except Author.DoesNotExist:
            return Response({"error": "Author not found"}, status=404)


# Genre Choices View
class GenreChoicesView(APIView):
    def get(self, request):
        """Return all available genre choices"""
        genres = [{"value": choice[0], "label": choice[1]} for choice in Book.GENRE_CHOICES]
        return Response(genres)


class PoemGenreChoicesView(APIView):
    def get(self, request):
        """Return all available poem genre choices"""
        from .models import Poem
        genres = [{"value": choice[0], "label": choice[1]} for choice in Poem.GENRE_CHOICES]
        return Response(genres)


# Book Views
class BookListView(APIView):
    def get(self, request):
        # Check if admin wants to see all books (including inactive)
        show_all = request.query_params.get('show_all', 'false').lower() == 'true'
        
        if show_all:
            books = Book.objects.all().select_related('author', 'category')
        else:
            books = Book.objects.filter(is_active=True).select_related('author', 'category')
        
        # Filter by category
        category_id = request.query_params.get('category')
        if category_id:
            books = books.filter(category_id=category_id)
        
        # Filter by author
        author_id = request.query_params.get('author')
        if author_id:
            books = books.filter(author_id=author_id)
        
        # Filter by genre
        genre = request.query_params.get('genre')
        if genre:
            books = books.filter(genre=genre)
        
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        user_id = request.data.get("user_id")
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class BookDetailView(APIView):
    def get(self, request, pk):
        try:
            book = Book.objects.select_related('author', 'category').get(pk=pk)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=404)
    
    def put(self, request, pk):
        user_id = request.data.get("user_id")
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=404)
        
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        user_id = request.data.get("user_id")
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            book = Book.objects.get(pk=pk)
            book.delete()  # Actually delete from database
            return Response({"message": "Book deleted"}, status=200)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=404)


# Cloudinary Upload Views
class UploadImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Upload image (cover images, author photos) to Cloudinary"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "No file provided"}, status=400)
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                folder="ebook_images",
                resource_type="image"
            )
            
            return Response({
                "url": upload_result['secure_url'],
                "public_id": upload_result['public_id']
            }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class UploadPDFView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Upload PDF/EPUB ebooks to Cloudinary"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "No file provided"}, status=400)
            
            # Upload to Cloudinary as RAW resource type (most reliable for PDFs)
            upload_result = cloudinary.uploader.upload(
                file,
                folder="ebooks",
                resource_type="raw",  # Use raw for reliable PDF delivery
                type="upload",
                access_mode="public"  # Ensure public access
            )
            
            # Get the secure URL
            secure_url = upload_result['secure_url']
            
            return Response({
                "url": secure_url,
                "public_id": upload_result['public_id'],
                "format": upload_result.get('format'),
                "bytes": upload_result.get('bytes'),
                "resource_type": upload_result.get('resource_type')
            }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class UploadTextView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """Upload text files to Cloudinary"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "No file provided"}, status=400)
            
            # Upload to Cloudinary as raw file
            upload_result = cloudinary.uploader.upload(
                file,
                folder="ebook_texts",
                resource_type="raw"
            )
            
            return Response({
                "url": upload_result['secure_url'],
                "public_id": upload_result['public_id']
            }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)



# Profile Update View
class AppProfileUpdateView(APIView):
    def get(self, request, pk):
        """Get user profile"""
        try:
            user = AppUser.objects.get(pk=pk)
            serializer = AppUserUpdateSerializer(user)
            return Response(serializer.data)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
    
    def put(self, request, pk):
        """Update user profile"""
        try:
            user = AppUser.objects.get(pk=pk)
            serializer = AppUserUpdateSerializer(user, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


# UTILITY: Fix old PDFs access mode
class FixPDFAccessView(APIView):
    def post(self, request):
        """Fix access mode for existing PDFs in Cloudinary"""
        try:
            public_id = request.data.get('public_id')
            if not public_id:
                return Response({"error": "public_id required"}, status=400)
            
            # Update access mode using Cloudinary API
            result = cloudinary.api.update(
                public_id,
                resource_type="raw",
                access_mode="public"
            )
            
            return Response({
                "message": "Access mode updated to public",
                "public_id": result.get('public_id'),
                "access_mode": result.get('access_mode')
            }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)



# Forgot Password Views
class ForgotPasswordSendOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Send OTP to user's email for password reset"""
        print("=== FORGOT PASSWORD: SEND OTP ===")
        email = request.data.get('email')
        print(f"Email received: {email}")
        
        if not email:
            print("ERROR: No email provided")
            return Response({"error": "Email is required"}, status=400)
        
        # Check if user exists
        try:
            user = AppUser.objects.get(email=email)
            print(f"✓ User found: {user.username} ({user.email})")
        except AppUser.DoesNotExist:
            print(f"ERROR: No user found with email: {email}")
            return Response({"error": "No account found with this email"}, status=404)
        
        # Generate OTP
        otp = PasswordResetOTP.generate_otp()
        print(f"✓ OTP generated: {otp}")
        
        # Save OTP to database
        otp_record = PasswordResetOTP.objects.create(
            email=email,
            otp=otp
        )
        print(f"✓ OTP saved to database (ID: {otp_record.id})")
        
        # Send email using Brevo API (Production Safe)
        from .email_service import send_otp_email
        
        print("=== SENDING EMAIL VIA BREVO API ===")
        email_sent, email_message = send_otp_email(
            to_email=email,
            otp=otp,
            user_name=user.username
        )
        
        # Always print OTP to console for backup
        print(f"\n{'='*50}")
        print(f"🔐 OTP FOR USER: {user.username}")
        print(f"📧 Email: {email}")
        print(f"🔑 OTP Code: {otp}")
        print(f"✉️ Email Sent: {email_sent}")
        print(f"{'='*50}\n")
        
        # Return success regardless of email status
        return Response({
            "message": "OTP generated successfully. Check your email.",
            "email": email,
            "email_sent": email_sent,
            "otp_for_testing": otp  # For development/testing
        }, status=200)


class ForgotPasswordVerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Verify OTP entered by user"""
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=400)
        
        # Find the latest OTP for this email
        try:
            otp_record = PasswordResetOTP.objects.filter(
                email=email,
                otp=otp,
                is_used=False
            ).latest('created_at')
            
            if not otp_record.is_valid():
                return Response({"error": "OTP has expired"}, status=400)
            
            return Response({
                "message": "OTP verified successfully",
                "email": email
            }, status=200)
            
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)


class ForgotPasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Reset password after OTP verification"""
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not email or not otp or not new_password:
            return Response({
                "error": "Email, OTP, and new password are required"
            }, status=400)
        
        # Verify OTP again
        try:
            otp_record = PasswordResetOTP.objects.filter(
                email=email,
                otp=otp,
                is_used=False
            ).latest('created_at')
            
            if not otp_record.is_valid():
                return Response({"error": "OTP has expired"}, status=400)
            
            # Mark OTP as used
            otp_record.is_used = True
            otp_record.save()
            
            # Update user password
            try:
                user = AppUser.objects.get(email=email)
                user.password = make_password(new_password)
                user.save()
                
                return Response({
                    "message": "Password reset successfully",
                    "email": email
                }, status=200)
                
            except AppUser.DoesNotExist:
                return Response({"error": "User not found"}, status=404)
            
        except PasswordResetOTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)




class PoemListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all active poems with optional filtering"""
        from .serializers import PoemSerializer
        
        poems = Poem.objects.filter(is_active=True)
        
        # Filter by category (string-based)
        category = request.query_params.get('category')
        if category:
            poems = poems.filter(category=category)
        
        # Filter by genre (string-based)
        genre = request.query_params.get('genre')
        if genre:
            poems = poems.filter(genre=genre)
        
        # Filter by author
        author_id = request.query_params.get('author')
        if author_id:
            poems = poems.filter(author_id=author_id)
        
        # Search by title or content
        search = request.query_params.get('search')
        if search:
            poems = poems.filter(
                models.Q(title__icontains=search) | 
                models.Q(content__icontains=search)
            )
        
        serializer = PoemSerializer(poems, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new poem (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        from .serializers import PoemSerializer
        serializer = PoemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PoemDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        """Get single poem details"""
        try:
            from .serializers import PoemSerializer
            poem = Poem.objects.get(pk=pk, is_active=True)
            serializer = PoemSerializer(poem)
            return Response(serializer.data)
        except Poem.DoesNotExist:
            return Response({"error": "Poem not found"}, status=404)
    
    def put(self, request, pk):
        """Update poem (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            from .serializers import PoemSerializer
            poem = Poem.objects.get(pk=pk)
            serializer = PoemSerializer(poem, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Poem.DoesNotExist:
            return Response({"error": "Poem not found"}, status=404)
    
    def delete(self, request, pk):
        """Delete poem (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            poem = Poem.objects.get(pk=pk)
            poem.is_active = False
            poem.save()
            return Response({"message": "Poem deleted successfully"})
        except Poem.DoesNotExist:
            return Response({"error": "Poem not found"}, status=404)


class UserPoemView(APIView):
    """View for users to create and manage their own poems"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all poems by a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            from .serializers import PoemSerializer
            poems = Poem.objects.filter(user_id=user_id, is_active=True)
            serializer = PoemSerializer(poems, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
    
    def post(self, request):
        """Create a new user poem"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        # Create poem data - category is now a string field
        poem_data = {
            'title': request.data.get('title'),
            'content': request.data.get('content'),
            'category': request.data.get('category'),  # Direct string value
            'genre': request.data.get('genre', 'poetry'),
            'language': request.data.get('language', 'Hindi'),
            'background_image_url': request.data.get('background_image_url', ''),
            'user': user_id,
            'author': None,  # User poems don't have author
            'is_approved': True  # Auto-approve for now, can be changed later
        }
        
        from .serializers import PoemSerializer
        serializer = PoemSerializer(data=poem_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserPoemDetailView(APIView):
    """View for users to update/delete their own poems"""
    permission_classes = [AllowAny]
    
    def put(self, request, pk):
        """Update user's own poem"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            poem = Poem.objects.get(pk=pk, user_id=user_id)
        except Poem.DoesNotExist:
            return Response({"error": "Poem not found or you don't have permission"}, status=404)
        
        from .serializers import PoemSerializer
        serializer = PoemSerializer(poem, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        """Delete user's own poem"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            poem = Poem.objects.get(pk=pk, user_id=user_id)
            poem.is_active = False
            poem.save()
            return Response({"message": "Poem deleted successfully"})
        except Poem.DoesNotExist:
            return Response({"error": "Poem not found or you don't have permission"}, status=404)



# ============================================
# REVIEW VIEWS
# ============================================

class BookReviewListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, book_id):
        """Get all reviews for a book"""
        from .serializers import BookReviewSerializer
        reviews = BookReview.objects.filter(book_id=book_id).select_related('user')
        serializer = BookReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    def post(self, request, book_id):
        """Add or update review for a book"""
        user_id = request.data.get("user_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")
        
        if not user_id or not rating:
            return Response({"error": "user_id and rating required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            book = Book.objects.get(id=book_id)
        except (AppUser.DoesNotExist, Book.DoesNotExist):
            return Response({"error": "User or Book not found"}, status=404)
        
        # Check if review already exists
        review, created = BookReview.objects.update_or_create(
            book=book,
            user=user,
            defaults={'rating': rating, 'comment': comment}
        )
        
        from .serializers import BookReviewSerializer
        serializer = BookReviewSerializer(review)
        
        return Response({
            "message": "Review added successfully" if created else "Review updated successfully",
            "review": serializer.data
        }, status=201 if created else 200)


class BookReviewDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, book_id):
        """Get user's review for a book"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            from .serializers import BookReviewSerializer
            review = BookReview.objects.get(book_id=book_id, user_id=user_id)
            serializer = BookReviewSerializer(review)
            return Response(serializer.data)
        except BookReview.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)
    
    def delete(self, request, book_id):
        """Delete user's review"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            review = BookReview.objects.get(book_id=book_id, user_id=user_id)
            review.delete()
            return Response({"message": "Review deleted successfully"})
        except BookReview.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)


class PoemReviewListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, poem_id):
        """Get all reviews for a poem"""
        from .serializers import PoemReviewSerializer
        reviews = PoemReview.objects.filter(poem_id=poem_id).select_related('user')
        serializer = PoemReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    def post(self, request, poem_id):
        """Add or update review for a poem"""
        user_id = request.data.get("user_id")
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")
        
        if not user_id or not rating:
            return Response({"error": "user_id and rating required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            poem = Poem.objects.get(id=poem_id)
        except (AppUser.DoesNotExist, Poem.DoesNotExist):
            return Response({"error": "User or Poem not found"}, status=404)
        
        # Check if review already exists
        review, created = PoemReview.objects.update_or_create(
            poem=poem,
            user=user,
            defaults={'rating': rating, 'comment': comment}
        )
        
        from .serializers import PoemReviewSerializer
        serializer = PoemReviewSerializer(review)
        
        return Response({
            "message": "Review added successfully" if created else "Review updated successfully",
            "review": serializer.data
        }, status=201 if created else 200)


class PoemReviewDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, poem_id):
        """Get user's review for a poem"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            from .serializers import PoemReviewSerializer
            review = PoemReview.objects.get(poem_id=poem_id, user_id=user_id)
            serializer = PoemReviewSerializer(review)
            return Response(serializer.data)
        except PoemReview.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)
    
    def delete(self, request, poem_id):
        """Delete user's review"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            review = PoemReview.objects.get(poem_id=poem_id, user_id=user_id)
            review.delete()
            return Response({"message": "Review deleted successfully"})
        except PoemReview.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)



class UnifiedFeedView(APIView):
    """Get all content types (Books, Poems, Short Stories, Audiobooks, Videos) sorted by creation date - OPTIMIZED with RAW SQL"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.db import connection
        
        # Get pagination parameters
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        user_id = request.query_params.get('user_id')  # Optional: to check if user liked
        
        # Use raw SQL with UNION for maximum performance
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 'book' as type, b.id, b.title, 
                       COALESCE(a.name, 'Unknown') as author_name,
                       b.cover_image_url as cover_image,
                       b.created_at
                FROM accounts_book b
                LEFT JOIN accounts_author a ON b.author_id = a.id
                WHERE b.is_active IS TRUE
                
                UNION ALL
                
                SELECT 'poem' as type, p.id, p.title,
                       COALESCE(a.name, u.username, 'Unknown') as author_name,
                       p.background_image_url as cover_image,
                       p.created_at
                FROM accounts_poem p
                LEFT JOIN accounts_author a ON p.author_id = a.id
                LEFT JOIN accounts_appuser u ON p.user_id = u.id
                WHERE p.is_active IS TRUE AND p.is_approved IS TRUE
                
                UNION ALL
                
                SELECT 'story' as type, s.id, s.title,
                       COALESCE(a.name, u.username, 'Unknown') as author_name,
                       s.cover_image_url as cover_image,
                       s.created_at
                FROM accounts_shortstory s
                LEFT JOIN accounts_author a ON s.author_id = a.id
                LEFT JOIN accounts_appuser u ON s.user_id = u.id
                WHERE s.is_active IS TRUE AND s.is_approved IS TRUE
                
                UNION ALL
                
                SELECT 'audiobook' as type, ab.id, ab.title,
                       COALESCE(a.name, 'Unknown') as author_name,
                       ab.cover_image_url as cover_image,
                       ab.created_at
                FROM accounts_audiobook ab
                LEFT JOIN accounts_author a ON ab.author_id = a.id
                WHERE ab.is_active IS TRUE
                
                UNION ALL
                
                SELECT 'video' as type, v.id, v.title,
                       COALESCE(a.name, 'Unknown') as author_name,
                       v.thumbnail_url as cover_image,
                       v.created_at
                FROM accounts_video v
                LEFT JOIN accounts_author a ON v.author_id = a.id
                WHERE v.is_active IS TRUE
                
                UNION ALL
                
                SELECT 'image' as type, i.id, i.title,
                       COALESCE(a.name, 'Unknown') as author_name,
                       i.image_url as cover_image,
                       i.created_at
                FROM accounts_image i
                LEFT JOIN accounts_author a ON i.author_id = a.id
                WHERE i.is_active IS TRUE
                
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, [limit, offset])
            
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Get total count
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT id FROM accounts_book WHERE is_active IS TRUE
                    UNION ALL
                    SELECT id FROM accounts_poem WHERE is_active IS TRUE AND is_approved IS TRUE
                    UNION ALL
                    SELECT id FROM accounts_shortstory WHERE is_active IS TRUE AND is_approved IS TRUE
                    UNION ALL
                    SELECT id FROM accounts_audiobook WHERE is_active IS TRUE
                    UNION ALL
                    SELECT id FROM accounts_video WHERE is_active IS TRUE
                    UNION ALL
                    SELECT id FROM accounts_image WHERE is_active IS TRUE
                ) as total
            """)
            total = cursor.fetchone()[0]
        
        # Add like and comment counts for each item
        for item in results:
            # Get like count
            like_count = Like.objects.filter(
                content_type=item['type'],
                content_id=item['id']
            ).count()
            item['like_count'] = like_count
            
            # Check if current user liked this
            item['user_liked'] = False
            if user_id:
                item['user_liked'] = Like.objects.filter(
                    content_type=item['type'],
                    content_id=item['id'],
                    user_id=user_id
                ).exists()
            
            # Get comment count
            comment_count = Comment.objects.filter(
                content_type=item['type'],
                content_id=item['id']
            ).count()
            item['comment_count'] = comment_count
            
            # Convert datetime objects to ISO format
            if item['created_at']:
                item['created_at'] = item['created_at'].isoformat()
        
        return Response({
            'total': total,
            'items': results
        })


class AuthorDetailUpdateView(APIView):
    """Get and update author details"""
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
            from .serializers import AuthorSerializer
            return Response(AuthorSerializer(author).data)
        except Author.DoesNotExist:
            return Response({"error": "Author not found"}, status=404)
    
    def put(self, request, pk):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            author = Author.objects.get(pk=pk)
            from .serializers import AuthorSerializer
            serializer = AuthorSerializer(author, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Author.DoesNotExist:
            return Response({"error": "Author not found"}, status=404)


# ============================================
# SHORT STORY VIEWS
# ============================================

class ShortStoryListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all active short stories"""
        from .serializers import ShortStorySerializer
        stories = ShortStory.objects.filter(is_active=True, is_approved=True)
        
        # Filter by genre
        genre = request.query_params.get('genre')
        if genre:
            stories = stories.filter(genre=genre)
        
        # Filter by author
        author_id = request.query_params.get('author')
        if author_id:
            stories = stories.filter(author_id=author_id)
        
        serializer = ShortStorySerializer(stories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new short story (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        from .serializers import ShortStorySerializer
        serializer = ShortStorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ShortStoryDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        """Get single short story"""
        try:
            from .serializers import ShortStorySerializer
            story = ShortStory.objects.get(pk=pk, is_active=True)
            serializer = ShortStorySerializer(story)
            return Response(serializer.data)
        except ShortStory.DoesNotExist:
            return Response({"error": "Story not found"}, status=404)
    
    def put(self, request, pk):
        """Update short story (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            from .serializers import ShortStorySerializer
            story = ShortStory.objects.get(pk=pk)
            serializer = ShortStorySerializer(story, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except ShortStory.DoesNotExist:
            return Response({"error": "Story not found"}, status=404)
    
    def delete(self, request, pk):
        """Delete short story (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            story = ShortStory.objects.get(pk=pk)
            story.is_active = False
            story.save()
            return Response({"message": "Story deleted successfully"})
        except ShortStory.DoesNotExist:
            return Response({"error": "Story not found"}, status=404)


# ============================================
# AUDIOBOOK VIEWS
# ============================================

class AudiobookListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all active audiobooks"""
        from .serializers import AudiobookSerializer
        audiobooks = Audiobook.objects.filter(is_active=True)
        
        # Filter by genre
        genre = request.query_params.get('genre')
        if genre:
            audiobooks = audiobooks.filter(genre=genre)
        
        # Filter by author
        author_id = request.query_params.get('author')
        if author_id:
            audiobooks = audiobooks.filter(author_id=author_id)
        
        serializer = AudiobookSerializer(audiobooks, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new audiobook (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        from .serializers import AudiobookSerializer
        serializer = AudiobookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AudiobookDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        """Get single audiobook"""
        try:
            from .serializers import AudiobookSerializer
            audiobook = Audiobook.objects.get(pk=pk, is_active=True)
            serializer = AudiobookSerializer(audiobook)
            return Response(serializer.data)
        except Audiobook.DoesNotExist:
            return Response({"error": "Audiobook not found"}, status=404)
    
    def put(self, request, pk):
        """Update audiobook (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            from .serializers import AudiobookSerializer
            audiobook = Audiobook.objects.get(pk=pk)
            serializer = AudiobookSerializer(audiobook, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Audiobook.DoesNotExist:
            return Response({"error": "Audiobook not found"}, status=404)
    
    def delete(self, request, pk):
        """Delete audiobook (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            audiobook = Audiobook.objects.get(pk=pk)
            audiobook.is_active = False
            audiobook.save()
            return Response({"message": "Audiobook deleted successfully"})
        except Audiobook.DoesNotExist:
            return Response({"error": "Audiobook not found"}, status=404)


# ============================================
# VIDEO VIEWS
# ============================================

class VideoListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all active videos"""
        from .serializers import VideoSerializer
        videos = Video.objects.filter(is_active=True)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            videos = videos.filter(category=category)
        
        # Filter by author
        author_id = request.query_params.get('author')
        if author_id:
            videos = videos.filter(author_id=author_id)
        
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new video (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        from .serializers import VideoSerializer
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class VideoDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        """Get single video"""
        try:
            from .serializers import VideoSerializer
            video = Video.objects.get(pk=pk, is_active=True)
            serializer = VideoSerializer(video)
            return Response(serializer.data)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=404)
    
    def put(self, request, pk):
        """Update video (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            from .serializers import VideoSerializer
            video = Video.objects.get(pk=pk)
            serializer = VideoSerializer(video, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=404)
    
    def delete(self, request, pk):
        """Delete video (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            video = Video.objects.get(pk=pk)
            video.is_active = False
            video.save()
            return Response({"message": "Video deleted successfully"})
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=404)



# ============================================
# IMAGE VIEWS
# ============================================

class ImageListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all active images"""
        from .serializers import ImageSerializer
        images = Image.objects.filter(is_active=True)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            images = images.filter(category=category)
        
        # Filter by author
        author_id = request.query_params.get('author')
        if author_id:
            images = images.filter(author_id=author_id)
        
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new image (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        from .serializers import ImageSerializer
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ImageDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        """Get single image"""
        try:
            from .serializers import ImageSerializer
            image = Image.objects.get(pk=pk, is_active=True)
            serializer = ImageSerializer(image)
            return Response(serializer.data)
        except Image.DoesNotExist:
            return Response({"error": "Image not found"}, status=404)
    
    def put(self, request, pk):
        """Update image (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            from .serializers import ImageSerializer
            image = Image.objects.get(pk=pk)
            serializer = ImageSerializer(image, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Image.DoesNotExist:
            return Response({"error": "Image not found"}, status=404)
    
    def delete(self, request, pk):
        """Delete image (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        try:
            image = Image.objects.get(pk=pk)
            image.is_active = False
            image.save()
            return Response({"message": "Image deleted successfully"})
        except Image.DoesNotExist:
            return Response({"error": "Image not found"}, status=404)



# ============================================
# LIKE & COMMENT VIEWS
# ============================================

class LikeToggleView(APIView):
    """Toggle like on any content type"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Toggle like (add if not exists, remove if exists)"""
        user_id = request.data.get('user_id')
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        
        if not all([user_id, content_type, content_id]):
            return Response(
                {"error": "user_id, content_type, and content_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if like already exists
        existing_like = Like.objects.filter(
            user=user,
            content_type=content_type,
            content_id=content_id
        ).first()
        
        if existing_like:
            # Unlike
            existing_like.delete()
            return Response({
                "message": "Unliked successfully",
                "liked": False
            }, status=status.HTTP_200_OK)
        else:
            # Like
            like = Like.objects.create(
                user=user,
                content_type=content_type,
                content_id=content_id
            )
            serializer = LikeSerializer(like)
            return Response({
                "message": "Liked successfully",
                "liked": True,
                "like": serializer.data
            }, status=status.HTTP_201_CREATED)


class LikeListView(APIView):
    """Get all likes for a specific content"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get likes for specific content"""
        content_type = request.query_params.get('content_type')
        content_id = request.query_params.get('content_id')
        user_id = request.query_params.get('user_id')  # Optional: check if user liked
        
        if not all([content_type, content_id]):
            return Response(
                {"error": "content_type and content_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        likes = Like.objects.filter(
            content_type=content_type,
            content_id=content_id
        )
        
        # Check if current user liked this content
        user_liked = False
        if user_id:
            user_liked = likes.filter(user_id=user_id).exists()
        
        serializer = LikeSerializer(likes, many=True)
        return Response({
            "count": likes.count(),
            "user_liked": user_liked,
            "likes": serializer.data
        }, status=status.HTTP_200_OK)


class CommentListView(APIView):
    """Get and create comments for any content type"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all comments for specific content"""
        content_type = request.query_params.get('content_type')
        content_id = request.query_params.get('content_id')
        
        if not all([content_type, content_id]):
            return Response(
                {"error": "content_type and content_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comments = Comment.objects.filter(
            content_type=content_type,
            content_id=content_id
        ).order_by('-created_at')
        
        serializer = CommentSerializer(comments, many=True)
        return Response({
            "count": comments.count(),
            "comments": serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new comment"""
        user_id = request.data.get('user_id')
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        text = request.data.get('text')
        
        if not all([user_id, content_type, content_id, text]):
            return Response(
                {"error": "user_id, content_type, content_id, and text are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        comment = Comment.objects.create(
            user=user,
            content_type=content_type,
            content_id=content_id,
            text=text
        )
        
        serializer = CommentSerializer(comment)
        return Response({
            "message": "Comment added successfully",
            "comment": serializer.data
        }, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    """Update and delete specific comment"""
    permission_classes = [AllowAny]
    
    def put(self, request, pk):
        """Update a comment"""
        user_id = request.data.get('user_id')
        text = request.data.get('text')
        
        if not all([user_id, text]):
            return Response(
                {"error": "user_id and text are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user owns this comment
        if comment.user.id != int(user_id):
            return Response(
                {"error": "You can only edit your own comments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment.text = text
        comment.save()
        
        serializer = CommentSerializer(comment)
        return Response({
            "message": "Comment updated successfully",
            "comment": serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Delete a comment"""
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            comment = Comment.objects.get(id=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user owns this comment or is admin
        try:
            user = AppUser.objects.get(id=user_id)
            if comment.user.id != int(user_id) and not user.is_admin:
                return Response(
                    {"error": "You can only delete your own comments"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        comment.delete()
        return Response(
            {"message": "Comment deleted successfully"},
            status=status.HTTP_200_OK
        )
