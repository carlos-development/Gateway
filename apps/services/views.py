# ==========================================
# apps/services/views.py - OPTIMIZADO
# ==========================================

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Service, ServiceCategory

def service_list(request):
    """
    Lista de servicios optimizada.
    
    Optimizaciones:
    1. select_related() para categorías
    2. only() para campos necesarios
    3. Paginación
    """
    # Servicios activos con categoría en 1 query
    services = Service.objects.filter(
        active=True
    ).select_related('category').only(
        'id', 'name', 'slug', 'short_description',
        'icon', 'image', 'category__name',
        'category__icon', 'category__slug'
    ).order_by('category__order', 'name')
    
    # Paginación
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Categorías activas
    categories = ServiceCategory.objects.filter(
        active=True
    ).only('id', 'name', 'slug', 'icon', 'description')
    
    context = {
        'services': page_obj,
        'categories': categories,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'services/service_list.html', context)


def service_detail(request, slug):
    """
    Detalle de servicio optimizado.
    """
    # Obtener servicio con categoría
    service = get_object_or_404(
        Service.objects.select_related('category'),
        slug=slug,
        active=True
    )
    
    # Servicios relacionados
    related_services = Service.objects.filter(
        category=service.category,
        active=True
    ).exclude(
        id=service.id
    ).select_related('category').only(
        'id', 'name', 'slug', 'short_description', 'icon', 'image',
        'category__name', 'category__icon'
    )[:4]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    
    return render(request, 'services/service_detail.html', context)


def service_category(request, slug):
    """
    Filtrar servicios por categoría - Optimizado.
    """
    # Obtener categoría
    category = get_object_or_404(
        ServiceCategory,
        slug=slug,
        active=True
    )
    
    # Servicios de esta categoría
    services = Service.objects.filter(
        category=category,
        active=True
    ).select_related('category').only(
        'id', 'name', 'slug', 'short_description', 'icon', 'image',
        'category__name', 'category__icon'
    )
    
    # Paginación
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Todas las categorías
    categories = ServiceCategory.objects.filter(
        active=True
    ).only('id', 'name', 'slug', 'icon')
    
    context = {
        'category': category,
        'services': page_obj,
        'categories': categories,
        'selected_category': category,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'services/service_list.html', context)

