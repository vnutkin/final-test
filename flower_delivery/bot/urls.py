# bot/urls.py
from django.urls import path, include
from . import views
from django.http import HttpResponse


from .views import home

urlpatterns = [
    path('', home, name='home'),  # Используем представление home
    path('webhook/', views.webhook, name='bot_webhook'),
    path('accounts/', include('django.contrib.auth.urls')),
]