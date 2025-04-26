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
from django.contrib import messages
from asgiref.sync import sync_to_async
import asyncio  # Добавьте импорт
# orders/views.py
@login_required
def create_order(request):
    # Проверяем, есть ли товары в корзине
    order = Order.objects.filter(user=request.user, status='gathering').first()
    if not order or not BasketItem.objects.filter(order=order).exists():
        messages.error(request, "Ваша корзина пуста!")
        return redirect('view_cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Обновляем данные заказа
            order.address = form.cleaned_data['address']
            order.comment = form.cleaned_data['comment']
            order.status = 'created'
            order.save()
            # Запуск асинхронной функции через asyncio.run()
            try:
                from orders.utils import send_order_update_notification
                asyncio.run(send_order_update_notification(order))
            except Exception as e:
                print(f"Ошибка отправки уведомления: {e}")

            messages.success(request, "Заказ успешно создан!")
            return redirect('order_history')
    else:
        form = OrderForm()

    return render(request, 'orders/create_order.html', {'form': form})

# orders/views.py



class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_history.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

# orders/views.py

#from orders.models import BasketItem



# orders/views.py
@login_required
def view_cart(request):
    # Получаем активный заказ со статусом "Набор"
    order = Order.objects.filter(user=request.user, status='gathering').first()
    if not order:
        # Если заказа нет, показываем пустую корзину
        return render(request, 'orders/cart.html', {'items_with_total': [], 'total_price': 0})

    # Получаем товары из корзины
    basket_items = BasketItem.objects.filter(order=order)
    items_with_total = []
    total_price = 0

    for item in basket_items:
        total_item_price = item.product.price * item.quantity
        items_with_total.append({
            'item': item,
            'total_price': total_item_price
        })
        total_price += total_item_price

    return render(request, 'orders/cart.html', {
        'items_with_total': items_with_total,
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

        # Добавляем отправку уведомления
        from orders.utils import send_order_update_notification
        asyncio.run(send_order_update_notification(order))

        return redirect('admin_order_list')
    return render(request, 'orders/update_order_status.html', {'order': order})

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminOrderListView(ListView):
    model = Order
    template_name = 'orders/admin_order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')


@login_required
def cancel_order(request):
    # Получаем активный заказ со статусом "Набор"
    order = Order.objects.filter(user=request.user, status='gathering').first()
    if order:
        # Удаляем все товары из корзины
        BasketItem.objects.filter(order=order).delete()
        # Удаляем заказ
        order.delete()
    return redirect('view_cart')