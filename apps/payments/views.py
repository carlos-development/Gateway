"""
Views for payment processing
"""
import json
import uuid
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from apps.products.models import Cart, CartItem
from .models import Order, OrderItem, Payment, WompiWebhookEvent
from .services import WompiClient
from .email_utils import send_order_confirmation_email, send_payment_approved_email, send_new_order_admin_email

logger = logging.getLogger(__name__)


# ==========================================
# CHECKOUT VIEW
# ==========================================

@require_http_methods(["GET"])
def checkout_view(request):
    """Vista de checkout con todos los métodos de pago"""
    # Obtener o crear carrito
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    try:
        cart = Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('products:product_list')

    # Verificar que el carrito tenga items
    if cart.item_count == 0:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('products:product_list')

    # Obtener direcciones del usuario si está autenticado
    user_addresses = None
    default_address = None
    if request.user.is_authenticated:
        from apps.accounts.models import ShippingAddress
        user_addresses = ShippingAddress.objects.filter(user=request.user)
        default_address = user_addresses.filter(is_default=True).first()

    # Calcular IVA y total
    tax = cart.total * Decimal('0.19')
    total = cart.total * Decimal('1.19')

    context = {
        'cart': cart,
        'user_addresses': user_addresses,
        'default_address': default_address,
        'tax': tax,
        'total': total,
        'wompi_public_key': settings.WOMPI_PUBLIC_KEY,
        'environment': settings.WOMPI_ENVIRONMENT,
    }

    return render(request, 'payments/checkout.html', context)


@require_http_methods(["GET"])
def checkout_widget_view(request):
    """Vista de checkout usando el Widget de Wompi"""
    # Obtener o crear carrito
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    try:
        cart = Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('products:product_list')

    # Verificar que el carrito tenga items
    if cart.item_count == 0:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('products:product_list')

    # Calcular IVA y total
    tax = cart.total * Decimal('0.19')
    total = cart.total * Decimal('1.19')
    total_in_cents = int(total * 100)  # Wompi necesita centavos

    # URL de redirección después del pago
    redirect_url = request.build_absolute_uri(reverse('payments:payment_callback'))

    # Obtener direcciones guardadas del usuario si está autenticado
    saved_addresses = []
    if request.user.is_authenticated:
        from apps.accounts.models import ShippingAddress
        saved_addresses = ShippingAddress.objects.filter(user=request.user).order_by('-is_default', '-created_at')

    context = {
        'cart': cart,
        'tax': tax,
        'total': total,
        'total_in_cents': total_in_cents,
        'wompi_public_key': settings.WOMPI_PUBLIC_KEY,
        'wompi_integrity_key': settings.WOMPI_INTEGRITY_KEY,
        'redirect_url': redirect_url,
        'environment': settings.WOMPI_ENVIRONMENT,
        'saved_addresses': saved_addresses,
    }

    return render(request, 'payments/checkout_widget.html', context)


# ==========================================
# PROCESS PAYMENT
# ==========================================

@require_POST
def process_payment(request):
    """Procesar el pago según el método seleccionado"""
    try:
        # Obtener datos del formulario
        payment_method = request.POST.get('payment_method')
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone', '')

        # Obtener carrito
        session_key = request.session.session_key
        cart = get_object_or_404(Cart, session_key=session_key)

        if cart.item_count == 0:
            messages.error(request, 'Tu carrito está vacío')
            return redirect('products:product_list')

        # Crear orden (total_amount en pesos, Wompi necesita centavos)
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_name=customer_name,
            total_amount=cart.total,  # En pesos
            status='PENDING'
        )

        # Crear items de la orden
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku if hasattr(cart_item.product, 'sku') else '',
                quantity=cart_item.quantity,
                unit_price=cart_item.price
            )

        # Procesar según el método de pago
        if payment_method == 'CARD':
            return process_card_payment(request, order)
        elif payment_method == 'PSE':
            return process_pse_payment(request, order)
        elif payment_method == 'NEQUI':
            return process_nequi_payment(request, order)
        elif payment_method in ['BANCOLOMBIA', 'BANCOLOMBIA_TRANSFER', 'BANCOLOMBIA_COLLECT', 'BANCOLOMBIA_QR']:
            return process_bancolombia_payment(request, order, payment_method)
        else:
            messages.error(request, 'Método de pago no válido')
            return redirect('payments:checkout')

    except Exception as e:
        logger.error(f"Error procesando pago: {str(e)}", exc_info=True)
        messages.error(request, f'Error procesando el pago: {str(e)}')
        return redirect('payments:checkout')


