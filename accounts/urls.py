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
    FixPDFAccessView,
    ForgotPasswordSendOTPView,
    ForgotPasswordVerifyOTPView,
    ForgotPasswordResetView,
    PoemCategoryListView,
    PoemListView,
    PoemDetailView,
    BookReviewListView,
    BookReviewDetailView,
    PoemReviewListView,
    PoemReviewDetailView
)

urlpatterns = [
    path("app/register/", AppRegisterView.as_view()),
    path("app/login/", AppLoginView.as_view()),
    path("app/profile/<int:pk>/", AppProfileUpdateView.as_view()),
    
    # Forgot Password
    path("app/forgot-password/send-otp/", ForgotPasswordSendOTPView.as_view()),
    path("app/forgot-password/verify-otp/", ForgotPasswordVerifyOTPView.as_view()),
    path("app/forgot-password/reset/", ForgotPasswordResetView.as_view()),
    
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
    
    # Poem Endpoints
    path("poem-categories/", PoemCategoryListView.as_view()),
    path("poems/", PoemListView.as_view()),
    path("poems/<int:pk>/", PoemDetailView.as_view()),
    
    # Review Endpoints
    path("books/<int:book_id>/reviews/", BookReviewListView.as_view()),
    path("books/<int:book_id>/reviews/user/", BookReviewDetailView.as_view()),
    path("poems/<int:poem_id>/reviews/", PoemReviewListView.as_view()),
    path("poems/<int:poem_id>/reviews/user/", PoemReviewDetailView.as_view()),
]
