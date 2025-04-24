# orders/utils.py
from django.utils import timezone
from datetime import time
from asgiref.sync import sync_to_async
from aiogram import Bot
import os
from dotenv import load_dotenv

load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def is_working_time():
    """Проверяет текущее время в часовом поясе проекта"""
    now = timezone.localtime().time()
    return time(9, 0) <= now <= time(17, 0)


async def send_order_update_notification(order):
    bot = Bot(TELEGRAM_BOT_TOKEN)
    shop = await sync_to_async(lambda: order.product_set.first().shop)()
    message = f"📦 Заказ #{order.id}\nСтатус изменен на: {order.get_status_display()}"
    await bot.send_message(chat_id=shop.id_telegram, text=message)