# ==========================================
# CARD PAYMENT
# ==========================================

def process_card_payment(request, order):
    """Procesar pago con tarjeta de crédito/débito"""
    try:
        card_token = request.POST.get('card_token')
        installments = int(request.POST.get('installments', 1))

        if not card_token:
            messages.error(request, 'Debes tokenizar la tarjeta primero')
            return redirect('payments:checkout')

        # Validar cuotas
        if installments < 1 or installments > 36:
            messages.error(request, 'Número de cuotas inválido (1-36)')
            return redirect('payments:checkout')

        # Crear cliente Wompi
        client = WompiClient()

        # 1. Obtener acceptance token
        logger.info(f"Procesando pago con tarjeta para orden {order.order_number}")
        acceptance_token_data = client.get_acceptance_token()
        if not acceptance_token_data or 'data' not in acceptance_token_data:
            messages.error(request, 'Error al obtener token de aceptación de Wompi')
            return redirect('payments:checkout')

        acceptance_token = acceptance_token_data['data']['presigned_acceptance']['acceptance_token']

        # 2. Construir payment_method usando builder
        payment_method_data = client.build_card_payment_method(card_token, installments)

        # 3. Preparar referencia única
        reference = f"{order.order_number}"

        # 4. Crear transacción en Wompi
        wompi_response = client.create_transaction(
            amount_in_cents=int(order.total_amount * 100),  # Convertir pesos a centavos
            currency='COP',
            customer_email=order.customer_email,
            payment_method=payment_method_data,
            reference=reference,
            acceptance_token=acceptance_token,
            redirect_url=request.build_absolute_uri(reverse('payments:payment_success', args=[order.id]))
        )

        # Guardar el pago
        transaction_data = wompi_response.get('data', {})
        payment = Payment.objects.create(
            order=order,
            wompi_transaction_id=transaction_data.get('id'),
            wompi_reference=reference,
            payment_method='CARD',
            amount=order.total_amount,
            currency='COP',
            status=transaction_data.get('status', 'PENDING'),
            payment_method_data=payment_method_data,
            wompi_response=transaction_data
        )

        # Actualizar estado de la orden
        if payment.status == 'APPROVED':
            order.status = 'PAID'
            order.paid_at = timezone.now()
            order.save()

            # Limpiar carrito
            clear_cart(request)

            return redirect('payments:payment_success', order_id=order.id)
        elif payment.status == 'PENDING':
            order.status = 'PROCESSING'
            order.save()
            return redirect('payments:payment_pending', order_id=order.id)
        else:
            order.status = 'FAILED'
            order.save()
            return redirect('payments:payment_failed', order_id=order.id)

    except Exception as e:
        logger.error(f"Error en pago con tarjeta: {str(e)}", exc_info=True)
        order.status = 'FAILED'
        order.save()
        messages.error(request, f'Error procesando el pago: {str(e)}')
        return redirect('payments:payment_failed', order_id=order.id)


# ==========================================
# PSE PAYMENT
# ==========================================

