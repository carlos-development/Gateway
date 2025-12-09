"""
Admin interface for Payments app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, Payment, WompiWebhookEvent


class OrderItemInline(admin.TabularInline):
    """Inline para items del pedido"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'quantity', 'unit_price', 'total_price', 'product']
    can_delete = False

    def total_price(self, obj):
        return f"${obj.total_price:,.0f}"
    total_price.short_description = 'Total'


class PaymentInline(admin.TabularInline):
    """Inline para pagos del pedido"""
    model = Payment
    extra = 0
    readonly_fields = [
        'wompi_transaction_id', 'wompi_reference', 'payment_method',
        'amount', 'currency', 'status', 'created_at'
    ]
    can_delete = False
    fields = [
        'wompi_transaction_id', 'payment_method', 'amount',
        'status', 'created_at'
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin para pedidos"""
    list_display = [
        'order_number', 'customer_name', 'customer_email',
        'total_amount_display', 'status_badge', 'items_count',
        'created_at', 'paid_at'
    ]
    list_filter = ['status', 'created_at', 'paid_at']
    search_fields = ['order_number', 'customer_email', 'customer_name', 'customer_phone']
    readonly_fields = [
        'id', 'order_number', 'created_at', 'updated_at',
        'total_amount_display', 'shipping_address_display', 'items_count'
    ]
    inlines = [OrderItemInline, PaymentInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    actions = ['mark_as_processing', 'mark_as_cancelled', 'export_to_csv']
    list_per_page = 25

    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id', 'order_number', 'status', 'user', 'items_count')
        }),
        ('Información del Cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Montos', {
            'fields': ('total_amount', 'tax_amount', 'shipping_amount', 'total_amount_display')
        }),
        ('Dirección de Envío', {
            'fields': ('shipping_address', 'shipping_address_display'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
    )

    def items_count(self, obj):
        """Mostrar cantidad de items en el pedido"""
        count = obj.items.count()
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 2px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    items_count.short_description = 'Items'

    def mark_as_processing(self, request, queryset):
        """Marcar pedidos como en procesamiento"""
        updated = queryset.update(status='PROCESSING')
        self.message_user(request, f'{updated} pedido(s) marcado(s) como EN PROCESAMIENTO.')
    mark_as_processing.short_description = 'Marcar como EN PROCESAMIENTO'

    def mark_as_cancelled(self, request, queryset):
        """Cancelar pedidos"""
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f'{updated} pedido(s) cancelado(s).')
    mark_as_cancelled.short_description = 'Cancelar pedidos seleccionados'

    def export_to_csv(self, request, queryset):
        """Exportar pedidos a CSV"""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="pedidos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Número de Orden', 'Cliente', 'Email', 'Teléfono',
            'Total', 'Estado', 'Items', 'Fecha Creación', 'Fecha Pago'
        ])

        for order in queryset:
            writer.writerow([
                order.order_number,
                order.customer_name,
                order.customer_email,
                order.customer_phone,
                f'${order.total_amount:,.0f}',
                order.get_status_display(),
                order.items.count(),
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.paid_at.strftime('%Y-%m-%d %H:%M') if order.paid_at else '-'
            ])

        return response
    export_to_csv.short_description = 'Exportar pedidos a CSV'

    def total_amount_display(self, obj):
        """Mostrar monto total formateado"""
        return f"${obj.total_amount:,.0f} COP"
    total_amount_display.short_description = 'Monto Total'

    def status_badge(self, obj):
        """Mostrar estado con badge de color"""
        colors = {
            'PENDING': '#ffc107',
            'PROCESSING': '#17a2b8',
            'PAID': '#28a745',
            'FAILED': '#dc3545',
            'CANCELLED': '#6c757d',
            'REFUNDED': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'

    def shipping_address_display(self, obj):
        """Mostrar dirección de envío formateada"""
        if not obj.shipping_address:
            return '-'

        address = obj.shipping_address
        html = '<div style="line-height: 1.6;">'

        if address.get('name'):
            html += f"<strong>{address.get('name')}</strong><br>"
        if address.get('address_line_1'):
            html += f"{address.get('address_line_1')}<br>"
        if address.get('address_line_2'):
            html += f"{address.get('address_line_2')}<br>"
        if address.get('city') or address.get('region'):
            html += f"{address.get('city', '')}, {address.get('region', '')}<br>"
        if address.get('country'):
            html += f"{address.get('country')}<br>"
        if address.get('postal_code'):
            html += f"CP: {address.get('postal_code')}<br>"
        if address.get('phone_number'):
            html += f"Tel: {address.get('phone_number')}"

        html += '</div>'
        return mark_safe(html)
    shipping_address_display.short_description = 'Dirección de Envío'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin para pagos"""
    list_display = [
        'wompi_transaction_id', 'order_link', 'payment_method',
        'amount_display', 'status_badge', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'wompi_transaction_id', 'wompi_reference',
        'order__order_number', 'order__customer_email'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'order', 'wompi_transaction_id',
        'wompi_reference', 'payment_method', 'amount', 'currency',
        'wompi_response_display', 'payment_method_data_display'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25

    fieldsets = (
        ('Información del Pago', {
            'fields': ('id', 'order', 'status')
        }),
        ('Wompi', {
            'fields': (
                'wompi_transaction_id', 'wompi_reference',
                'payment_method', 'amount', 'currency'
            )
        }),
        ('Datos del Método de Pago', {
            'fields': ('payment_method_data', 'payment_method_data_display'),
            'classes': ('collapse',)
        }),
        ('Respuesta de Wompi', {
            'fields': ('wompi_response', 'wompi_response_display'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def order_link(self, obj):
        """Link al pedido"""
        url = reverse('admin:payments_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Pedido'

    def amount_display(self, obj):
        """Mostrar monto formateado"""
        return f"${obj.amount:,.0f} {obj.currency}"
    amount_display.short_description = 'Monto'

    def status_badge(self, obj):
        """Mostrar estado con badge de color"""
        colors = {
            'PENDING': '#ffc107',
            'APPROVED': '#28a745',
            'DECLINED': '#dc3545',
            'ERROR': '#dc3545',
            'VOIDED': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'

    def wompi_response_display(self, obj):
        """Mostrar respuesta de Wompi formateada"""
        if not obj.wompi_response:
            return '-'
        import json
        return mark_safe(f'<pre>{json.dumps(obj.wompi_response, indent=2, ensure_ascii=False)}</pre>')
    wompi_response_display.short_description = 'Respuesta de Wompi (JSON)'

    def payment_method_data_display(self, obj):
        """Mostrar datos del método de pago formateados"""
        if not obj.payment_method_data:
            return '-'
        import json
        return mark_safe(f'<pre>{json.dumps(obj.payment_method_data, indent=2, ensure_ascii=False)}</pre>')
    payment_method_data_display.short_description = 'Datos del Método de Pago (JSON)'


@admin.register(WompiWebhookEvent)
class WompiWebhookEventAdmin(admin.ModelAdmin):
    """Admin para eventos webhook de Wompi"""
    list_display = [
        'id', 'event_type', 'transaction_id', 'payment_link',
        'processed_badge', 'created_at'
    ]
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['transaction_id', 'payment__wompi_transaction_id']
    readonly_fields = [
        'id', 'event_type', 'transaction_id', 'payload',
        'processed', 'processed_at', 'error_message',
        'payment', 'created_at', 'payload_display'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50
    actions = ['mark_as_unprocessed', 'reprocess_webhooks']

    fieldsets = (
        ('Información del Evento', {
            'fields': ('id', 'event_type', 'transaction_id', 'payment')
        }),
        ('Estado de Procesamiento', {
            'fields': ('processed', 'processed_at', 'error_message')
        }),
        ('Payload', {
            'fields': ('payload', 'payload_display'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )

    def mark_as_unprocessed(self, request, queryset):
        """Marcar webhooks como no procesados para reprocesar"""
        updated = queryset.update(processed=False, error_message=None)
        self.message_user(request, f'{updated} webhook(s) marcado(s) como NO PROCESADOS.')
    mark_as_unprocessed.short_description = 'Marcar como NO PROCESADO'

    def reprocess_webhooks(self, request, queryset):
        """Reprocesar webhooks seleccionados"""
        from django.utils import timezone

        success_count = 0
        error_count = 0

        for webhook in queryset:
            try:
                # Buscar el pago
                if webhook.payment:
                    payment = webhook.payment
                else:
                    # Intentar encontrar el pago por transaction_id
                    from .models import Payment
                    payment = Payment.objects.get(wompi_transaction_id=webhook.transaction_id)
                    webhook.payment = payment

                # Actualizar estado del pago desde el payload
                transaction_data = webhook.payload.get('data', {}).get('transaction', {})
                status = transaction_data.get('status')

                if status:
                    payment.status = status
                    payment.wompi_response = transaction_data
                    payment.save()

                    # Actualizar orden
                    order = payment.order
                    if status == 'APPROVED':
                        order.status = 'PAID'
                        order.paid_at = timezone.now()
                    elif status in ['DECLINED', 'ERROR']:
                        order.status = 'FAILED'
                    order.save()

                    webhook.processed = True
                    webhook.processed_at = timezone.now()
                    webhook.error_message = None
                    webhook.save()

                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                webhook.error_message = str(e)
                webhook.save()
                error_count += 1

        if success_count > 0:
            self.message_user(request, f'{success_count} webhook(s) reprocesado(s) exitosamente.')
        if error_count > 0:
            self.message_user(request, f'{error_count} webhook(s) fallaron al reprocesar.', level='ERROR')
    reprocess_webhooks.short_description = 'Reprocesar webhooks seleccionados'

    def payment_link(self, obj):
        """Link al pago asociado"""
        if not obj.payment:
            return '-'
        url = reverse('admin:payments_payment_change', args=[obj.payment.id])
        return format_html('<a href="{}">{}</a>', url, obj.payment.wompi_transaction_id)
    payment_link.short_description = 'Pago'

    def processed_badge(self, obj):
        """Mostrar estado procesado con badge"""
        if obj.processed:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold;">✓ Procesado</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-weight: bold;">⏳ Pendiente</span>'
            )
    processed_badge.short_description = 'Procesado'

    def payload_display(self, obj):
        """Mostrar payload formateado"""
        if not obj.payload:
            return '-'
        import json
        return mark_safe(f'<pre>{json.dumps(obj.payload, indent=2, ensure_ascii=False)}</pre>')
    payload_display.short_description = 'Payload (JSON)'
