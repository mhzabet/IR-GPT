from django.db import models
from django.contrib.auth.models import AbstractUser

LANGUAGE = [
    ("en", "english"),
    ("fa", "farsi")
]

class CustomUser(AbstractUser):
    preferred_lang = models.CharField(max_length=50, choices=LANGUAGE, )
    avatar = models.ImageField(upload_to="uploads/avatars/")

    def __str__(self):
        return f'{self.username}'