def process_pse_payment(request, order):
    """Procesar pago con PSE - Débito bancario"""
    try:
        # Datos PSE del formulario
        financial_institution_code = request.POST.get('pse_bank')
        user_type = int(request.POST.get('pse_user_type', 0))  # 0=natural, 1=jurídica
        user_legal_id_type = request.POST.get('pse_document_type', 'CC')
        user_legal_id = request.POST.get('pse_document_number')
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')

        if not all([financial_institution_code, user_legal_id, customer_name]):
            messages.error(request, 'Faltan datos requeridos para PSE')
            return redirect('payments:checkout')

        # Crear cliente Wompi
        client = WompiClient()

        # 1. Obtener acceptance token
        logger.info(f"Procesando pago PSE para orden {order.order_number}")
        acceptance_token_data = client.get_acceptance_token()
        if not acceptance_token_data or 'data' not in acceptance_token_data:
            messages.error(request, 'Error al obtener token de aceptación de Wompi')
            return redirect('payments:checkout')

        acceptance_token = acceptance_token_data['data']['presigned_acceptance']['acceptance_token']

        # 2. Construir payment_method usando builder
        payment_description = f'Pago Orden {order.order_number}'
        payment_method_data = client.build_pse_payment_method(
            financial_institution_code=financial_institution_code,
            user_type=user_type,
            user_legal_id_type=user_legal_id_type,
            user_legal_id=user_legal_id,
            payment_description=payment_description
        )

        # 3. Construir customer_data (obligatorio para PSE)
        phone_with_code = f"57{customer_phone}" if customer_phone and not customer_phone.startswith('57') else customer_phone
        customer_data = client.build_customer_data(
            phone_number=phone_with_code or "573001234567",
            full_name=customer_name
        )

        # 4. Preparar referencia única
        reference = f"{order.order_number}"

        # 5. Crear transacción en Wompi
        wompi_response = client.create_transaction(
            amount_in_cents=int(order.total_amount * 100),  # Convertir pesos a centavos
            currency='COP',
            customer_email=order.customer_email,
            payment_method=payment_method_data,
            reference=reference,
            acceptance_token=acceptance_token,
            redirect_url=request.build_absolute_uri(reverse('payments:payment_success', args=[order.id])),
            customer_data=customer_data  # Requerido para PSE
        )

        # Guardar el pago
        transaction_data = wompi_response.get('data', {})
        payment = Payment.objects.create(
            order=order,
            wompi_transaction_id=transaction_data.get('id'),
            wompi_reference=reference,
            payment_method='PSE',
            amount=order.total_amount,
            currency='COP',
            status=transaction_data.get('status', 'PENDING'),
            payment_method_data=payment_method_data,
            wompi_response=transaction_data
        )

        # PSE siempre redirige al banco
        async_payment_url = transaction_data.get('payment_method', {}).get('async_payment_url')
        if async_payment_url:
            order.status = 'PROCESSING'
            order.save()
            return redirect(async_payment_url)
        else:
            order.status = 'PENDING'
            order.save()
            return redirect('payments:payment_pending', order_id=order.id)

    except Exception as e:
        logger.error(f"Error en pago con PSE: {str(e)}", exc_info=True)
        order.status = 'FAILED'
        order.save()
        messages.error(request, f'Error procesando el pago: {str(e)}')
        return redirect('payments:payment_failed', order_id=order.id)


# ==========================================
# NEQUI PAYMENT
# ==========================================

