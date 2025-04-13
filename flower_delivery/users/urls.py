# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Пример маршрута для регистрации
    path('register/', views.register, name='register'),
    # Добавьте другие маршруты по необходимости
]