# catalog/views.py
from django.shortcuts import get_object_or_404, redirect
from catalog.models import Product
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order, BasketItem
from django.contrib import messages  # Добавьте эту строку в начале файла

def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog/product_list.html', {'products': products})






@login_required
def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        order, created = Order.objects.get_or_create(
            user=request.user,
            status='gathering',
            defaults={'address': '', 'comment': ''}
        )

        basket_item, item_created = BasketItem.objects.get_or_create(
            user=request.user,
            product=product,
            order=order,
            defaults={'quantity': 1}
        )

        if not item_created:
            basket_item.quantity += 1
            basket_item.save()

        messages.success(request, "Товар добавлен в корзину!")  # Теперь ошибки не будет

    return redirect('view_cart')