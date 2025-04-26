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
                # Асинхронный вызов через отдельный поток
                import threading
                def async_task():
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    basket_item = instance.basketitem_set.first()
                    if basket_item and basket_item.product.shop:
                        shop = basket_item.product.shop
#                        loop.run_until_complete(
#                            send_to_telegram_bot(shop.id_telegram, f"Новый заказ #{instance.id}")
#                        )
                    loop.close()

                thread = threading.Thread(target=async_task, daemon=True)
                thread.start()

