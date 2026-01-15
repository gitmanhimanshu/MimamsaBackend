from django.urls import path
from .views import (
    AppRegisterView, 
    AppLoginView,
    AppProfileUpdateView,
    CategoryListView,
    AuthorListView,
    AuthorDetailView,
    GenreChoicesView,
    BookListView,
    BookDetailView,
    UploadImageView,
    UploadPDFView,
    UploadTextView,
    FixPDFAccessView
)

urlpatterns = [
    path("app/register/", AppRegisterView.as_view()),
    path("app/login/", AppLoginView.as_view()),
    path("app/profile/<int:pk>/", AppProfileUpdateView.as_view()),
    
    path("categories/", CategoryListView.as_view()),
    path("authors/", AuthorListView.as_view()),
    path("authors/<int:pk>/", AuthorDetailView.as_view()),
    path("genres/", GenreChoicesView.as_view()),
    path("books/", BookListView.as_view()),
    path("books/<int:pk>/", BookDetailView.as_view()),
    
    # Cloudinary Upload Endpoints
    path("upload/image/", UploadImageView.as_view()),
    path("upload/pdf/", UploadPDFView.as_view()),
    path("upload/text/", UploadTextView.as_view()),
    
    # Utility: Fix old PDFs
    path("fix-pdf-access/", FixPDFAccessView.as_view()),
]
