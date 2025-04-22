# orders/urls.py
from django.urls import path
from .views import OrderHistoryView, create_order

urlpatterns = [
    path('history/', OrderHistoryView.as_view(), name='order_history'),
    path('create/', create_order, name='create_order'),
]
