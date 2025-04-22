# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(max_length=15)

    class Meta:
        model = CustomUser
        fields = ('phone', 'password1', 'password2')
