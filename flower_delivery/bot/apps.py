# bot/apps.py
from django.apps import AppConfig
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
from dotenv import load_dotenv

load_dotenv('./tokens.env')


class BotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bot"

    def ready(self):
        asyncio.run(self.start_bot())

    async def start_bot(self):
        # Создаем хранилище и передаем его в Dispatcher
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)  # Передаем storage через параметр

        # Регистрация обработчиков
        from .handlers import register_handlers
        register_handlers(dp)

        # Инициализация бота
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

        # Запуск бота
        await bot.delete_webhook()
        await dp.start_polling(bot)
