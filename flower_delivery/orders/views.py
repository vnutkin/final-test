# orders/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.shortcuts import render, redirect
from .forms import OrderForm


# orders/views.py
from django.contrib.auth.decorators import login_required
from catalog.models import Product
from orders.models import Order, BasketItem
from bot.handlers import send_to_telegram_bot  # Убедитесь, что функция существует
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect



@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            # Привязываем товары из корзины к заказу
            basket_items = BasketItem.objects.filter(user=request.user)
            for item in basket_items:
                item.order = order
                item.save()

            # Очищаем корзину
            basket_items.delete()

            return redirect('order_history')
    else:
        form = OrderForm()

    return render(request, 'orders/create_order.html', {'form': form})

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
    basket_items = BasketItem.objects.filter(user=request.user)
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
    item = get_object_or_404(BasketItem, id=item_id, user=request.user)
    item.delete()
    return redirect('view_cart')