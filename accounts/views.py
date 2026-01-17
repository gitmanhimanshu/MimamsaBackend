from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
import cloudinary.uploader

from .models import AppUser, Category, Author, Book, PasswordResetOTP, PoemCategory, Poem, BookReview, PoemReview
from .serializers import (
    AppUserRegisterSerializer,
    AppUserUpdateSerializer,
    CategorySerializer, 
    AuthorSerializer, 
    BookSerializer
)
from django.db import models


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
        
        # Send email with OTP (with timeout protection)
        print("=== EMAIL CONFIGURATION CHECK ===")
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        print(f"To Email: {email}")
        print("=" * 50)
        
        # Check if credentials are set
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("⚠️ WARNING: Email credentials not configured!")
            print("⚠️ EMAIL_HOST_USER or EMAIL_HOST_PASSWORD is missing")
        
        subject = "Mimanasa - Password Reset OTP"
        message = f"""
Hello {user.username},

You requested to reset your password for your Mimanasa account.

Your OTP is: {otp}

This OTP will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
Mimanasa Team
        """
        
        # ALWAYS print OTP to console for backup
        print(f"\n{'='*50}")
        print(f"🔐 OTP FOR USER: {user.username}")
        print(f"📧 Email: {email}")
        print(f"🔑 OTP Code: {otp}")
        print(f"⏰ Expires: 10 minutes from now")
        print(f"{'='*50}\n")
        
        # Try to send email with timeout protection
        email_sent = False
        email_error_msg = None
        try:
            import socket
            # Set socket timeout to 10 seconds
            socket.setdefaulttimeout(10)
            
            result = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,  # Don't raise exception
            )
            if result > 0:
                email_sent = True
                print(f"✓ Email sent successfully! Result: {result}")
            else:
                print(f"⚠️ Email sending returned 0 - may have failed")
        except Exception as email_error:
            email_error_msg = f"{type(email_error).__name__}: {str(email_error)}"
            print(f"⚠️ Email sending failed: {email_error_msg}")
            # Continue anyway - OTP is saved in database
        finally:
            # Reset socket timeout
            socket.setdefaulttimeout(None)
        
        # Return success regardless of email status
        response_data = {
            "message": "OTP generated successfully. Check your email or contact support.",
            "email": email,
            "email_sent": email_sent,
            "otp_for_testing": otp  # For development/testing
        }
        
        if email_error_msg:
            response_data["email_error"] = email_error_msg
        
        return Response(response_data, status=200)


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


# ============================================
# POEM VIEWS
# ============================================

class PoemCategoryListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all active poem categories"""
        from .serializers import PoemCategorySerializer
        categories = PoemCategory.objects.filter(is_active=True)
        serializer = PoemCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new poem category (admin only)"""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        
        try:
            user = AppUser.objects.get(id=user_id)
            if not user.is_admin:
                return Response({"error": "Admin access required"}, status=403)
        except AppUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        
        from .serializers import PoemCategorySerializer
        serializer = PoemCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PoemListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all active poems with optional filtering"""
        from .serializers import PoemSerializer
        
        poems = Poem.objects.filter(is_active=True)
        
        # Filter by category
        category_id = request.query_params.get('category')
        if category_id:
            poems = poems.filter(category_id=category_id)
        
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
