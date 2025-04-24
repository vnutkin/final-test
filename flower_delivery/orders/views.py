# orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from catalog.models import Product
from orders.models import Order, BasketItem
from bot.handlers import send_to_telegram_bot  # Убедитесь, что функция существует
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect

# orders/views.py
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


@login_required
def create_order(request):
    # Получаем товары из корзины пользователя
    basket_items = BasketItem.objects.filter(user=request.user, order__isnull=True)

    if not basket_items.exists():
        return redirect('cart')  # Перенаправляем, если корзина пуста

    # Проверяем, что все товары принадлежат одному магазину
    shops = set(item.product.shop for item in basket_items)
    if len(shops) > 1:
        return redirect('cart')  # Перенаправляем, если товары из разных магазинов

    # Создаем заказ
    order = Order.objects.create(user=request.user, status='created')

    # Привязываем товары к заказу
    for item in basket_items:
        item.order = order
        item.save()

    # Формируем сообщение для отправки в магазин
    shop = basket_items.first().product.shop
    message = (
        f"🛒 Новый заказ #{order.id}\n"
        f"📦 Товаров: {basket_items.count()}\n"
        f"📦 Статус: {order.get_status_display()}"
    )
    send_to_telegram_bot(chat_id=shop.id_telegram, message=message)

    return redirect('order_history')


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# orders/views.py

#from orders.models import BasketItem



@login_required
def view_cart(request):
    # Получаем активный заказ пользователя (статус "draft")
    active_order = Order.objects.filter(user=request.user, status='draft').first()
    if not active_order:
        return render(request, 'orders/cart.html', {'basket_items': []})

    # Получаем товары из корзины
    basket_items = BasketItem.objects.filter(order=active_order)
    total_price = sum(item.product.price * item.quantity for item in basket_items)

    return render(request, 'orders/cart.html', {
        'basket_items': basket_items,
        'total_price': total_price
    })



@login_required
def remove_from_cart(request, item_id):
    # Получаем товар из корзины
    basket_item = get_object_or_404(BasketItem, id=item_id, order__user=request.user, order__status='draft')
    order = basket_item.order

    # Удаляем товар из корзины
    basket_item.delete()

    # Если в корзине больше нет товаров, удаляем заказ
    if not BasketItem.objects.filter(order=order).exists():
        order.delete()

    return redirect('cart')
# orders/views.py




@staff_member_required
def admin_order_list(request):
    orders = Order.objects.all()
    return render(request, 'orders/admin_order_list.html', {'orders': orders})

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        # Отправляем уведомление через бота
        send_order_update_notification(order)
        return redirect('admin_order_list')
    return render(request, 'orders/update_order_status.html', {'order': order})


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminOrderListView(ListView):
    model = Order
    template_name = 'orders/admin_order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')