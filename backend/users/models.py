from django.db import models
from django.contrib.auth.models import AbstractUser

LANGUAGE = [
    ("en", "english"),
    ("fa", "farsi")
]

class CustomUser(AbstractUser):
    preferred_lang = models.CharField(max_length=50, choices=LANGUAGE, null=True)
    avatar = models.ImageField(upload_to="uploads/avatars/", null=True)
    email = models.EmailField(null=False, blank=False, max_length=200)

    def __str__(self):
        return f'{self.id} - {self.username}'
