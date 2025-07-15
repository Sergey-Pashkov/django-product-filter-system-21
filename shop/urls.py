from django.urls import path
from . import views

urlpatterns = [
    # Главная страница - показываем список товаров с фильтрацией
    path('', views.product_filter_view, name='product_list'),
    
    # Старые маршруты (сохраняем для совместимости)
    path('recent-orders/', views.recent_orders_view, name='recent_orders'),
    path('popular-products/', views.popular_products_view, name='popular_products'),
    path('combined-filter/', views.combined_filter_view, name='combined_filter'),
    
    # Новые маршруты для улучшенной фильтрации
    path('products/', views.product_filter_view, name='product_filter'),
    path('products/stats/', views.get_product_stats, name='product_stats'),
]