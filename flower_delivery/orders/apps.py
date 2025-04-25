# orders/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        # Импорт ВНУТРИ метода ready() после инициализации приложений
        from .models import Order
        from bot.handlers import send_to_telegram_bot

        # Регистрация сигнала
        @receiver(post_save, sender=Order)
        def notify_shop(sender, instance, **kwargs):
            if kwargs.get('created', False):
                # Получаем первый товар из корзины
                basket_item = instance.basketitem_set.first()

                if basket_item and hasattr(basket_item.product, 'shop'):
                    shop = basket_item.product.shop
                    send_to_telegram_bot(
                        shop.id_telegram,
                        f"Новый заказ #{instance.id}"
                    )

