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
        # Обернутый ORM-запрос
        get_shop = sync_to_async(Shop.objects.get)
        shop = await get_shop(id_telegram=chat_id)
        await bot.send_message(chat_id=shop.id_telegram, text=message)
    except Exception as e:
        print(f"Ошибка отправки: {e}")


# Исправляем функцию отправки уведомлений
async def send_order_update_notification(order):
    try:
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

        # Получаем первый элемент корзины
        get_first_item = sync_to_async(lambda: order.basketitem_set.first())
        basket_item = await get_first_item()

        if basket_item:
            # Получаем магазин через продукт
            get_shop = sync_to_async(lambda: basket_item.product.shop)
            shop = await get_shop()

            message = f"📦 Заказ #{order.id}\nСтатус: {order.get_status_display()}"
            await bot.send_message(chat_id=shop.id_telegram, text=message)
    except Exception as e:
        print(f"Ошибка уведомления: {e}")



@router.message(F.text == "📦 Активные заказы")
async def active_orders(message: types.Message):
    chat_id = message.chat.id

    def _fetch_orders():
        return list(
            Order.objects.filter(
                basketitem__product__shop__id_telegram=chat_id,
                status__in=['created', 'paid', 'delivering']
            ).distinct().prefetch_related('basketitem_set__product')
        )

    try:
        orders = await sync_to_async(_fetch_orders)()
        response = "📦 Активные заказы:\n"
        for order in orders:
            products = ", ".join([bi.product.name for bi in order.basketitem_set.all()])
            response += f"""#{order.id} - {order.get_status_display()}
Товары: {products}\n\n"""
        await message.answer(response, reply_markup=get_main_keyboard())
    except Exception as e:
        print(f"Database error: {e}")
        await message.answer("❌ Ошибка при получении заказов")



@router.message(F.text == "✅ Оплаченные заказы")
async def paid_orders(message: types.Message):
    chat_id = message.chat.id
    def _fetch_orders_p():
        return list(
            Order.objects.filter(
                basketitem__product__shop__id_telegram=chat_id,
                status__in=['paid']
            ).distinct().prefetch_related('basketitem_set__product')
        )

    try:
        orders = await sync_to_async(_fetch_orders_p)()
        if not orders:
            await message.answer("Нет оплаченных заказов", reply_markup=get_main_keyboard())
            return

        # Формируем текст ответа
        response = "✅ Оплаченные заказы:\n"
        for order in orders:
            # Добавляем информацию о заказе
            response +=  f"""#{order.id} | Коммент: {order.comment} | Адрес: {order.address}\n"""
          # Добавляем информацию о товарах
            items = order.basketitem_set.all()
            items_text = "\n".join([
                f"• {item.product.name} (ID: {item.product.id}) - {item.quantity} шт."
                for item in items
            ])
            response += f"{items_text}\n\n"

        # Создаем клавиатуру для каждого заказа
        keyboard = []
        for order in orders:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"🚚 заказ #{order.id}| Адрес: {order.address} | Коммент: {order.comment}",
                    callback_data=f"change_status_delivering_{order.id}"
                )
           ])

        # Отправляем сообщение с текстом и клавиатурой
        await message.answer(response,  reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    except Shop.DoesNotExist:
        await message.answer("❌ Магазин не найден.", reply_markup=get_main_keyboard())
    except Exception as e:
        print(f"Database error: {e}")
        await message.answer("Ошибка при получении заказов.", reply_markup=get_main_keyboard())


@router.message(F.text == "🚚 Заказы в доставке")
async def delivering_orders(message: types.Message):
    chat_id = message.chat.id
    def _fetch_orders_d():
        return list(
            Order.objects.filter(
                basketitem__product__shop__id_telegram=chat_id,
                status__in=['delivering']
            ).distinct().prefetch_related('basketitem_set__product')
        )
    try:
        orders = await sync_to_async(_fetch_orders_d)()

        if not orders:
            await message.answer("Нет заказов в доставке", reply_markup=get_main_keyboard())
            return

        # Формируем текст ответа
        response = "🚚 Заказы в доставке:\n"

        keyboard = []
        for order in orders:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"✅ Завершить #{order.id}| Адр.: {order.address} | Ком.: {order.comment}",
                    callback_data=f"complete_order_{order.id}"
                )
            ])

        # Отправляем сообщение с текстом и клавиатурой
        await message.answer(response, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))

    except Shop.DoesNotExist:
        await message.answer("❌ Магазин не найден.", reply_markup=get_main_keyboard())
    except Exception as e:
        print(f"Database error: {e}")
        await message.answer("Ошибка при получении заказов.", reply_markup=get_main_keyboard())

@router.message()
async def unknown_message(message: types.Message):
    await message.answer("Неизвестная команда. Пожалуйста, используйте кнопки меню.")


# обработчик завершения заказа
@router.callback_query(lambda c: c.data.startswith("change_status_delivering_"))
async def delivering_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[-1])
    order = await sync_to_async(Order.objects.get)(id=order_id)
    order.status = 'delivering'
    await sync_to_async(order.save)()
    await callback.answer(f"Заказ #{order.id} в доставке!")

@router.callback_query(lambda c: c.data.startswith("complete_order_"))
async def complete_order(callback: types.CallbackQuery):
    order_id = int(callback.data.split("_")[-1])
    order = await sync_to_async(Order.objects.get)(id=order_id)
    order.status = 'completed'
    await sync_to_async(order.save)()
    await callback.answer(f"Заказ #{order.id} завершен!")



def register_handlers(dp):
    # В функции register_handlers добавьте:
    router.message.register(active_orders, F.text == "📦 Активные заказы")
    router.message.register(paid_orders, F.text == "✅ Оплаченные заказы")
    router.message.register(delivering_orders, F.text == "🚚 Заказы в доставке")
    dp.include_router(router)

