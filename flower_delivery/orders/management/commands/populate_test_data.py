# orders/management/commands/populate_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from catalog.models import Product
from orders.models import Order, BasketItem, Shop
from faker import Faker
import random

User = get_user_model()
fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Generate test data for performance testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=50)
        parser.add_argument('--products', type=int, default=10)
        parser.add_argument('--orders', type=int, default=50)

    def handle(self, *args, **options):
        # Создание магазинов
        self.create_shops()

        # Создание пользователей
        self.create_users(options['users'])

        # Создание товаров
        self.create_products(options['products'])

        # Создание заказов
        self.create_orders(options['orders'])

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created: "
                f"{options['users']} users, "
                f"{options['products']} products, "
                f"{options['orders']} orders"
            )
        )

    def create_shops(self):
        for _ in range(5):
            Shop.objects.get_or_create(
                name=fake.company(),
                id_telegram=fake.numerify('79########')
            )

    def create_users(self, count):
        for _ in range(count):
            User.objects.create_user(
                username=fake.word().capitalize(),
                phone=fake.numerify('79########'),
                password='testpass123'
            )

    def create_products(self, count):
        shops = Shop.objects.all()
        for _ in range(count):
            Product.objects.create(
                name=fake.word().capitalize(),
                price=random.randint(100, 5000),
                image='products/default.jpg',
                shop=random.choice(shops)
            )

    def create_orders(self, count):
        users = User.objects.all()
        products = Product.objects.all()
        for _ in range(count):
            user = random.choice(users)  # Выбираем пользователя
            order = Order.objects.create(
                user=user,
                status=random.choice(['created', 'paid', 'delivering']),
                address=fake.address(),
                comment=fake.text(max_nb_chars=100)
            )
            # Добавляем товары в заказ
            for _ in range(random.randint(1, 5)):
                BasketItem.objects.create(
                    user=user,  # <-- Добавьте эту строку
                    product=random.choice(products),
                    order=order,
                    quantity=random.randint(1, 3)
                )