from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from django.conf import settings
import os
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from orders.models import Shop, Order
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Загрузка переменных окружения
load_dotenv('./tokens.env')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Создаем роутер
router = Router()


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📦 Активные заказы")
    builder.button(text="🔄 Обновить статус")
    builder.adjust(2)  # Расположить кнопки в 2 колонки
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



@router.message(Command("active_orders"))
@router.message(F.text == "📦 Активные заказы")
async def active_orders(message: types.Message):
    try:
        chat_id = message.chat.id
        # Получаем магазин по Telegram ID
        shop = await sync_to_async(Shop.objects.get)(id_telegram=chat_id)
        # Фильтруем заказы, связанные с магазином через продукт
        orders = await sync_to_async(list)(
            Order.objects.filter(product__shop=shop, status__in=['created', 'paid', 'delivering'])
        )

        if orders:
            response = "📦 Активные заказы:\n"
            for order in orders:
                response += f"#{order.id} - {order.get_status_display()} ({order.created_at.strftime('%d.%m.%Y %H:%M')})\n"
                response += f"Сменить статус: /update_order {order.id}\n"
        else:
            response = "Нет активных заказов."

        await message.answer(response, reply_markup=get_main_keyboard())

    except Shop.DoesNotExist:
        await message.answer("❌ Магазин не найден. Используйте /start для регистрации.",
                             reply_markup=get_main_keyboard())


@router.message(F.text == "🔄 Обновить статус")
async def update_order_menu(message: types.Message):
    chat_id = message.chat.id
    # Получаем активные заказы магазина
    orders = await sync_to_async(list)(
        Order.objects.filter(product__shop__id_telegram=chat_id, status__in=['created', 'paid', 'delivering']))

    if not orders:
        await message.answer("Нет активных заказов.", reply_markup=get_main_keyboard())
        return

    # Создаем кнопки с ID заказов
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Заказ #{order.id}", callback_data=f"select_order:{order.id}")]
        for order in orders
    ])

    await message.answer("Выберите заказ:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("select_order:"))
async def select_order(callback: types.CallbackQuery):
    order_id = callback.data.split(":")[1]
    await callback.message.answer(
        f"Выберите статус для заказа #{order_id}:",
        reply_markup=get_status_keyboard(order_id)
    )
    await callback.message.answer("Меню:", reply_markup=get_main_keyboard())


@router.message(Command("update_order"))
@router.message(F.text == "🔄 Обновить статус")
async def update_order_menu(message: types.Message):
    chat_id = message.chat.id
    # Получаем активные заказы магазина
    orders = await sync_to_async(list)(
        Order.objects.filter(product__shop__id_telegram=chat_id, status__in=['created', 'paid', 'delivering']))

    if not orders:
        await message.answer("Нет активных заказов.", reply_markup=get_main_keyboard())
        return

    # Создаем кнопки с ID заказов
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Заказ #{order.id}", callback_data=f"select_order:{order.id}")]
        for order in orders
    ])

    await message.answer("Выберите заказ:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("select_order:"))
async def select_order(callback: types.CallbackQuery):
    order_id = callback.data.split(":")[1]
    await callback.message.answer(
        f"Выберите статус для заказа #{order_id}:",
        reply_markup=get_status_keyboard(order_id)
    )
    await callback.message.answer("Меню:", reply_markup=get_main_keyboard())


@router.callback_query(lambda c: c.data.startswith("update_status:"))
async def handle_status_update(callback_query: types.CallbackQuery):
    data = callback_query.data.split(":")
    order_id, new_status = data[1], data[2]

    # Получаем заказ
    order = await sync_to_async(Order.objects.filter(id=order_id).first)()
    if not order:
        await callback_query.answer("Заказ не найден.")
        return

    # Обновляем статус
    order.status = new_status
    await sync_to_async(order.save)()

    # Отправляем подтверждение
    await callback_query.message.edit_text(
        f"Статус заказа #{order.id} изменен на {order.get_status_display()}."
    )

    # Уведомляем магазин
    try:
        product = await sync_to_async(order.product_set.first)()
        if product and product.shop:
            await send_to_telegram_bot(
                product.shop.id_telegram,
                f"📦 Заказ #{order.id} изменен на {order.get_status_display()}."
            )
    except Exception as e:
        print(f"Ошибка уведомления: {e}")

    await callback_query.message.answer("Меню:", reply_markup=get_main_keyboard())

def register_handlers(dp):
    dp.include_router(router)

