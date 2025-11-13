# apps/core/admin.py
from django.contrib import admin
from .models import CompanyInfo, ValueCard, Client, Brand

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    """Admin para información de la empresa"""
    list_display = ['name', 'phone', 'email']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slogan', 'description')
        }),
        ('Contacto', {
            'fields': ('phone', 'email', 'address', 'business_hours')
        }),
        ('Redes Sociales', {
            'fields': ('facebook_url', 'whatsapp_number', 'instagram_url', 'linkedin_url')
        }),
        ('Métricas Hero', {
            'fields': ('years_experience', 'security_percentage', 'support_availability')
        }),
    )
    
    def has_add_permission(self, request):
        # Solo permitir una instancia
        return not CompanyInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar
        return False

@admin.register(ValueCard)
class ValueCardAdmin(admin.ModelAdmin):
    """Admin para valores de la empresa"""
    list_display = ['title', 'icon', 'order', 'active']
    list_editable = ['order', 'active']
    list_filter = ['active']
    search_fields = ['title', 'description']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin para clientes"""
    list_display = ['name', 'order', 'active']
    list_editable = ['order', 'active']
    list_filter = ['active']
    search_fields = ['name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin para marcas"""
    list_display = ['name', 'order', 'active']
    list_editable = ['order', 'active']
    list_filter = ['active']
    search_fields = ['name']