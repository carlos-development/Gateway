# apps/core/views.py
from django.shortcuts import render
from apps.core.models import CompanyInfo, ValueCard, Client, Brand
from apps.products.models import ProductCategory, Product
from apps.services.models import ServiceCategory, Service

def home(request):
    """
    Vista para la página de inicio.
    """
    company_info = CompanyInfo.objects.first()
    value_cards = ValueCard.objects.filter(active=True)
    clients = Client.objects.filter(active=True)
    brands = Brand.objects.filter(active=True)
    
    # Obtener productos y servicios destacados
    featured_products = Product.objects.filter(active=True, featured=True)[:6]
    featured_services = Service.objects.filter(active=True, featured=True)[:6]
    
    # Obtener categorías
    product_categories = ProductCategory.objects.filter(active=True)
    service_categories = ServiceCategory.objects.filter(active=True)

    context = {
        'company_info': company_info,
        'value_cards': value_cards,
        'clients': clients,
        'brands': brands,
        'featured_products': featured_products,
        'featured_services': featured_services,
        'product_categories': product_categories,
        'service_categories': service_categories,
    }
    
    return render(request, 'core/home.html', context)