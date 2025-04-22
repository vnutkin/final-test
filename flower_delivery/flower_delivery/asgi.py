
import os
import asyncio
from django.core.asgi import get_asgi_application
from flower_delivery.bot.apps import BotConfig

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
application = get_asgi_application()

# Создаем экземпляр BotConfig
bot_app_config = BotConfig("bot", "bot")  # name и app_name


async def start_bot():
    await bot_app_config.start_bot()  # Вызываем метод на экземпляре

# Запуск бота в фоне
asyncio.create_task(start_bot())
