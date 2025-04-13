# users/models.py
from django.contrib.auth.hashers import make_password
from django.db import models



from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
