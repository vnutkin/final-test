# orders/tests.py
from django.test import TestCase
from django.utils import timezone
from .utils import is_working_time

class WorkingTimeTest(TestCase):
    def test_working_hours(self):

        self.assertTrue(is_working_time())