def process_nequi_payment(request, order):
    """Procesar pago con Nequi - Push notification en app móvil"""
    try:
        nequi_phone = request.POST.get('nequi_phone')

        if not nequi_phone:
            messages.error(request, 'Debes ingresar tu número de Nequi')
            return redirect('payments:checkout')

        # Validar formato de número
        if len(nequi_phone) != 10 or not nequi_phone.isdigit():
            messages.error(request, 'Número de Nequi inválido. Debe tener 10 dígitos.')
            return redirect('payments:checkout')

        # Crear cliente Wompi
        client = WompiClient()

        # 1. Obtener acceptance token
        logger.info(f"Procesando pago Nequi para orden {order.order_number}")
        acceptance_token_data = client.get_acceptance_token()
        if not acceptance_token_data or 'data' not in acceptance_token_data:
            messages.error(request, 'Error al obtener token de aceptación de Wompi')
            return redirect('payments:checkout')

        acceptance_token = acceptance_token_data['data']['presigned_acceptance']['acceptance_token']

        # 2. Construir payment_method usando builder
        payment_method_data = client.build_nequi_payment_method(nequi_phone)

        # 3. Preparar referencia única
        reference = f"{order.order_number}"

        # 4. Crear transacción en Wompi
        wompi_response = client.create_transaction(
            amount_in_cents=int(order.total_amount * 100),  # Convertir pesos a centavos
            currency='COP',
            customer_email=order.customer_email,
            payment_method=payment_method_data,
            reference=reference,
            acceptance_token=acceptance_token,
            redirect_url=request.build_absolute_uri(reverse('payments:payment_success', args=[order.id]))
        )

        # Guardar el pago
        transaction_data = wompi_response.get('data', {})
        payment = Payment.objects.create(
            order=order,
            wompi_transaction_id=transaction_data.get('id'),
            wompi_reference=reference,
            payment_method='NEQUI',
            amount=order.total_amount,
            currency='COP',
            status=transaction_data.get('status', 'PENDING'),
            payment_method_data=payment_method_data,
            wompi_response=transaction_data
        )

        # Nequi siempre es asíncrono (usuario debe aprobar en su app)
        order.status = 'PROCESSING'
        order.save()

        # Limpiar carrito
        clear_cart(request)

        return redirect('payments:payment_pending', order_id=order.id)

    except Exception as e:
        logger.error(f"Error en pago con Nequi: {str(e)}", exc_info=True)
        order.status = 'FAILED'
        order.save()
        messages.error(request, f'Error procesando el pago: {str(e)}')
        return redirect('payments:payment_failed', order_id=order.id)


# ==========================================
# BANCOLOMBIA PAYMENTS
# ==========================================

def process_bancolombia_payment(request, order, payment_type='BANCOLOMBIA_TRANSFER'):
    """Procesar pago con Botón Bancolombia - Transferencia bancaria"""
    try:
        # Crear cliente Wompi
        client = WompiClient()

        # 1. Obtener acceptance token
        logger.info(f"Procesando pago Bancolombia para orden {order.order_number}")
        acceptance_token_data = client.get_acceptance_token()
        if not acceptance_token_data or 'data' not in acceptance_token_data:
            messages.error(request, 'Error al obtener token de aceptación de Wompi')
            return redirect('payments:checkout')

        acceptance_token = acceptance_token_data['data']['presigned_acceptance']['acceptance_token']

        # 2. Construir payment_method usando builder
        payment_description = f'Pago Orden {order.order_number}'
        payment_method_data = client.build_bancolombia_transfer_payment_method(payment_description)

        # 3. Preparar referencia única
        reference = f"{order.order_number}"

        # 4. Crear transacción en Wompi
        wompi_response = client.create_transaction(
            amount_in_cents=int(order.total_amount * 100),  # Convertir pesos a centavos
            currency='COP',
            customer_email=order.customer_email,
            payment_method=payment_method_data,
            reference=reference,
            acceptance_token=acceptance_token,
            redirect_url=request.build_absolute_uri(reverse('payments:payment_success', args=[order.id]))
        )

        # Guardar el pago
        transaction_data = wompi_response.get('data', {})
        payment = Payment.objects.create(
            order=order,
            wompi_transaction_id=transaction_data.get('id'),
            wompi_reference=reference,
            payment_method=payment_type,
            amount=order.total_amount,
            currency='COP',
            status=transaction_data.get('status', 'PENDING'),
            payment_method_data=payment_method_data,
            wompi_response=transaction_data
        )

        order.status = 'PROCESSING'
        order.save()

        # Limpiar carrito
        clear_cart(request)

        # Redirigir según respuesta
        async_payment_url = transaction_data.get('payment_method', {}).get('async_payment_url')
        if async_payment_url:
            return redirect(async_payment_url)
        else:
            return redirect('payments:payment_pending', order_id=order.id)

    except Exception as e:
        logger.error(f"Error en pago con {payment_type}: {str(e)}", exc_info=True)
        order.status = 'FAILED'
        order.save()
        messages.error(request, f'Error procesando el pago: {str(e)}')
        return redirect('payments:payment_failed', order_id=order.id)


# ==========================================
# PAYMENT STATUS VIEWS
# ==========================================

