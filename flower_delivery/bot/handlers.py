# bot/handlers.py
# bot/handlers.py (оптимизированная версия)
from telegram import Bot
from django.conf import settings
from django.core.cache import cache
from telegram import Update
from telegram.ext import CallbackContext

def get_bot_instance():
    """Кеширование объекта бота"""
    bot = cache.get('telegram_bot')
    if not bot:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        cache.set('telegram_bot', bot, timeout=3600)
    return bot

def send_to_telegram_bot(chat_id: str, message: str):
    try:
        bot = get_bot_instance()
        bot.send_message(
            chat_id=chat_id,
            text=message,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Telegram API Error: {str(e)}")
        # Можно добавить повторную попытку отправки



async def start(update: Update, context: CallbackContext):
    if context.args and context.args[0] == settings.ADMIN_PASSWORD:
        chat_id = update.effective_chat.id
        Shop.objects.update_or_create(
            id_telegram=chat_id,
            defaults={'name': f"Магазин {chat_id}"}
        )
        await update.message.reply_text("✅ Магазин привязан!")
    else:
        await update.message.reply_text("❌ Неверный пароль администратора.")

async def handle_update(update: Update, context: CallbackContext):
    """Обработчик входящих сообщений"""
    if update.message:
        if update.message.text == '/start':
            start(update, context)
        else:
            await update.message.reply_text("Используйте /start для начала работы.")


# Регистрация обработчиков
def register_handlers(application):
    application.add_handler(CommandHandler("start", start))