from django.urls import path
from .views import UserDetailView, RegisterUserView, EmailVerificationView, ResendVerificationCodeView
urlpatterns = [
    path("user/<int:pk>", UserDetailView.as_view(), name="user-detail"),
    path("user/register/", RegisterUserView.as_view(), name="register-user"),
    path("user/verify/", EmailVerificationView.as_view(), name="verify-user"),
    path("user/resend-verify-code/", ResendVerificationCodeView.as_view(), name='resend-verify-code')
]