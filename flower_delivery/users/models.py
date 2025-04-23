# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True)

    USERNAME_FIELD = 'phone'  # Используем телефон для входа
    REQUIRED_FIELDS = ['username']  # Для команды createsuperuser

    def __str__(self):
        return self.phone