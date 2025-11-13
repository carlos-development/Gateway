# apps/services/admin.py
from django.contrib import admin
from .models import ServiceCategory, Service

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin para categorías de servicios"""
    list_display = ['name', 'slug', 'icon', 'order', 'active']
    list_editable = ['order', 'active']
    list_filter = ['active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin para servicios"""
    list_display = ['name', 'category', 'icon', 'active', 'featured']
    list_editable = ['active', 'featured']
    list_filter = ['category', 'active', 'featured']
    search_fields = ['name', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('category', 'name', 'slug', 'icon', 'image')
        }),
        ('Descripciones', {
            'fields': ('short_description', 'full_description')
        }),
        ('Características', {
            'fields': ('features',),
            'description': 'Ingrese las características en formato JSON array, ejemplo: ["Característica 1", "Característica 2"]'
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('active', 'featured')
        }),
    )