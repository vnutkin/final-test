# catalog/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    shop = models.ForeignKey("orders.Shop", on_delete=models.CASCADE)  # Используем строковое представление



