# bot/handlers.py
from telegram import Update
from telegram.ext import CallbackContext
from django.conf import settings
from orders.models import Shop

def start(update: Update, context: CallbackContext):
    if context.args and context.args[0] == settings.ADMIN_PASSWORD:
        chat_id = update.effective_chat.id
        Shop.objects.update_or_create(
            id_telegram=chat_id,
            defaults={'name': f"Магазин {chat_id}"}
        )
        update.message.reply_text("✅ Магазин привязан!")
    else:
        update.message.reply_text("❌ Неверный пароль администратора.")

def send_to_telegram_bot(chat_id, message):
    # Логика отправки через API Telegram
    pass

# bot/handlers.py


def handle_update(update: Update, context: CallbackContext):
    """Главный обработчик"""
    if update.message and update.message.text == '/start':
        start(update, context)