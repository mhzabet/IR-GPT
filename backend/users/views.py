from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import CustomUser
from .utils import generate_secure_otp

class RegisterUserView(APIView):
    pass