def payment_success(request, order_id):
    """Vista de pago exitoso"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payments/payment_success.html', {'order': order})


def payment_pending(request, order_id):
    """Vista de pago pendiente"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payments/payment_pending.html', {'order': order})


def payment_failed(request, order_id):
    """Vista de pago fallido"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payments/payment_failed.html', {'order': order})


# ==========================================
# WEBHOOK
# ==========================================

@csrf_exempt
@require_POST
def wompi_webhook(request):
    """Recibir notificaciones de Wompi sobre cambios en transacciones"""
    try:
        # Leer el payload
        payload = json.loads(request.body.decode('utf-8'))

        logger.info(f"Webhook recibido de Wompi: {payload}")

        # Extraer datos del evento
        event = payload.get('event')
        data = payload.get('data', {})
        transaction_id = data.get('transaction', {}).get('id')

        # Guardar el evento webhook
        webhook_event = WompiWebhookEvent.objects.create(
            event_type=event,
            transaction_id=transaction_id,
            payload=payload,
            processed=False
        )

        # Procesar el evento
        if event == 'transaction.updated':
            process_transaction_updated(webhook_event, data)
        elif event == 'nequi_token.updated':
            process_nequi_token_updated(webhook_event, data)

        return HttpResponse(status=200)

    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}", exc_info=True)
        return HttpResponse(status=500)


def process_transaction_updated(webhook_event, data):
    """Procesar actualización de transacción"""
    try:
        transaction_data = data.get('transaction', {})
        transaction_id = transaction_data.get('id')
        status = transaction_data.get('status')

        # Buscar el pago
        payment = Payment.objects.filter(wompi_transaction_id=transaction_id).first()

        if payment:
            # Actualizar el pago
            payment.status = status
            payment.wompi_response = transaction_data
            payment.save()

            # Actualizar la orden
            order = payment.order
            if status == 'APPROVED':
                order.status = 'PAID'
                order.paid_at = timezone.now()
            elif status == 'DECLINED' or status == 'ERROR':
                order.status = 'FAILED'
            elif status == 'VOIDED':
                order.status = 'REFUNDED'

            order.save()

            # Marcar webhook como procesado
            webhook_event.payment = payment
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

            logger.info(f"Pago {payment.id} actualizado a {status}")

    except Exception as e:
        logger.error(f"Error procesando transaction.updated: {str(e)}", exc_info=True)
        webhook_event.error_message = str(e)
        webhook_event.save()


def process_nequi_token_updated(webhook_event, data):
    """Procesar actualización de token Nequi"""
    try:
        # Aquí se puede manejar la actualización de tokens Nequi si es necesario
        logger.info(f"Token Nequi actualizado: {data}")

        webhook_event.processed = True
        webhook_event.processed_at = timezone.now()
        webhook_event.save()

    except Exception as e:
        logger.error(f"Error procesando nequi_token.updated: {str(e)}", exc_info=True)
        webhook_event.error_message = str(e)
        webhook_event.save()


# ==========================================
# API ENDPOINTS (AJAX)
# ==========================================

@require_http_methods(["GET"])
def get_pse_banks(request):
    """Obtener lista de bancos PSE"""
    try:
        client = WompiClient()
        banks = client.get_pse_financial_institutions()
        return JsonResponse({'banks': banks})
    except Exception as e:
        logger.error(f"Error obteniendo bancos PSE: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def tokenize_card(request):
    """Tokenizar una tarjeta de crédito"""
    try:
        data = json.loads(request.body.decode('utf-8'))

        # Validar datos requeridos
        required_fields = ['number', 'cvc', 'exp_month', 'exp_year', 'card_holder']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'Campo requerido: {field}'}, status=400)

        client = WompiClient()
        response = client.tokenize_card(
            card_number=data.get('number'),  # Frontend envía 'number'
            cvc=data.get('cvc'),
            exp_month=data.get('exp_month'),
            exp_year=data.get('exp_year'),
            card_holder=data.get('card_holder')
        )

        # Extraer el token de la respuesta
        if response.get('data') and response['data'].get('id'):
            return JsonResponse({
                'success': True,
                'token': response['data']['id'],
                'card_info': {
                    'brand': response['data'].get('brand'),
                    'last_four': response['data'].get('last_four')
                }
            })
        else:
            error_msg = response.get('error', {}).get('reason', 'Error desconocido')
            return JsonResponse({'error': error_msg}, status=400)

    except Exception as e:
        logger.error(f"Error tokenizando tarjeta: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def tokenize_nequi(request):
    """Tokenizar cuenta Nequi"""
    try:
        data = json.loads(request.body.decode('utf-8'))

        client = WompiClient()
        response = client.tokenize_nequi(
            phone_number=data.get('phone_number')
        )

        return JsonResponse(response)

    except Exception as e:
        logger.error(f"Error tokenizando Nequi: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def clear_cart(request):
    """Limpiar el carrito después de un pago exitoso"""
    session_key = request.session.session_key
    if session_key:
        try:
            cart = Cart.objects.get(session_key=session_key)
            cart.items.all().delete()
            cart.delete()
        except Cart.DoesNotExist:
            pass


# ==========================================
# WIDGET CHECKOUT - NEW FLOW
# ==========================================

@require_POST
def create_order_from_widget(request):
    """
    Crear orden después de que el Widget de Wompi procesó el pago

    El Widget ya creó la transacción en Wompi, aquí solo creamos
    la orden en nuestra DB y consultamos el estado final
    """
    try:
        # Obtener datos del formulario
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        transaction_id = request.POST.get('transaction_id')
        reference = request.POST.get('reference')

        # Datos de envío
        shipping_address_line = request.POST.get('shipping_address', '')
        shipping_city = request.POST.get('shipping_city', '')
        shipping_department = request.POST.get('shipping_department', '')
        shipping_notes = request.POST.get('shipping_notes', '')

        # Validar datos requeridos
        if not all([customer_name, customer_email, customer_phone, transaction_id, reference]):
            messages.error(request, 'Datos incompletos del pago')
            return redirect('payments:checkout_widget')

        # Obtener carrito
        session_key = request.session.session_key
        try:
            cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            messages.error(request, 'Carrito no encontrado')
            return redirect('products:product_list')

        # Calcular totales
        tax = cart.total * Decimal('0.19')
        total = cart.total * Decimal('1.19')

        # Preparar datos de dirección de envío
        shipping_address_data = {
            'address': shipping_address_line,
            'city': shipping_city,
            'state': shipping_department,
            'notes': shipping_notes
        }

        # Crear la orden
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            order_number=reference,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            total_amount=total,
            tax_amount=tax,
            shipping_amount=Decimal('0.00'),
            shipping_address=shipping_address_data,
            status='PROCESSING'
        )

        # Crear items de la orden
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.price
            )

        # Consultar estado de la transacción en Wompi (GET sí funciona)
        client = WompiClient()
        try:
            transaction_data = client.get_transaction(transaction_id)
            transaction_info = transaction_data.get('data', {})
            status = transaction_info.get('status', 'PENDING')
            payment_method = transaction_info.get('payment_method_type', 'UNKNOWN')
        except Exception as e:
            logger.error(f"Error consultando transacción {transaction_id}: {e}")
            status = 'PENDING'
            payment_method = 'UNKNOWN'
            transaction_info = {}

        # Crear registro de pago
        payment = Payment.objects.create(
            order=order,
            wompi_transaction_id=transaction_id,
            wompi_reference=reference,
            payment_method=payment_method,
            amount=total,
            currency='COP',
            status=status,
            wompi_response=transaction_info
        )

        # Actualizar estado de la orden según el pago
        if status == 'APPROVED':
            order.status = 'PAID'
            order.paid_at = timezone.now()
            order.save()

            # Limpiar carrito
            cart.items.all().delete()
            cart.delete()

            # Enviar emails
            send_payment_approved_email(order, payment)
            send_new_order_admin_email(order)

            messages.success(request, '¡Pago exitoso! Tu pedido ha sido confirmado.')
            return redirect('payments:payment_success', order_id=order.id)

        elif status == 'PENDING':
            order.status = 'PROCESSING'
            order.save()

            # Enviar email de confirmación de orden
            send_order_confirmation_email(order)
            send_new_order_admin_email(order)

            messages.info(request, 'Tu pago está siendo procesado. Te notificaremos cuando se confirme.')
            return redirect('payments:payment_pending', order_id=order.id)

        else:  # DECLINED, ERROR
            order.status = 'FAILED'
            order.save()
            messages.error(request, 'El pago no pudo ser procesado. Intenta nuevamente.')
            return redirect('payments:payment_failed', order_id=order.id)

    except Exception as e:
        logger.error(f"Error creando orden desde widget: {str(e)}", exc_info=True)
        messages.error(request, 'Error procesando tu pedido. Contacta soporte.')
        return redirect('payments:checkout_widget')


@require_http_methods(["GET"])
def payment_callback(request):
    """
    Callback donde Wompi redirige después del pago

    URL params: ?id=TRANSACTION_ID
    """
    transaction_id = request.GET.get('id')

    if not transaction_id:
        messages.error(request, 'Transacción no encontrada')
        return redirect('products:product_list')

    try:
        # Buscar el pago por transaction_id
        payment = Payment.objects.get(wompi_transaction_id=transaction_id)
        order = payment.order

        # Consultar estado actualizado en Wompi
        client = WompiClient()
        try:
            transaction_data = client.get_transaction(transaction_id)
            transaction_info = transaction_data.get('data', {})
            status = transaction_info.get('status')

            # Actualizar estado del pago
            payment.status = status
            payment.wompi_response = transaction_info
            payment.save()

            # Actualizar estado de la orden
            if status == 'APPROVED':
                order.status = 'PAID'
                order.paid_at = timezone.now()
                order.save()
                return redirect('payments:payment_success', order_id=order.id)

            elif status == 'PENDING':
                order.status = 'PROCESSING'
                order.save()
                return redirect('payments:payment_pending', order_id=order.id)

            else:  # DECLINED, ERROR
                order.status = 'FAILED'
                order.save()
                return redirect('payments:payment_failed', order_id=order.id)

        except Exception as e:
            logger.error(f"Error consultando estado de transacción: {e}")
            # Redirigir a pending si no podemos confirmar
            return redirect('payments:payment_pending', order_id=order.id)

    except Payment.DoesNotExist:
        # Si el pago no existe aún, redirigir a checkout
        messages.warning(request, 'Pago no encontrado. Por favor completa el proceso de checkout.')
        return redirect('payments:checkout_widget')


# ==========================================
# WEBHOOKS DE WOMPI
# ==========================================

@csrf_exempt
@require_POST
def wompi_webhook(request):
    """
    Webhook para recibir notificaciones de Wompi sobre cambios de estado

    Wompi enviará notificaciones cuando:
    - Una transacción cambie de estado (PENDING -> APPROVED/DECLINED)
    - Se complete un pago asíncrono (PSE, Bancolombia, Nequi)

    Documentación: https://docs.wompi.co/docs/colombia/eventos-webhooks/
    """
    try:
        # 1. Leer el body del request
        payload = json.loads(request.body.decode('utf-8'))

        # 2. Validar firma de integridad según documentación de Wompi
        # La firma viene en payload.signature.checksum
        # Se calcula: SHA256(concatenar valores de las properties + timestamp + events_secret)
        if settings.WOMPI_EVENTS_SECRET and 'signature' in payload:
            import hashlib

            signature_data = payload.get('signature', {})
            checksum_received = signature_data.get('checksum', '')
            properties = signature_data.get('properties', [])
            timestamp = payload.get('timestamp', '')

            # Construir string para validar
            # Concatenar valores de las propiedades especificadas
            values_to_concat = []
            transaction_data = payload.get('data', {}).get('transaction', {})

            for prop in properties:
                # Las propiedades vienen como "transaction.id", "transaction.status", etc.
                prop_key = prop.replace('transaction.', '')
                value = transaction_data.get(prop_key, '')
                values_to_concat.append(str(value))

            # Agregar timestamp y secret
            concat_string = ''.join(values_to_concat) + str(timestamp) + settings.WOMPI_EVENTS_SECRET

            # Calcular checksum esperado
            expected_checksum = hashlib.sha256(concat_string.encode('utf-8')).hexdigest()

            # Validar
            if checksum_received != expected_checksum:
                logger.warning(f"Webhook signature mismatch: received={checksum_received}, expected={expected_checksum}, concat_string={concat_string}")
                return JsonResponse({'error': 'Invalid signature'}, status=401)

            logger.info(f"Webhook signature validated successfully")

        # 3. Extraer datos del evento
        event_type = payload.get('event')
        timestamp = payload.get('timestamp')
        data = payload.get('data', {})
        transaction_data = data.get('transaction', {})

        transaction_id = transaction_data.get('id')
        status = transaction_data.get('status')
        reference = transaction_data.get('reference')

        logger.info(f"Webhook recibido: {event_type} | Transaction: {transaction_id} | Status: {status}")

        # 4. Guardar el evento en la base de datos
        webhook_event = WompiWebhookEvent.objects.create(
            event_type=event_type,
            transaction_id=transaction_id,
            payload=payload,
            signature=signature_header,
            processed=False
        )

        # 5. Procesar según el tipo de evento
        if event_type == 'transaction.updated':
            # Buscar el pago por transaction_id o reference
            try:
                payment = Payment.objects.get(wompi_transaction_id=transaction_id)
            except Payment.DoesNotExist:
                # Intentar por referencia
                try:
                    payment = Payment.objects.get(wompi_reference=reference)
                except Payment.DoesNotExist:
                    logger.error(f"Payment no encontrado: transaction_id={transaction_id}, reference={reference}")
                    webhook_event.processed = True
                    webhook_event.error_message = f"Payment no encontrado"
                    webhook_event.save()
                    return JsonResponse({'status': 'payment_not_found'}, status=404)

            # Actualizar estado del pago
            old_status = payment.status
            payment.status = status
            payment.wompi_response = transaction_data
            payment.updated_at = timezone.now()
            payment.save()

            logger.info(f"Payment {payment.id} actualizado: {old_status} -> {status}")

            # Actualizar estado de la orden
            order = payment.order

            if status == 'APPROVED' and old_status != 'APPROVED':
                # Solo actualizar si el estado cambió a APPROVED
                order.status = 'PAID'
                order.paid_at = timezone.now()
                order.save()
                logger.info(f"Orden {order.order_number} marcada como PAID")

                # Enviar email de pago aprobado
                send_payment_approved_email(order, payment)
                logger.info(f"Email de pago aprobado enviado para orden {order.order_number}")

            elif status == 'DECLINED':
                order.status = 'FAILED'
                order.save()
                logger.info(f"Orden {order.order_number} marcada como FAILED")

            elif status == 'ERROR':
                order.status = 'FAILED'
                order.save()
                logger.info(f"Orden {order.order_number} marcada como FAILED (ERROR)")

            # Marcar webhook como procesado
            webhook_event.processed = True
            webhook_event.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Webhook procesado correctamente',
                'payment_id': str(payment.id),
                'order_id': str(order.id),
                'new_status': status
            })

        else:
            # Evento no manejado
            logger.info(f"Evento no manejado: {event_type}")
            webhook_event.processed = True
            webhook_event.error_message = f"Evento no manejado: {event_type}"
            webhook_event.save()
            return JsonResponse({'status': 'event_not_handled', 'event': event_type})

    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando JSON del webhook: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    except Exception as e:
        logger.error(f"Error procesando webhook: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# MIS COMPRAS - CUSTOMER ORDER VIEWS
# ==========================================

@login_required
def my_orders_view(request):
    """Vista de 'Mis Compras' - Listado de pedidos del usuario"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'orders': orders,
    }

    return render(request, 'payments/my_orders.html', context)


@login_required
def order_detail_view(request, order_id):
    """Vista de detalle de un pedido específico"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = order.payment_set.first()

    context = {
        'order': order,
        'payment': payment,
    }

    return render(request, 'payments/order_detail.html', context)
