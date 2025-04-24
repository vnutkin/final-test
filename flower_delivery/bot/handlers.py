from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from django.conf import settings
import os
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from orders.models import Shop, Order

# Загрузка переменных окружения
load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Создаем роутер
router = Router()


@router.message(Command("start"))
async def start_command(message: types.Message):
    print("Команда /start получена!")
    args = message.text.split()[1:]  # Получаем аргументы после команды /start
    chat_id = str(message.chat.id)

    if len(args) >= 2:
        password, shop_name = args[0], args[1]
    elif len(args) == 1:
        password, shop_name = args[0], f"магазин {chat_id}"  # Используем ID Telegram как название
    else:
        await message.answer("❌ Неверный формат команды. Используйте: /start пароль [название_магазина]")
        return

    if password != settings.ADMIN_PASSWORD:
        await message.answer("❌ Неверный пароль администратора.")
        return

    # Используем sync_to_async для выполнения синхронных операций Django
    update_or_create_shop = sync_to_async(Shop.objects.update_or_create)
    shop, created = await update_or_create_shop(
        id_telegram=chat_id,
        defaults={'name': shop_name}
    )

    if created:
        await message.answer(f"✅ Магазин '{shop.name}' успешно создан!")
    else:
        await message.answer(f"✅ Магазин '{shop.name}' успешно обновлен!")


async def send_to_telegram_bot(chat_id: str, message: str):
    try:
        bot = Bot(TELEGRAM_BOT_TOKEN)

        # Если есть обращение к моделям Django, используйте sync_to_async
        get_shop = sync_to_async(Shop.objects.get)
        shop = await get_shop(id_telegram=chat_id)

        await bot.send_message(chat_id=shop.id_telegram, text=message)
    except Exception as e:
        print(f"Ошибка отправки: {e}")


async def send_order_update_notification(order):
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    shop = await sync_to_async(lambda: order.product_set.first().shop)()
    message = f"📦 Заказ #{order.id}\nСтатус изменен на: {order.get_status_display()}"
    await bot.send_message(chat_id=shop.id_telegram, text=message)


@router.message(Command("active_orders"))
async def active_orders(message: types.Message):
    chat_id = message.chat.id
    # Получаем активные заказы для магазина
    orders = await sync_to_async(list)(Order.objects.filter(product__shop__id_telegram=chat_id, status__in=['created', 'paid', 'delivering']))
    if orders:
        response = "📦 Активные заказы:\n"
        for order in orders:
            response += f"#{order.id} - {order.get_status_display()} ({order.created_at.strftime('%d.%m.%Y %H:%M')})\n"
            response += f"Сменить статус: /update_order {order.id}\n"
    else:
        response = "Нет активных заказов."
    await message.answer(response)


# Создаем клавиатуру с кнопками для выбора статуса
def get_status_keyboard(order_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Оплачен", callback_data=f"update_status:{order_id}:paid"),
            InlineKeyboardButton(text="Доставляется", callback_data=f"update_status:{order_id}:delivering"),
        ],
        [
            InlineKeyboardButton(text="Выполнен", callback_data=f"update_status:{order_id}:completed"),
        ]
    ])
    return keyboard


@router.message(Command("update_order"))
async def update_order(message: types.Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Использование: /update_order <order_id>")
        return
    order_id = args[1]
    order = await sync_to_async(Order.objects.filter(id=order_id).first)()
    if not order:
        await message.answer("Заказ не найден.")
        return
    # Отправляем сообщение с кнопками для изменения статуса
    await message.answer(
        f"Выберите новый статус для заказа #{order.id}:",
        reply_markup=get_status_keyboard(order.id)
    )



@router.callback_query(lambda c: c.data.startswith("update_status:"))
async def handle_status_update(callback_query: types.CallbackQuery):
    order_id, new_status = callback_query.data.split(":")[1:]
    order = await sync_to_async(Order.objects.filter(id=order_id).first)()
    if not order:
        await callback_query.answer("Заказ не найден.")
        return
    # Обновляем статус заказа
    order.status = new_status
    await sync_to_async(order.save)()
    # Уведомляем пользователя о новом статусе
    await callback_query.message.edit_text(
        f"Статус заказа #{order.id} изменен на {order.get_status_display()}."
    )
    # Отправляем уведомление в магазин через бота
    await send_to_telegram_bot(order.product_set.first().shop.id_telegram, f"📦 Заказ #{order.id} изменен на {order.get_status_display()}.")


def register_handlers(dp):
    dp.include_router(router)