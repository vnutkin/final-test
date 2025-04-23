# bot/apps.py
import threading  # Добавьте этот импорт
import sys
from django.apps import AppConfig
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
from dotenv import load_dotenv

load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot"

    def ready(self):
        # Запускать бота только при вызове 'runserver'
        if 'runserver' in sys.argv and not any('run_bot' in arg for arg in sys.argv):
            bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            bot_thread.start()

    def run_bot(self):
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