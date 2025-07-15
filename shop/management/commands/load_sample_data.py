"""
Команда Django для создания тестовых данных для демонстрации системы фильтрации товаров.

Использование:
python manage.py load_sample_data

Эта команда создает:
- Тестового пользователя
- Товары разных категорий с разными датами создания
- Заказы с разной популярностью товаров
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Product, Order, OrderItem
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Загружает тестовые данные для демонстрации системы фильтрации товаров'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед загрузкой новых',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Очистка существующих данных...')
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Данные очищены.'))

        # Создаем тестового пользователя, если его нет
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Тест',
                'last_name': 'Пользователь'
            }
        )
        if created:
            user.set_password('testpassword123')
            user.save()
            self.stdout.write(f'Создан пользователь: {user.username}')

        # Данные товаров с разными датами создания
        products_data = [
            # Электроника (дорогие товары)
            ('Смартфон iPhone 15', 'Электроника', 89000, -30),
            ('Ноутбук Dell XPS', 'Электроника', 75000, -25),
            ('Планшет Samsung Galaxy', 'Электроника', 35000, -20),
            ('Наушники Sony WH-1000XM5', 'Электроника', 25000, -15),
            ('Телевизор LG OLED', 'Электроника', 120000, -22),
            ('Монитор 4K', 'Электроника', 35000, -18),
            ('Клавиатура механическая', 'Электроника', 8500, -12),
            ('Мышка игровая', 'Электроника', 4500, -8),
            ('Веб-камера', 'Электроника', 6500, -5),
            ('Микрофон студийный', 'Электроника', 15000, -14),
            
            # Одежда (средний ценовой сегмент)
            ('Джинсы Levis 501', 'Одежда', 6500, -10),
            ('Кроссовки Nike Air Max', 'Одежда', 12000, -7),
            ('Платье летнее Zara', 'Одежда', 4500, -5),
            ('Куртка зимняя North Face', 'Одежда', 25000, -28),
            ('Рубашка хлопковая', 'Одежда', 3500, -6),
            ('Футболка базовая', 'Одежда', 1500, -4),
            ('Носки хлопковые (5 пар)', 'Одежда', 800, -3),
            ('Кепка New Era', 'Одежда', 2500, -9),
            ('Свитер шерстяной', 'Одежда', 8500, -16),
            ('Юбка джинсовая', 'Одежда', 3200, -11),
            
            # Бытовые товары (недорогие)
            ('Пылесос Dyson', 'Бытовая техника', 35000, -12),
            ('Микроволновка Samsung', 'Бытовая техника', 12000, -18),
            ('Кофеварка Nespresso', 'Бытовая техника', 15000, -7),
            ('Блендер Vitamix', 'Бытовая техника', 45000, -20),
            ('Утюг Philips', 'Бытовая техника', 4500, -6),
            ('Фен для волос', 'Бытовая техника', 3500, -4),
            ('Швабра с отжимом', 'Бытовая техника', 1200, -2),
            ('Стиральный порошок (3кг)', 'Бытовая химия', 650, -1),
            ('Жидкое мыло (500мл)', 'Бытовая химия', 350, -1),
            ('Средство для мытья посуды', 'Бытовая химия', 180, -1),
        ]

        # Создаем товары
        created_products = []
        for name, category, price, days_ago in products_data:
            created_date = datetime.now() - timedelta(days=abs(days_ago))
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'price': price,
                    'created_at': created_date
                }
            )
            if created:
                created_products.append(product)
                self.stdout.write(f'Создан товар: {name} ({created_date.strftime("%Y-%m-%d")})')
            else:
                # Обновляем существующий товар
                product.category = category
                product.price = price
                product.created_at = created_date
                product.save()
                created_products.append(product)
                self.stdout.write(f'Обновлен товар: {name}')

        # Создаем заказы для демонстрации популярности
        self.stdout.write('Создание заказов...')
        
        # Определяем товары, которые должны быть популярными
        popular_items = [
            'Наушники Sony WH-1000XM5',
            'Кроссовки Nike Air Max', 
            'Смартфон iPhone 15',
            'Кофеварка Nespresso',
            'Джинсы Levis 501'
        ]
        
        # Создаем 50 заказов
        orders_created = 0
        for i in range(50):
            order = Order.objects.create(user=user)
            
            # Каждый заказ содержит 1-4 товара
            items_in_order = random.randint(1, 4)
            
            for j in range(items_in_order):
                # 60% шанс взять популярный товар, 40% - случайный
                if random.random() < 0.6 and popular_items:
                    try:
                        product_name = random.choice(popular_items)
                        product = Product.objects.get(name=product_name)
                    except Product.DoesNotExist:
                        product = random.choice(created_products)
                else:
                    product = random.choice(created_products)
                
                quantity = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )
            
            orders_created += 1

        self.stdout.write(f'Создано {orders_created} заказов')

        # Выводим статистику
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_order_items = OrderItem.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n=== СТАТИСТИКА ==='))
        self.stdout.write(self.style.SUCCESS(f'Товаров: {total_products}'))
        self.stdout.write(self.style.SUCCESS(f'Заказов: {total_orders}'))
        self.stdout.write(self.style.SUCCESS(f'Позиций в заказах: {total_order_items}'))
        
        # Показываем топ-5 популярных товаров
        from django.db.models import Count
        top_products = Product.objects.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:5]
        
        self.stdout.write(self.style.SUCCESS(f'\nТОП-5 ПОПУЛЯРНЫХ ТОВАРОВ:'))
        for i, product in enumerate(top_products, 1):
            self.stdout.write(f'{i}. {product.name} - {product.order_count} заказов')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Тестовые данные успешно загружены!'))
        self.stdout.write(f'Теперь можно тестировать фильтрацию и сортировку на сайте.')
