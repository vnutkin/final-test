"""
URL configuration for flower_delivery project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# flower_delivery/urls.py
from django.contrib import admin
from django.urls import path, include
from users.views import profile
#from bot.views import home


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bot.urls')),  # Главная страница
    path('users/', include('users.urls')),  # Маршруты для пользователей
    path('catalog/', include('catalog.urls')),
    path('orders/', include('orders.urls')),
    path('bot/', include('bot.urls')),
    path('accounts/profile/', profile, name='profile'),  # Новый маршрут для профиля
]