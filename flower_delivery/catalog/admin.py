from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'shop')
    list_filter = ('shop',)
    search_fields = ('name',)
    fields = ('name', 'price', 'image', 'shop')