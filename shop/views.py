from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from .models import User, Order, Product, OrderItem


def recent_orders_view(request):
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    
    # Аннотируем количество заказов за последние 30 дней для каждого пользователя
    users_with_recent_orders = User.objects.annotate(
        recent_order_count=Count('order', filter=Q(order__created_at__gte=thirty_days_ago))
    ).filter(recent_order_count__gt=0)

    return render(request, 'shop/recent_orders.html', {'users': users_with_recent_orders})


def product_filter_view(request):
    """
    Основное представление для фильтрации и сортировки товаров.
    Поддерживает фильтрацию по категории, цене, дате и сортировку по разным параметрам.
    Включает пагинацию и AJAX-поддержку.
    """
    # Получаем параметры фильтрации из GET-запроса
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort', 'popularity')  # по умолчанию сортировка по популярности
    page = request.GET.get('page', 1)
    
    # Базовый queryset с аннотацией количества заказов для сортировки по популярности
    products = Product.objects.annotate(
        order_count=Count('orderitem')  # считаем количество заказов для каждого товара
    )
    
    # Применяем фильтры
    if category:
        products = products.filter(category__icontains=category)  # поиск по части названия категории
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))  # цена больше или равна
        except ValueError:
            pass  # игнорируем некорректные значения
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))  # цена меньше или равна
        except ValueError:
            pass
    
    # Фильтрация по дате добавления
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            products = products.filter(created_at__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Добавляем время до конца дня
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            products = products.filter(created_at__lte=date_to_obj)
        except ValueError:
            pass
    
    # Применяем сортировку
    sort_options = {
        'popularity': '-order_count',      # по популярности (убывание)
        'price_asc': 'price',             # по цене (возрастание)
        'price_desc': '-price',           # по цене (убывание)
        'date_asc': 'created_at',         # по дате (сначала старые)
        'date_desc': '-created_at',       # по дате (сначала новые)
        'name': 'name',                   # по названию (алфавит)
    }
    
    if sort_by in sort_options:
        products = products.order_by(sort_options[sort_by])
    else:
        products = products.order_by('-order_count')  # по умолчанию по популярности
    
    # Пагинация - 10 товаров на страницу
    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(page)
    
    # Получаем уникальные категории для фильтра (правильный способ)
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
    
    context = {
        'products': page_obj,
        'categories': categories,
        'current_filters': {
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort_by,
        },
        'total_count': products.count(),
    }
    
    # AJAX-поддержка: если запрос через AJAX, возвращаем только часть HTML
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('shop/product_list_ajax.html', context, request=request)
        return JsonResponse({
            'html': html,
            'total_count': products.count(),
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })
    
    return render(request, 'shop/product_list.html', context)


def popular_products_view(request):
    products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')  # сортировка по количеству заказов в убывающем порядке

    return render(request, 'shop/popular_products.html', {'products': products})

def combined_filter_view(request):
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-order_count')
    
    products = Product.objects.annotate(
        order_count=Count('orderitem')
    )
    
    if category:
        products = products.filter(category=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    products = products.order_by(sort)
    
    return render(request, 'shop/combined_filter.html', {'products': products})

def get_product_stats(request):
    """
    AJAX-представление для получения статистики товаров.
    Возвращает общее количество товаров и количество по категориям.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_products = Product.objects.count()
        
        # Статистика по категориям
        category_stats = Product.objects.values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        # Самые популярные товары (топ-5)
        popular_products = Product.objects.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:5]
        
        popular_list = [
            {
                'name': product.name,
                'category': product.category,
                'order_count': product.order_count,
                'price': float(product.price)
            }
            for product in popular_products
        ]
        
        return JsonResponse({
            'total_products': total_products,
            'category_stats': list(category_stats),
            'popular_products': popular_list,
        })
    
    return JsonResponse({'error': 'Only AJAX requests allowed'}, status=400)