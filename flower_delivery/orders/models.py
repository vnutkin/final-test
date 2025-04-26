# orders/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_order_update_notification  # Импортируйте из utils
import asyncio

class Order(models.Model):
    STATUS_CHOICES = [
        ('gathering', 'Набор'),
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('delivering', 'Доставляется'),
        ('completed', 'Выполнен'),
    ]
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    address = models.TextField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"

    def clean(self):
        if self.pk:
            # Импорт внутри метода
            from .utils import is_working_time
            if not is_working_time():
                raise ValidationError("Изменения разрешены только в рабочее время")


    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)


class Shop(models.Model):  # Корректное определение
    id_telegram = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, default="Новый магазин")

    def __str__(self):
        return self.name

    # orders/models.py
class BasketItem(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)  # Новое поле

    def __str__(self):
        return f"{self.user.phone} - {self.product.name} ({self.quantity})"
