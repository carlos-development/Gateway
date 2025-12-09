# ==========================================
# GATEWAY IT - VIEWS OPTIMIZADAS
# Optimización de consultas a la base de datos
# ==========================================

"""
ANTES vs DESPUÉS - Comparación de Queries

ANTES (Sin optimizar):
- product_list: 1 query + N queries (1 por cada producto para obtener categoría)
- Si tienes 20 productos = 21 queries

DESPUÉS (Optimizado):
- product_list: 1 query con JOIN
- 20 productos = 1 query

REDUCCIÓN: ~95% menos queries
"""

# ==========================================
# apps/core/views.py - OPTIMIZADO
# ==========================================

from django.shortcuts import render
from django.core.cache import cache
from apps.core.models import CompanyInfo, ValueCard, Client, Brand
from apps.products.models import Product
from apps.services.models import Service

def home(request):
    """
    Vista optimizada para la página de inicio.
    
    Optimizaciones aplicadas:
    1. select_related() para relaciones ForeignKey
    2. only() para limitar campos consultados
    3. Caché de datos que no cambian frecuentemente
    """
    # Intentar obtener datos del caché primero
    cache_key = 'home_page_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        context = cached_data
    else:
        # Obtener información de la empresa (singleton - solo 1 registro)
        company_info = CompanyInfo.objects.first()
        
        # Valores activos - solo campos necesarios
        value_cards = ValueCard.objects.filter(
            active=True
        ).only('title', 'description', 'icon', 'order')
        
        # Clientes activos - optimizado con only()
        clients = Client.objects.filter(
            active=True
        ).only('name', 'logo', 'order')
        
        # Marcas activas - optimizado con only()
        brands = Brand.objects.filter(
            active=True
        ).only('name', 'logo', 'order')
        
        # Productos destacados con su categoría en 1 query
        featured_products = Product.objects.filter(
            active=True,
            featured=True
        ).select_related('category').only(
            'name', 'slug', 'price', 'image', 'icon',
            'category__name', 'category__icon'
        )[:6]
        
        # Servicios destacados con su categoría en 1 query
        featured_services = Service.objects.filter(
            active=True,
            featured=True
        ).select_related('category').only(
            'name', 'slug', 'short_description', 'icon', 'image',
            'category__name', 'category__icon'
        )[:6]
        
        context = {
            'company_info': company_info,
            'value_cards': value_cards,
            'clients': clients,
            'brands': brands,
            'featured_products': featured_products,
            'featured_services': featured_services,
        }
        
        # Cachear por 15 minutos (datos que no cambian frecuentemente)
        cache.set(cache_key, context, 60 * 15)
    
    return render(request, 'core/home.html', context)