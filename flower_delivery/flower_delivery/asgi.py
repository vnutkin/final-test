"""
ASGI config for flower_delivery project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""


import os
from django.core.asgi import get_asgi_application
from bot.apps import BotConfig

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
application = get_asgi_application()

# Инициализация бота
import asyncio
asyncio.create_task(BotConfig.start_bot(BotConfig))