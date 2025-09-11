from django.test import TestCase
from rest_framework.exceptions import ValidationError
from users.models import CustomUser
from users.serializers import BaseUserSerializer, RegisterUserSerializer, ResetPasswordSerializer, PasswordResetRequestSerializer, ChangePasswordSerializer


User = CustomUser
class TestBaseUserSerializer(TestCase):
    
    def setUp(self):
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "preferred_lang": "en",
           
        }
        self.user_instance = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password="testpassword123",
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
            preferred_lang=self.user_data["preferred_lang"],
          
        )
    
    def test_serializer_serializtion(self):
        """Test that the serializer correctly serializes a user instance."""

        serializer = BaseUserSerializer(instance=self.user_instance)
        serialized_data = serializer.data
        self.assertIn('id', serialized_data)
        self.assertEqual(serialized_data['first_name'], self.user_data['first_name'])
        self.assertEqual(serialized_data['last_name'], self.user_data['last_name'])
        self.assertEqual(serialized_data['username'], self.user_data['username'])
        self.assertEqual(serialized_data['email'], self.user_data['email'])
        self.assertEqual(serialized_data['preferred_lang'], self.user_data['preferred_lang'])
        self.assertEqual(serialized_data['is_active'], False) # signals.py set this to False by default
        self.assertTrue(serialized_data['avatar'] is None)
        self.assertNotIn('password', serialized_data)
        self.assertNotIn('password2', serialized_data)
class TestRegisterUserSerializer(TestCase):
    
    def setUp(self):
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'user@mail.com',
            'first_name': 'Test',
            'last_name': 'User',
            'preferred_lang': 'en',
            'avatar': None,
            'password':'TestPass123',
            'password2':'TestPass123',
        }

    def test_valid_data_creates_user(self):
        """Test that valid data creates a user."""
        serializer = RegisterUserSerializer(data=self.valid_user_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.valid_user_data['username'])
        self.assertEqual(user.email, self.valid_user_data['email'])
        self.assertTrue(user.check_password(self.valid_user_data['password']))
        self.assertNotIn(self.valid_user_data['password2'], serializer.data) # check for pop in create method

    def test_password_mismatch(self):
        """Test that password mismatch raises a validation error."""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password2'] = 'DifferentPass123'
        serializer = RegisterUserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
class TestPasswordResetRequestSerializer(TestCase):

    def setUp(self):
        self.mail = "test@mail.com"
        self.user = User.objects.create_user(
            username='existinguser',
            email=self.mail,
            password='TestPass123')
        
    
    def test_valid_email(self):
        """Test that a valid email passes validation."""
        serializer = PasswordResetRequestSerializer(data={'email': self.mail})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['email'], self.mail)
    
    def test_invalid_email(self):
        """Test that an invalid email raises a validation error."""
        serializer = PasswordResetRequestSerializer(data={'email': 'invalid@mail.com'})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn('email', serializer.errors)
