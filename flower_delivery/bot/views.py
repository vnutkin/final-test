# bot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aiogram import Bot, Dispatcher, types
import json
import os
from dotenv import load_dotenv
from django.shortcuts import render


def home(request):
    return render(request, 'home.html', {
        'login_url': '/users/login/',  # URL для входа
        'register_url': '/users/register/',  # URL для регистрации
    })

load_dotenv('./tokens.env')
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()  # Без аргументов!

@csrf_exempt
async def webhook(request):
    if request.method == 'POST':
        update = types.Update(**json.loads(request.body))
        await dp.feed_update(bot, update)  # Передаем bot здесь
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'method not allowed'}, status=405)