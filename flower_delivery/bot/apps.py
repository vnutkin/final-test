# bot/apps.py
from django.apps import AppConfig
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
from dotenv import load_dotenv
import sys

load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot"

    def ready(self):
        # Запускать бота только при вызове 'runserver'
        if 'runserver' in sys.argv:
            asyncio.run(self.start_bot())

    async def start_bot(self):
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Регистрация обработчиков
        from .handlers import register_handlers
        register_handlers(dp)

        # Инициализация бота
        bot = Bot(TELEGRAM_BOT_TOKEN)
        await bot.delete_webhook()
        await dp.start_polling(bot)
