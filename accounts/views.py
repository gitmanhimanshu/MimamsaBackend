from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader

from .models import AppUser, Category, Author, Book
from .serializers import (
    AppUserRegisterSerializer,
    AppUserUpdateSerializer,
    CategorySerializer, 
    AuthorSerializer, 
    BookSerializer
)


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
