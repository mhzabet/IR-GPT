from django.db import models
from django.contrib.auth.models import AbstractUser

LANGUAGE = [
    ("en", "english"),
    ("fa", "farsi")
]

class CustomUser(AbstractUser):
    preferred_lang = models.CharField(max_length=50, choices=LANGUAGE, null=True, default='en')
    avatar = models.ImageField(upload_to="uploads/avatars/", null=True, blank=True)
    email = models.EmailField(null=False, blank=False, max_length=200, unique=True)

    def __str__(self):
        return f'{self.id} - {self.username}'
