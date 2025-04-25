# orders/urls.py
from django.urls import path
from .views import OrderHistoryView, create_order, admin_order_list, update_order_status
from . import views
from catalog.views import add_to_cart

urlpatterns = [
    path('history/', OrderHistoryView.as_view(), name='order_history'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create-order/', views.create_order, name='create_order'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('admin/orders/', admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/update/', update_order_status, name='update_order_status'),
    path('cart/cancel/', views.cancel_order, name='cancel_order'),
]
