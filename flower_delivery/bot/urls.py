# bot/urls.py
from django.urls import path, include
from . import views
from django.http import HttpResponse

urlpatterns = [
    path('', lambda request: HttpResponse("Сервер работает!"), name='home'),
    path('webhook/', views.webhook, name='bot_webhook'),
    path('accounts/', include('django.contrib.auth.urls')),
]
