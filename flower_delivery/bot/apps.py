# bot/apps.py
from django.apps import AppConfig
from .handlers import register_handlers

class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot"

    def ready(self):
        from .views import application
        register_handlers(application)
        application.run_polling()  # Или настройте вебхук