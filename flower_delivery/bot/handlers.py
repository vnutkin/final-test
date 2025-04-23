# bot/handlers.py
# bot/handlers.py
from aiogram import Router, types, Bot
from aiogram.filters import Command
from django.conf import settings
from orders.models import Shop
import os
from dotenv import load_dotenv
from asgiref.sync import sync_to_async

load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    print("Команда /start получена!")
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if args and args[0] == settings.ADMIN_PASSWORD:
        chat_id = message.chat.id

        # Используем sync_to_async для выполнения синхронных операций
        update_or_create_shop = sync_to_async(Shop.objects.update_or_create)
        await update_or_create_shop(
            id_telegram=chat_id,
            defaults={'name': f"Магазин {chat_id}"}
        )

        await message.answer("✅ Магазин привязан!")
    else:
        await message.answer("❌ Неверный пароль администратора.")


async def send_to_telegram_bot(chat_id: str, message: str):
    try:
        bot = Bot(TELEGRAM_BOT_TOKEN)

        # Если есть обращение к моделям Django, используйте sync_to_async
        get_shop = sync_to_async(Shop.objects.get)
        shop = await get_shop(id_telegram=chat_id)

        await bot.send_message(chat_id=shop.id_telegram, text=message)
    except Exception as e:
        print(f"Ошибка отправки: {e}")


def register_handlers(dp):
    dp.include_router(router)