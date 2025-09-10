from django.test import TestCase
from users.models import CustomUser

User = CustomUser

class CustomUserModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):    
        """Initialize: Initail user with test data"""
        cls.user = User.objects.create_user(username='testuser', password='testpass123', email='test@mail.com')

    def test_user_exists(self):
        """TestCase: test for user creation in db."""
        self.assertEqual(User.objects.count(), 1)

    def test_email_verify_required(self):
        """TestCase: test user must not be active before verify email."""
        self.assertFalse(self.user.is_active)

    def test_preferred_lang_defualt(self):
        """TestCase: test user preferred language to speak defualt."""
        self.assertEqual(self.user.preferred_lang, 'en')

    def test_avatar_is_null(self):
        """TestCase: test user is not required to upload avatar."""
        self.assertEqual(self.user.avatar, None)