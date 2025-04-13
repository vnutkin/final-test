# bot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from .handlers import handle_update

# bot/views.py
from telegram.ext import Updater

TOKEN = "ВАШ_ТОКЕН_БОТА"
updater = Updater(TOKEN, use_context=True)
bot = updater.bot

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        handle_update(Update.de_json(request.json, bot))
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'method not allowed'}, status=405)