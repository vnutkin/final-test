# orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView


# orders/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from catalog.models import Product
from orders.models import Order, BasketItem
from bot.handlers import send_to_telegram_bot  # Убедитесь, что функция существует


@login_required
def create_order(request):
    # Получаем товары из корзины пользователя
    basket_items = BasketItem.objects.filter(user=request.user)

    # Создаем заказ
    new_order = Order.objects.create(user=request.user, status='created')

    # Привязываем товары к заказу
    for item in basket_items:
        item.order = new_order
        item.save()

    # Получаем магазины, связанные с товарами
    shops = set(item.product.shop for item in basket_items)

    # Отправляем уведомления
    message = (
        f"🛒 Новый заказ #{new_order.id}\n"
        f"📦 Товаров: {basket_items.count()}\n"
        f"📦 Статус: {new_order.get_status_display()}"
    )

    for shop in shops:
        send_to_telegram_bot(
            chat_id=shop.id_telegram,
            message=message
        )
    return redirect('order_history')

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)