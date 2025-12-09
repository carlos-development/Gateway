# apps/products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductCategory, Product, ProductImage, Cart, CartItem

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """Admin para categorías de productos"""
    list_display = ['name', 'slug', 'icon', 'order', 'active']
    list_editable = ['order', 'active']
    list_filter = ['active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    """Inline para imágenes de productos"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'is_primary', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return "Sin imagen"
    image_preview.short_description = "Vista previa"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin para productos"""
    list_display = ['name', 'category', 'sku', 'final_price', 'stock', 'active', 'featured', 'image_count']
    list_editable = ['active', 'featured']
    list_filter = ['category', 'active', 'featured', 'created_at']
    search_fields = ['name', 'sku', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'last_api_sync']
    inlines = [ProductImageInline]

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
        ('Multimedia (Imagen de respaldo)', {
            'fields': ('image', 'icon'),
            'description': 'La imagen principal se gestiona en la galería de imágenes abajo'
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

    def image_count(self, obj):
        count = obj.images.count()
        if count > 0:
            return format_html('<span style="color: green;">✓ {} imágenes</span>', count)
        return format_html('<span style="color: orange;">⚠ Sin imágenes</span>')
    image_count.short_description = "Galería"

    def mark_as_featured(self, request, queryset):
        queryset.update(featured=True)
    mark_as_featured.short_description = "Marcar como destacado"

    def mark_as_not_featured(self, request, queryset):
        queryset.update(featured=False)
    mark_as_not_featured.short_description = "Quitar de destacados"

    def deactivate_products(self, request, queryset):
        queryset.update(active=False)
    deactivate_products.short_description = "Desactivar productos"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin para imágenes de productos"""
    list_display = ['product', 'order', 'is_primary', 'image_thumbnail']
    list_filter = ['is_primary', 'product__category']
    list_editable = ['order', 'is_primary']
    search_fields = ['product__name', 'alt_text']

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 80px;" />', obj.image.url)
        return "Sin imagen"
    image_thumbnail.short_description = "Miniatura"

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