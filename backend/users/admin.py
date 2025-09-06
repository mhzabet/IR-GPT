from django.contrib import admin
from .models import CustomUser
from django.contrib.admin import register



@register(CustomUser)
class CustomuUserAdmin(admin.ModelAdmin):
    pass