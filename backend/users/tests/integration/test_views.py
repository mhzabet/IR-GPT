from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import cache
User = get_user_model()

class TestEmailVerficationView(TestCase):

    def setUp(self):
        self.user_data = {
            'first_name':'test',
            'last_name':'user',
            'username':'testuser',
            'email':'test@mail.com',
            'preferred_lang':'en',
            'avatar': '',
            'password': 'testPassword!123',
            'password2':'testPassword!123',
        }
        self.client = APIClient()
        self.register_uri = '/account/user/register/'
        self.verify_uri = '/account/user/verify/'
        cache.clear()
    
    def test_user_verification_email(self):
        self.client.post(self.register_uri, data=self.user_data)
        code = cache.get(f"code:{self.user_data['email']}")
        data = {
            'email': self.user_data['email'],
            'code':code
        }
        verify = self.client.post(self.verify_uri, data=data)
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        self.assertEqual(verify.data['datail'], 'Account verified successfully.')

class TestResendVerificationCodeView(TestCase):

    def setUp(self):
        self.client = APIClient()
        cache.clear()

        self.data = {"email":"test@mail.com"}
        User.objects.create_user(
            "testUser", self.data['email'], "testPassword!123"
        )
        self.resend_code_uri = '/account/user/resend-verify-code/'
        self.verify_uri = '/account/user/verify/'

    def test_email_verification_by_resend_code(self):
        resend_response = self.client.post(self.resend_code_uri, data=self.data)
        self.assertEqual(resend_response.status_code, status.HTTP_200_OK)
        self.assertEqual(resend_response.data['detail'], 'Verification code resent successfuly. Check you\'r email for verification code.')

        code = cache.get(f"code:{self.data['email']}")

        verify_data = {
            'email': self.data['email'],
            'code':code
        }
        verify_response = self.client.post(self.verify_uri, data=verify_data)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertEqual(verify_response.data['datail'], 'Account verified successfully.')
    
    def test_attemption_protection(self):
        i = 0
        while i <= 5:
            i += 1
            resend_response = self.client.post(self.resend_code_uri, data=self.data)
        self.assertEqual(resend_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(resend_response.data['detail'], 'Maximum verification attempts reached. Please try agian later.')

    def test_email_validation(self):
        invalid_email = self.data.copy()
        invalid_email['email'] = 'invalid@mail.com'
        resend_response = self.client.post(self.resend_code_uri, data=invalid_email)
        self.assertEqual(resend_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resend_response.data['detail'], 'Email not registerd. Please sign up first.')

    def test_random_code_protection(self):
        resend_response = self.client.post(self.resend_code_uri, data=self.data)
        self.assertEqual(resend_response.status_code, status.HTTP_200_OK)
        self.assertEqual(resend_response.data['detail'], 'Verification code resent successfuly. Check you\'r email for verification code.')

        invalid_code = 993033 # random code

        verify_data = {
            'email': self.data['email'],
            'code':invalid_code
        }

        verify_response = self.client.post(self.verify_uri, data=verify_data)
        self.assertEqual(verify_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(verify_response.data['detail'], 'Provided verification code may invalid or expired.')