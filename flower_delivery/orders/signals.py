# orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from flower_delivery.bot.handlers import send_to_telegram_bot


@receiver(post_save, sender=Order)
def notify_shop(sender, instance, **kwargs):
    if kwargs['created']:
        # Отправка уведомления только в рабочее время
        from .utils import is_working_time
        if is_working_time():
            send_to_telegram_bot(instance.shop.id_telegram, f"Новый заказ #{instance.id}")
