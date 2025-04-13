# bot/apps.py
from django.apps import AppConfig

class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'  # Имя приложения должно совпадать с названием директории