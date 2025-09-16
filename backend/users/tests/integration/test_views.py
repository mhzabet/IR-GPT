from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()

class TestEmailVerficationIntegration(TestCase):

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
        self.assertEqual(verify.data['detail'], 'Account verified successfully.')

class TestResendVerificationCodeIntegration(TestCase):

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
        self.assertEqual(verify_response.data['detail'], 'Account verified successfully.')
    
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

class TestPasswordResetIntegration(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@mail.com',
            password='Old_Pass123'
        )
        self.reset_request_uri = '/account/user/request-password-reset/'
        self.reset_confirm_uri = '/account/user/password-reset/'

    @patch('users.views.send_mail')  # mock email sending
    def test_password_reset_flow(self, mock_send_mail):
        """Integrated test: request reset → confirm reset → password updated"""

        # Step 1: Request password reset
        request_data = {'email': self.user.email}
        response = self.client.post(self.reset_request_uri, data=request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Password reset link sent to your email.')
        mock_send_mail.assert_called_once()  # email was "sent"

        # Step 2: Generate uid and token as the view would
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)

        # Step 3: Confirm password reset
        confirm_data = {
            'uidb64': uidb64,
            'token': token,
            'new_password': 'New_Pass123',
            'confirm_new_password': 'New_Pass123'
        }
        confirm_response = self.client.post(self.reset_confirm_uri, data=confirm_data)
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        self.assertEqual(confirm_response.data['detail'], 'Password reset successfully.')

        # Step 4: Verify password actually changed in DB
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('New_Pass123'))
