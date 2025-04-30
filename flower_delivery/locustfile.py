import os
import sys
import django
from django.urls import reverse
from locust import HttpUser, task, between
import random
import logging

# Инициализация Django
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flower_delivery.settings")
django.setup()

logger = logging.getLogger(__name__)


class StoreUser(HttpUser):
    wait_time = between(1, 3)
    csrftoken = ""
    session_id = ""

    def on_start(self):
        try:
            # Регистрация и вход пользователя
            response = self.client.get(reverse("register"))
            self.csrftoken = response.cookies.get("csrftoken", "")

            phone = f"79{random.randint(100000000, 999999999)}"
            self.client.post(
                reverse("register"),
                {
                    "phone": phone,
                    "password1": "TestPass123!",
                    "password2": "TestPass123!"
                },
                headers={
                    "X-CSRFToken": self.csrftoken,
                    "Referer": self.host + reverse("register")
                }
            )

            self.csrftoken = self.client.get(reverse("login")).cookies.get("csrftoken", "")
            self.client.post(
                reverse("login"),
                {
                    "username": phone,
                    "password": "TestPass123!"
                },
                headers={
                    "X-CSRFToken": self.csrftoken,
                    "Referer": self.host + reverse("login")
                }
            )
            self.session_id = self.client.cookies.get("sessionid", "")

        except Exception as e:
            logger.error(f"Ошибка инициализации пользователя: {str(e)}")

    @task(5)
    def view_catalog(self):
        self.client.get(
            reverse("product_list"),
            headers={"Cookie": f"sessionid={self.session_id}"}
        )


class AdminUser(HttpUser):
    wait_time = between(2, 5)
    csrftoken = ""
    session_id = ""

    def on_start(self):
        try:
            response = self.client.get(reverse("login"))
            self.csrftoken = response.cookies.get("csrftoken", "")

            login_response = self.client.post(
                reverse("login"),
                {
                    "phone": "11111",
                    "password": "12345"
                },
                headers={
                    "X-CSRFToken": self.csrftoken,
                    "Referer": self.host + reverse("login")
                }
            )
            self.session_id = login_response.cookies.get("sessionid", "")

        except Exception as e:
            logger.error(f"Ошибка инициализации администратора: {str(e)}")

    @task(3)
    def manage_orders(self):
        self.client.get(
            reverse("admin_order_list"),
            headers={"Cookie": f"sessionid={self.session_id}"}
        )