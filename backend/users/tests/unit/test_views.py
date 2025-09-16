from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class TestRegisterUserView(TestCase):

    def setUp(self):
        self.user_data = {
            'first_name':'test',
            'last_name':'user',
            'username':'testuser',
            'email':'test@mail.com',
            'preferred_lang':'en',
            'avatar': '',
            'password':'testPassword!123',
            'password2':'testPassword!123',
        }
        self.client = APIClient()
        self.uri = '/account/user/register/'
    def test_user_register(self):

        response = self.client.post(self.uri, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'User created successfuly. Check you\'r email for verification code.')
    
    def test_duplicate_user_register(self):
        invalid_data = self.user_data.copy()
        invalid_data['username'] = 'existsuser'
        invalid_data['email'] = 'existmail@mail.com'
        User.objects.create_user(invalid_data['username'], invalid_data['email'], 'testPass123!') # create a user to check prevetion from register duplicate user.

        response = self.client.post(self.uri, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
class TestRestPasswordView(TestCase):

    def setUp(self):
        self.data = {
            'email': 'test@mail.com'
        }
        User.objects.create_user(
            'testuser',
            self.data['email'],
            'testPassword123!'
        )
        self.client = APIClient()
        self.reset_uri = '/account/user/request-password-reset/'

    def test_password_request(self):
        response = self.client.post(self.reset_uri, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password reset link sent to your email.')
    
    def test_valid_email(self):
        invalid_data = self.data.copy()
        invalid_data['email'] = 'invalid@mail.com'
        response = self.client.post(self.reset_uri, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestChangePasswordView(TestCase):
    
    def setUp(self):

        self.data = {
            "old_password":"Old_Pass123",
            "new_password":"New_Pass123",
            "confirm_new_password": "New_Pass123"
        }
        self.user = User.objects.create_user(
            'testuser', 'test@mail.com', self.data['old_password']
        )
        self.client = APIClient()
        self.uri = '/account/user/change-password/'
    def test_change_validation(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.uri, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password changed successfully.')
    
    def test_mismatch_password(self):
        self.client.force_authenticate(user=self.user)

        invalid_data = self.data.copy()
        invalid_data['new_password'] = 'FakeNew_Pass123'
        response = self.client.post(self.uri, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_password(self):
        
        self.client.force_authenticate(user=self.user)

        invalid_data = self.data.copy()
        invalid_data['old_password'] = 'FakeNew_Pass123'
        response = self.client.post(self.uri, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
