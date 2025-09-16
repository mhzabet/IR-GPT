from django.test import TestCase
from rest_framework.test import APIClient
from django.core.cache import cache
from rest_framework import status
class TestAuthFlowIntegration(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.data = {
            'username':'testuser',
            'email':'test@mail.com',
            'first_name': 'test',
            'last_name': 'user',
            'avatar': '',
            'preferred_lang': 'en',
            'password': 'Test_Pass123',
            'password2': 'Test_Pass123'
        }
        self.register_uri = '/account/user/register/'
        self.auth_uri = '/api/token/'
        self.verify_token_uri = '/api/token/verify/'
        self.email_verification_uri = '/account/user/verify/'
        cache.clear()
    def test_full_auth(self):
        register_response = self.client.post(self.register_uri, data=self.data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        code = cache.get(f'code:{self.data["email"]}')
        email_data = {
            'email': self.data['email'],
            'code': code
        }
        email_verifcation_response = self.client.post(self.email_verification_uri, data=email_data)
        self.assertEqual(email_verifcation_response.status_code, status.HTTP_200_OK)
        self.assertEqual(email_verifcation_response.data['detail'], 'Account verified successfully.')
        login_data = {
            'username': self.data['username'],
            'password': self.data['password']
        }
        auth_response = self.client.post(self.auth_uri, data=login_data)
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
        token_data = {
            "token": auth_response.data['access']
        }
        verify_token_response = self.client.post(self.verify_token_uri, data=token_data)
        self.assertEqual(verify_token_response.status_code, status.HTTP_200_OK)
