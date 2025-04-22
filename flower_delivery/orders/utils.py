# orders/utils.py
from django.utils import timezone
from datetime import time


def is_working_time():
    """Проверяет текущее время в часовом поясе проекта"""
    now = timezone.localtime().time()
    return time(9, 0) <= now <= time(17, 0)
