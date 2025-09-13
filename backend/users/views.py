from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.http import Http404
from django.conf import settings
from django.core.cache import cache
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site

from .serializers import RegisterUserSerializer, BaseUserSerializer, PasswordResetRequestSerializer, ResetPasswordSerializer, ChangePasswordSerializer
from .thorttlings import ResendVerificationThrottle
from .utils import generate_secure_verification_code



User = get_user_model()
class RegisterUserView(APIView):
    def post(self, request, format=None):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            verification_code = generate_secure_verification_code()
            # set code in cache
            cache.set(f"code:{user.email}", verification_code, timeout=600)
            cache.set(f"user-email", user.email, timeout=12000)
            # send mail to user email.
            send_mail(
                subject="Verify your email",
                message=f"You'r verification code is {verification_code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({'detail':'User created successfuly. Check you\'r email for verification code.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        user = request.user
        serializer = BaseUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ResendVerificationCodeView(APIView):
    throttle_classes = [ResendVerificationThrottle]

    def post(self, request, format=None):
        email = request.data.get("email",'').strip().lower()
        if not email:
            return Response({'detail':'Email address is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({'detail':'Email address is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            
            new_verification_code = generate_secure_verification_code()
            # delete perv cache and add a new one.
            cache_key = f"code:{user.email}"
            attempts_key = f"attempts:{user.email}"

            current_attempts = cache.get(attempts_key, 0)
            if current_attempts >= 5:
                return Response({'detail':'Maximum verification attempts reached. Please try agian later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            if cache.get(cache_key):
                cache.delete(cache_key)
            
            cache.set(cache_key, new_verification_code, timeout=600)
            cache.set(attempts_key, current_attempts + 1, timeout=3600) # 1 hour for attempts counter.
            send_mail(
                subject="Verify your email",
                message=f"You'r verification code is {new_verification_code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({'detail':'Verification code resent successfuly. Check you\'r email for verification code.',
                            'attempts_remaining': 5 - (current_attempts + 1),
                            'email':user.email}, 
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail':'Email not registerd. Please sign up first.'}, status=status.HTTP_400_BAD_REQUEST)
class EmailVerificationView(APIView):
    def post(self, request, format=None):
        email = request.data.get("email")
        code = request.data.get("code")

        saved_code = cache.get(f"code:{email}")
        if saved_code and int(saved_code) == int(code):
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()

                cache.delete(f"code:{email}")
                return Response({"datail":"Account verified successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"datail":"Provided user is not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail":"Provided verification code may invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    def post(self, request, format=None):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # generate token for reset password request
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request)

            # This path must be changed!!! [IMPORTANT]
            reset_path = f'http://{current_site}/reset-password/{uidb64}/{token}' # <-- when front-end is developed we must change it to the hanlder page.
            
            # send mail
            send_mail(
                subject="Reset you'r password.",
                message=f"Click here for reset your password: {reset_path}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email]
            )
            return Response({'detail':'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail':'The provided email is not found.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request, format=None):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail':'Password reset successfully.'}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail':'Password changed successfully.'}, status=status.HTTP_200_OK)