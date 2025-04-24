# catalog/views.py
from django.shortcuts import get_object_or_404, redirect
from catalog.models import Product
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order, BasketItem

# catalog/views.py


def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog/product_list.html', {'products': products})



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Получаем активную корзину пользователя
    basket_items = BasketItem.objects.filter(user=request.user, order__isnull=True)

    # Проверяем, что корзина пуста или товары из одного магазина
    if basket_items.exists() and basket_items.first().product.shop != product.shop:
        return redirect('catalog')  # Перенаправляем, если товар из другого магазина

    # Добавляем товар в корзину
    basket_item, created = BasketItem.objects.get_or_create(
        user=request.user,
        product=product,
        order=None,
        defaults={'quantity': 1}
    )
    if not created:
        basket_item.quantity += 1
        basket_item.save()

    return redirect('cart')