# catalog/models.py
# catalog/models.py
from django.db import models  # <-- Добавьте эту строку
from orders.models import Shop, Order  # Если используется модель Shop из другого приложения

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)



