# orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Order

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
    for shop in shops:
        send_to_telegram_bot(shop.id_telegram, f"Новый заказ #{new_order.id}")

    return redirect('order_history')

class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)