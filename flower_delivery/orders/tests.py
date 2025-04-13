# orders/tests.py
from django.test import TestCase
from django.utils import timezone
from .utils import is_working_time

class WorkingTimeTest(TestCase):
    def test_working_hours(self):
        # Тест для времени 10:00
        test_time = timezone.datetime(2023, 10, 1, 10, 0).time()
        self.assertTrue(is_working_time(test_time))