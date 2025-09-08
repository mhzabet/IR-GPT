from django.urls import path
from .views import UserDetailView, RegisterUserView, EmailVerificationView, ResendVerificationCodeView, PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView


urlpatterns = [
    path("user/", UserDetailView.as_view(), name="user-detail"),
    path("user/register/", RegisterUserView.as_view(), name="register-user"),
    path("user/verify/", EmailVerificationView.as_view(), name="verify-user"),
    path("user/resend-verify-code/", ResendVerificationCodeView.as_view(), name='resend-verify-code'),
    path("user/request-password-reset/", PasswordResetRequestView.as_view(), name='request-password-reset'),
    path("user/password-reset/", PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path("user/change-password/", ChangePasswordView.as_view(), name='change-password')
]