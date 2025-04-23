# orders/apps.py
# orders/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        # Отложенный импорт внутри метода ready()
        from .models import Order
        from bot.handlers import send_to_telegram_bot  # Измените здесь

        @receiver(post_save, sender=Order)
        def notify_shop(sender, instance, **kwargs):
            if kwargs.get('created', False):
                from .utils import is_working_time
                if is_working_time():
                    send_to_telegram_bot(
                        instance.shop.id_telegram,
                        f"Новый заказ #{instance.id}"
                    )