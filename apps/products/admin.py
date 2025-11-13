# apps/products/admin.py
from django.contrib import admin
from .models import ProductCategory, Product, Cart, CartItem

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin para categorías de productos"""
    list_display = ['name', 'slug', 'icon', 'order', 'active']
    list_editable = ['order', 'active']
    list_filter = ['active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin para productos"""
    list_display = ['name', 'category', 'sku', 'final_price', 'stock', 'active', 'featured']
    list_editable = ['active', 'featured']
    list_filter = ['category', 'active', 'featured', 'created_at']
    search_fields = ['name', 'sku', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'last_api_sync']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('category', 'name', 'slug', 'sku')
        }),
        ('Descripciones', {
            'fields': ('short_description', 'full_description')
        }),
        ('Precios', {
            'fields': ('price', 'sale_price')
        }),
        ('Inventario', {
            'fields': ('stock',)
        }),
        ('Multimedia', {
            'fields': ('image', 'icon')
        }),
        ('Especificaciones Técnicas', {
            'fields': ('specifications',),
            'description': 'Especificaciones en formato JSON, ejemplo: {"Procesador": "Intel i7", "RAM": "16GB"}'
        }),
        ('API Mayorista', {
            'fields': ('api_product_id', 'last_api_sync'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('active', 'featured', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'deactivate_products']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(featured=True)
    mark_as_featured.short_description = "Marcar como destacado"
    
    def mark_as_not_featured(self, request, queryset):
        queryset.update(featured=False)
    mark_as_not_featured.short_description = "Quitar de destacados"
    
    def deactivate_products(self, request, queryset):
        queryset.update(active=False)
    deactivate_products.short_description = "Desactivar productos"

class CartItemInline(admin.TabularInline):
    """Inline para items del carrito"""
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'subtotal']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin para carritos"""
    list_display = ['session_key', 'item_count', 'formatted_total', 'created_at']
    readonly_fields = ['session_key', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def has_add_permission(self, request):
        return False