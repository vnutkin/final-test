# orders/models.py
from django.db import models
from django.core.exceptions import ValidationError


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('delivering', 'Доставляется'),
        ('completed', 'Выполнен')
    ]
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    address = models.TextField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Запрет изменений статуса вне рабочего времени"""
        from .utils import is_working_time
        if self.pk and not is_working_time():
            raise ValidationError("Изменения разрешены только в рабочее время")


class Shop(models.Model):  # Корректное определение
    id_telegram = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, default="Новый магазин")


class BasketItem(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
