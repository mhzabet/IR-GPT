from django.test import TestCase
from rest_framework.test import APIClient
from users.views import RegisterUserView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import cache
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

class TestEmailVerficationView(TestCase):

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
        self.uri = '/account/user/verify/'
        cache.clear()
    
    def test_user_verification_email(self):
        register = self.client.post('/account/user/register/', data=self.user_data)
        code = cache.get(f"code:{self.user_data['email']}")
        data = {
            'email': self.user_data['email'],
            'code':code
        }
        verify = self.client.post(self.uri,data=data)
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        self.assertEqual(verify.data['datail'], 'Account verified successfully.')