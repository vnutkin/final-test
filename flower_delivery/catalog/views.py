# catalog/views.py
from django.shortcuts import get_object_or_404, redirect
from catalog.models import Product
from orders.models import BasketItem
from django.shortcuts import render
def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog/product_list.html', {'products': products})



def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        basket_item, created = BasketItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )
        if not created:
            basket_item.quantity += 1
            basket_item.save()
    return redirect('view_cart')