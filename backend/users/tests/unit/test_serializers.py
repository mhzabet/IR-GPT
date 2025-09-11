from django.test import TestCase
from rest_framework.exceptions import ValidationError
from users.models import CustomUser
from users.serializers import BaseUserSerializer, RegisterUserSerializer, ResetPasswordSerializer, PasswordResetRequestSerializer, ChangePasswordSerializer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.test import APIRequestFactory
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

class TestResetPasswordSerializer(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        
        cls.user_instance = User.objects.create_user('testuser','user@mail.com', 'testPassword123', is_active=True)

        cls.uidb64 =  urlsafe_base64_encode(force_bytes(cls.user_instance.pk))
        cls.token = PasswordResetTokenGenerator().make_token(cls.user_instance)
    
    def test_serializer_validation(self):
        valid_data = {
            'uidb64' : self.uidb64,
            'token' : self.token,
            'new_password': 'New_Password123',
            'confirm_new_password': 'New_Password123',
        }
        serializer = ResetPasswordSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(user.check_password(valid_data['new_password']))    

    def test_invalid_uidb64(self):

        invalid_data = {
            'uidb64' : self.uidb64 + "invalid",
            'token' : self.token,
            'new_password': 'New_Password123',
            'confirm_new_password': 'New_Password123',
            }
        serializer = ResetPasswordSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid(), serializer.errors)

    def test_invalid_token(self):
        invalid_data = {
            'uidb64' : self.uidb64,
            'token' : self.token + "invalid",
            'new_password': 'New_Password123',
            'confirm_new_password': 'New_Password123',
            }
        serializer = ResetPasswordSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid(), serializer.errors)
    def test_missmatch_password(self):
        invalid_data = {
            'uidb64' : self.uidb64,
            'token' : self.token,
            'new_password': 'New_Password123',
            'confirm_new_password': 'Missmatch_New_Password123',
            }
        serializer = ResetPasswordSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid(), serializer.errors)
class TestChangePasswordSerializer(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser','user@mail.com', 'testPassword123', is_active=True)
        self.factory = APIRequestFactory()
        self.request = self.factory.post('account/user/change-password')
        self.request.user = self.user
    def test_serializer_validation(self):
        data = {
            'old_password':'testPassword123',
            'new_password':'newPassword123',
            'confirm_new_password':'newPassword123',
        }
        serializer = ChangePasswordSerializer(data=data, context={"request":self.request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(user.check_password(data['new_password']))
    def test_missmatch_password(self):
        data = {
            'old_password':'testPassword123',
            'new_password':'newPassword123',
            'confirm_new_password':'diffNewPassword123',
        }
        serializer = ChangePasswordSerializer(data=data, context={"request":self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn("confirm_new_password", serializer.errors)
        self.assertEqual(serializer.errors['confirm_new_password'][0], "Passwords do not match" )
    def test_incorrect_old_password(self):
        data = {
            'old_password':'incorrectTestPassword123',
            'new_password':'newPassword123',
            'confirm_new_password':'newPassword123',
        }
        serializer = ChangePasswordSerializer(data=data, context={"request":self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn("old_password", serializer.errors)
        self.assertEqual(serializer.errors["old_password"][0], "Old password is incorrect")

    def test_password_validation(self):
        data = {
            'old_password':'testPassword123',
            'new_password':'1234',
            'confirm_new_password':'1234',
        }
        serializer = ChangePasswordSerializer(data=data, context={"request":self.request})
        self.assertFalse(serializer.is_valid(), serializer.errors)
        self.assertIn('non_field_errors', serializer.errors)