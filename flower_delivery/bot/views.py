# bot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import (
    Updater,
    Application,  # Новый класс в v20+
    CallbackContext,
    CallbackQueryHandler
)
from .handlers import handle_update
import os
import asyncio
from dotenv import load_dotenv

load_dotenv('./tokens.env') #

# Загрузка токена из переменных окружения теств
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Создаем экземпляр Application (вместо Updater)
application = Application.builder().token(TOKEN).build()


@csrf_exempt
def webhook(request):
    if request.method == "POST":
        # Обработка обновления через асинхронный контекст
        async def process_update():
            update = Update.de_json(request.json, application.bot)
            await application.process_update(update)

        asyncio.run(process_update())
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "method not allowed"}, status=405)