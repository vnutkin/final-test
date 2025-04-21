# bot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aiogram import Bot, Dispatcher, types
import json
import os
from dotenv import load_dotenv

load_dotenv('./tokens.env')
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)

@csrf_exempt
async def webhook(request):
    if request.method == 'POST':
        update = types.Update(**json.loads(request.body))
        await dp.process_update(update)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'method not allowed'}, status=405)