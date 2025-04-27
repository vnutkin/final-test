from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from django.conf import settings
import os
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from orders.models import Shop, Order, BasketItem
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Загрузка переменных окружения
load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Создаем роутер
router = Router()

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📦 Активные заказы")
    builder.button(text="✅ Оплаченные заказы")
    builder.button(text="🚚 Заказы в доставке")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


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
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_keyboard()  # Добавляем клавиатуру
    )

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





@router.message(F.text == "📦 Активные заказы")
async def active_orders(message: types.Message):
    try:
        chat_id = message.chat.id
        shop = await sync_to_async(Shop.objects.get)(id_telegram=chat_id)
        orders = await sync_to_async(list)(
            Order.objects.filter(
                basketitem__product__shop__id_telegram=chat_id,
                status__in=['created', 'paid', 'delivering']
            ).distinct()
        )
        if orders:
            response = "📦 Активные заказы:\n"
            for order in orders:
                response += (
                    f"#{order.id} - {order.get_status_display()} "
                    f"({order.created_at.strftime('%d.%m.%Y %H:%M')})\n"
                )
            await message.answer(response, reply_markup=get_main_keyboard())
        else:
            await message.answer("Нет активных заказов.",
                                reply_markup=get_main_keyboard())
    except Shop.DoesNotExist:
        await message.answer("❌ Магазин не найден. Используйте /start для регистрации.",
                             reply_markup=get_main_keyboard())







# В начале файла импортируем необходимые модели
#from orders.models import Order, BasketItem


@router.message(F.text == "✅ Оплаченные заказы")
async def paid_orders(message: types.Message):
    chat_id = message.chat.id
    try:
        shop = await sync_to_async(Shop.objects.get)(id_telegram=chat_id)
    except Shop.DoesNotExist:
        await message.answer("❌ Магазин не найден. Используйте /start для регистрации.",
                             reply_markup=get_main_keyboard())
        return

    orders = await sync_to_async(list)(
        Order.objects.filter(
            basketitem__product__shop=shop,
            status='paid'
        ).distinct()
    )

    if not orders:
        await message.answer("Нет оплаченных заказов", reply_markup=get_main_keyboard())
        return

    keyboard = []
    for order in orders:
        keyboard.append([
            InlineKeyboardButton(
                text=f"#{order.id}",
                callback_data=f"paid_order_details_{order.id}"
            ),
            # Исправлен callback_data для кнопки изменения статуса
            InlineKeyboardButton(
                text="🚚 В доставку",
                callback_data=f"change_status_delivering_{order.id}"
            )
        ])

    await message.answer("Оплаченные заказы:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))



@router.message(F.text == "🚚 Заказы в доставке")
async def delivering_orders(message: types.Message):
    chat_id = message.chat.id
    shop = await sync_to_async(Shop.objects.get)(id_telegram=chat_id)

    orders = await sync_to_async(list)(
        Order.objects.filter(
            basketitem__product__shop=shop,
            status='delivering'
        ).distinct()
    )

    if not orders:
        await message.answer("Нет заказов в доставке", reply_markup=get_main_keyboard())
        return

    response = "🚚 Заказы в доставке:\n"
    for order in orders:
        response += (
            f"#{order.id} | Адрес: {order.address} | Тел: {order.user.phone}\n"
        )

    keyboard = []
    for order in orders:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📦 Заказ #{order.id}",
                callback_data=f"delivery_order_details_{order.id}"
            ),
            InlineKeyboardButton(
                text="✅ Завершить",
                callback_data=f"complete_order_{order.id}"
            )
        ])

    await message.answer(response, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

# обрабоотчики деталей заказа
@router.callback_query(lambda c: c.data.startswith("delivery_order_details_"))
async def delivery_order_details(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[-1])
    order = await sync_to_async(Order.objects.get)(id=order_id)

    items = await sync_to_async(list)(order.basketitem_set.all())
    items_text = "\n".join([
        f"• {item.product.name} (ID: {item.product.id}) - {item.quantity} шт."
        for item in items
    ])

    text = (
        f"🚚 Заказ в доставке #{order.id}\n"
        f"Телефон: {order.user.phone}\n"
        f"Адрес: {order.address}\n"
        f"Комментарий: {order.comment}\n\n"
        f"Товары:\n{items_text}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_delivery")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "back_to_delivery")
async def back_to_delivery(callback: types.CallbackQuery):
    await delivering_orders(callback.message)

@router.callback_query(lambda c: c.data == "back_to_paid")
async def back_to_paid(callback: types.CallbackQuery):
    await paid_orders(callback.message)


# обработчик завершения заказа
@router.callback_query(lambda c: c.data.startswith("complete_order_"))
async def complete_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[-1])
    order = await sync_to_async(Order.objects.get)(id=order_id)
    order.status = 'completed'
    await sync_to_async(order.save)()
    await callback.answer(f"Заказ #{order.id} завершен!")


@router.callback_query(lambda c: c.data.startswith("change_status_"))
async def handle_status_update(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_")
    new_status = data[2]
    order_id = data[3]

    order = await sync_to_async(Order.objects.get)(id=order_id)
    order.status = new_status
    await sync_to_async(order.save)()

    # Обновляем сообщение после изменения статуса
    await callback_query.answer(f"Статус заказа #{order.id} изменен на {order.get_status_display()}")
    await paid_orders(callback_query.message)  # Возвращаемся к списку оплаченных заказов

def register_handlers(dp):
    # В функции register_handlers добавьте:
    router.message.register(active_orders, F.text == "📦 Активные заказы")
    router.message.register(paid_orders, F.text == "✅ Оплаченные заказы")
    router.message.register(delivering_orders, F.text == "🚚 Заказы в доставке")
    dp.include_router(router)

