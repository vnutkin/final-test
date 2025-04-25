import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import register_handlers
import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import BotCommand

load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/active_orders", description="Активные заказы"),
        BotCommand(command="/update_order", description="Обновить статус")
    ]
    await bot.set_my_commands(commands)

async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация обработчиков
    register_handlers(dp)

    # Инициализация бота
    bot = Bot(TELEGRAM_BOT_TOKEN)
    await set_bot_commands(bot)
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())