# apps/payments/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from decimal import Decimal
import uuid

User = get_user_model()


class Order(models.Model):
    """Pedido/Orden de compra"""

    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'Procesando'),
        ('PAID', 'Pagado'),
        ('FAILED', 'Fallido'),
        ('CANCELLED', 'Cancelado'),
        ('REFUNDED', 'Reembolsado'),
    ]

    # Identificación
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, editable=False)

    # Usuario y contacto
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
        help_text="Usuario que realizó el pedido (puede ser null para invitados)"
    )
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_name = models.CharField(max_length=200)

    # Información del pedido
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    shipping_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )

    # Estado y seguimiento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, help_text="Notas internas del pedido")

    # Dirección de envío
    shipping_address = models.JSONField(
        null=True,
        blank=True,
        help_text="Dirección de envío en formato JSON"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['customer_email']),
        ]

    def __str__(self):
        return f"Pedido {self.order_number} - {self.customer_email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generar número de orden único
            import random
            import string
            timestamp = str(int(self.created_at.timestamp())) if self.created_at else str(int(uuid.uuid4().int))[:10]
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.order_number = f"GW-{timestamp}-{random_str}"
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        """Calcula el subtotal (total - tax - shipping)"""
        return self.total_amount - self.tax_amount - self.shipping_amount

    @property
    def items_total(self):
        """Suma total de los items del pedido"""
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    """Items del pedido"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))]
    )

    # Referencia opcional al producto (puede ser null si se eliminó)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )

    class Meta:
        verbose_name = "Item del Pedido"
        verbose_name_plural = "Items del Pedido"

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class Payment(models.Model):
    """Pago asociado a un pedido"""

    PAYMENT_METHOD_CHOICES = [
        ('CARD', 'Tarjeta de Crédito/Débito'),
        ('PSE', 'PSE'),
        ('NEQUI', 'Nequi'),
        ('BANCOLOMBIA', 'Bancolombia'),
        ('BANCOLOMBIA_TRANSFER', 'Bancolombia Transfer'),
        ('BANCOLOMBIA_COLLECT', 'Bancolombia Collect'),
        ('BANCOLOMBIA_QR', 'Bancolombia QR'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobado'),
        ('DECLINED', 'Rechazado'),
        ('ERROR', 'Error'),
        ('VOIDED', 'Anulado'),
    ]

    # Identificación
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relaciones
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Información de Wompi
    wompi_transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="ID de la transacción en Wompi"
    )
    wompi_reference = models.CharField(
        max_length=100,
        unique=True,
        help_text="Referencia única de la transacción"
    )

    # Detalles del pago
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    currency = models.CharField(max_length=3, default='COP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Datos adicionales del método de pago (JSON)
    payment_method_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Datos específicos del método de pago (número de tarjeta enmascarado, banco PSE, etc.)"
    )

    # URLs
    redirect_url = models.URLField(
        blank=True,
        help_text="URL de redirección después del pago"
    )

    # Respuesta completa de Wompi
    wompi_response = models.JSONField(
        null=True,
        blank=True,
        help_text="Respuesta completa de la API de Wompi"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['wompi_transaction_id']),
            models.Index(fields=['wompi_reference']),
        ]

    def __str__(self):
        return f"Pago {self.wompi_reference} - {self.get_payment_method_display()} - {self.get_status_display()}"

    @property
    def is_approved(self):
        return self.status == 'APPROVED'

    @property
    def is_pending(self):
        return self.status == 'PENDING'

    @property
    def formatted_amount(self):
        return f"${self.amount:,.0f}"


class WompiWebhookEvent(models.Model):
    """Registro de eventos webhook de Wompi"""

    EVENT_CHOICES = [
        ('transaction.updated', 'Transacción actualizada'),
        ('nequi_token.updated', 'Token Nequi actualizado'),
    ]

    # Identificación
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)

    # Datos del evento
    transaction_id = models.CharField(max_length=100, blank=True)
    payload = models.JSONField(help_text="Payload completo del webhook")

    # Procesamiento
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Relacionado con pago (si se encontró)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='webhook_events'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Evento Webhook"
        verbose_name_plural = "Eventos Webhook"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['processed']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.transaction_id} - {'Procesado' if self.processed else 'Pendiente'}"
