# apps/products/models.py
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal

class ProductCategory(models.Model):
    """Categorías de productos"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(
        max_length=50, 
        help_text="Clase de Font Awesome",
        default="fas fa-box"
    )
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Productos del e-commerce"""
    
    # Información básica
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    sale_price = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Inventario
    sku = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)
    
    # API Mayorista
    api_product_id = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="ID del producto en la API del mayorista"
    )
    last_api_sync = models.DateTimeField(null=True, blank=True)
    
    # Multimedia
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    icon = models.CharField(
        max_length=50, 
        default='fas fa-box',
        help_text="Icono Font Awesome si no hay imagen"
    )
    
    # Especificaciones técnicas (JSON)
    specifications = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Especificaciones técnicas como JSON object"
    )
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Estado
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=['category', 'active']),
            models.Index(fields=['sku']),
            models.Index(fields=['api_product_id']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def final_price(self):
        """Retorna el precio final (con descuento si aplica)"""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def has_discount(self):
        """Verifica si el producto tiene descuento"""
        return self.sale_price is not None and self.sale_price < self.price
    
    @property
    def discount_percentage(self):
        """Calcula el porcentaje de descuento"""
        if self.has_discount:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return round(discount)
        return 0
    
    @property
    def in_stock(self):
        """Verifica si hay stock disponible"""
        return self.stock > 0

    @property
    def primary_image(self):
        """Retorna la imagen principal del producto"""
        # Intentar obtener la imagen marcada como principal
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url
        # Si no hay principal, usar la primera imagen
        first = self.images.first()
        if first:
            return first.image.url
        # Si no hay imágenes en la galería, usar la imagen del campo directo
        if self.image:
            return self.image.url
        return None

    @property
    def all_images(self):
        """Retorna todas las imágenes del producto"""
        return self.images.all()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Imágenes adicionales de productos (galería)"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    is_primary = models.BooleanField(
        default=False,
        help_text="Imagen principal del producto"
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"

    def __str__(self):
        return f"{self.product.name} - Imagen {self.order}"

    def save(self, *args, **kwargs):
        # Si es la primera imagen, marcarla como principal
        if not self.pk and not self.product.images.exists():
            self.is_primary = True
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Carrito de compras (basado en sesión)"""
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"
    
    def __str__(self):
        return f"Carrito {self.session_key}"
    
    @property
    def total(self):
        """Calcula el total del carrito"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def item_count(self):
        """Cuenta total de items"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def formatted_total(self):
        """Total formateado para mostrar"""
        return f"${self.total:,.0f}"


class CartItem(models.Model):
    """Items del carrito"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=0)
    
    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        """Calcula el subtotal del item"""
        return self.quantity * self.price
    
    @property
    def formatted_subtotal(self):
        """Subtotal formateado para mostrar"""
        return f"${self.subtotal:,.0f}"
    
    def save(self, *args, **kwargs):
        # Guardar el precio actual del producto al agregar al carrito
        if not self.pk:
            self.price = self.product.final_price
        super().save(*args, **kwargs)