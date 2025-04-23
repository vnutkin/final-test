# bot/management/commands/run_bot.py
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import register_handlers
import asyncio
import os
from dotenv import load_dotenv

load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        async def main():
            # Инициализация бота и диспетчера
            storage = MemoryStorage()
            dp = Dispatcher(storage=storage)
            bot = Bot(TELEGRAM_BOT_TOKEN)

            # Регистрация обработчиков
            register_handlers(dp)

            # Запуск бота
            await bot.delete_webhook()
            await dp.start_polling(bot)

        self.stdout.write("Запуск бота...")
        asyncio.run(main())
        self.stdout.write("Бот остановлен.")