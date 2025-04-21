# bot/handlers.py
from aiogram import Router, types, Dispatcher
from aiogram.filters import Command  # Импорт фильтра
from django.conf import settings
from orders.models import Shop

router = Router()

@router.message(Command("start"))  # Используем фильтр Command
async def start_command(message: types.Message):
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    if args and args[0] == settings.ADMIN_PASSWORD:
        chat_id = message.chat.id
        Shop.objects.update_or_create(
            id_telegram=chat_id,
            defaults={'name': f"Магазин {chat_id}"}
        )
        await message.answer("✅ Магазин привязан!")
    else:
        await message.answer("❌ Неверный пароль администратора.")

async def send_to_telegram_bot(chat_id: str, message: str):
    try:
        bot = get_bot_instance()  # или напрямую через Bot(token=...)
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def register_handlers(dp: Dispatcher):
    dp.include_router(router)