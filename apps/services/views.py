# apps/services/views.py
from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory

def service_list(request):
    """
    Lista todos los servicios activos.
    """
    services = Service.objects.filter(active=True)
    categories = ServiceCategory.objects.filter(active=True)
    context = {
        'services': services,
        'categories': categories,
    }
    return render(request, 'services/service_list.html', context)

def service_detail(request, slug):
    """
    Muestra el detalle de un servicio.
    """
    service = get_object_or_404(Service, slug=slug, active=True)
    related_services = Service.objects.filter(category=service.category, active=True).exclude(id=service.id)[:4]
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'services/service_detail.html', context)

def service_category(request, slug):
    """
    Filtra servicios por categoría.
    """
    category = get_object_or_404(ServiceCategory, slug=slug, active=True)
    services = Service.objects.filter(category=category, active=True)
    context = {
        'category': category,
        'services': services,
    }
    return render(request, 'services/service_list.html', context)