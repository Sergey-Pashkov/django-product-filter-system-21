from django.db import models


from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Product(models.Model):
    # Основные поля товара
    name = models.CharField(max_length=100, verbose_name='Название')
    category = models.CharField(max_length=50, verbose_name='Категория')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    # Дата добавления товара - автоматически устанавливается при создании
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        # Сортировка по умолчанию - сначала новые товары
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_order_count(self):
        """
        Метод для подсчета популярности товара (количество заказов).
        Считает, сколько раз данный товар был заказан.
        """
        return OrderItem.objects.filter(product=self).count()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f"Заказ #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
    
    def __str__(self):
        return f"Товар: {self.product.name}, Количество: {self.quantity}"
