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
    from orders.models import BasketItem

    # Получаем количество товаров через sync_to_async
    count = await sync_to_async(BasketItem.objects.filter(order=order).count)()

    # Получаем первый товар
    basket_item = await sync_to_async(BasketItem.objects.filter(order=order).first)()

    if not basket_item:
        return

    # Получаем shop через цепочку sync_to_async
    product = await sync_to_async(lambda: basket_item.product)()
    shop = await sync_to_async(lambda: product.shop)()

    message = f"📦 Заказ #{order.id}\nСтатус: {order.get_status_display()}\nТоваров: {count}"
    await bot.send_message(chat_id=shop.id_telegram, text=message)

# orders/utils.py
async def send_order_update_notification(order):
    bot = Bot(TELEGRAM_BOT_TOKEN)
    from orders.models import BasketItem

    # Получаем количество товаров через sync_to_async
    count = await sync_to_async(BasketItem.objects.filter(order=order).count)()

    # Получаем первый товар
    basket_item = await sync_to_async(BasketItem.objects.filter(order=order).first)()

    if not basket_item:
        return

    # Получаем shop через цепочку sync_to_async
    product = await sync_to_async(lambda: basket_item.product)()
    shop = await sync_to_async(lambda: product.shop)()

    message = f"📦 Заказ #{order.id}\nСтатус: {order.get_status_display()}\nТоваров: {count}"
    await bot.send_message(chat_id=shop.id_telegram, text=message)

