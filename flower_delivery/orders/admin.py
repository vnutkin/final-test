# orders/admin.py
from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('id', 'user__phone')
    actions = ['mark_paid', 'mark_delivering', 'mark_completed']  # Добавляем кастомные действия

    @admin.action(description="Пометить как оплаченные")
    def mark_paid(self, request, queryset):
        queryset.update(status='paid')

    @admin.action(description="Пометить как доставляется")
    def mark_delivering(self, request, queryset):
        queryset.update(status='delivering')

    @admin.action(description="Пометить как выполнен")
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')