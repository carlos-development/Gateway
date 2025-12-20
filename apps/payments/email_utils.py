"""
Utilidades para envío de emails relacionados con órdenes y pagos
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_confirmation_email(order):
    """
    Enviar email de confirmación de orden al cliente
    """
    try:
        subject = f'Confirmación de pedido #{order.order_number} - Gateway IT'

        # Renderizar template HTML
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
        })

        # Crear email
        email = EmailMultiAlternatives(
            subject=subject,
            body='',  # Texto plano vacío, usaremos solo HTML
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer_email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email de confirmación enviado a {order.customer_email} para orden {order.order_number}")
        return True

    except Exception as e:
        logger.error(f"Error enviando email de confirmación para orden {order.order_number}: {str(e)}", exc_info=True)
        return False


def send_payment_approved_email(order, payment=None):
    """
    Enviar email cuando el pago es aprobado
    """
    try:
        subject = f'Pago confirmado - Pedido #{order.order_number} - Gateway IT'

        # Renderizar template HTML
        html_content = render_to_string('emails/payment_approved.html', {
            'order': order,
            'payment': payment,
        })

        # Crear email
        email = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer_email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email de pago aprobado enviado a {order.customer_email} para orden {order.order_number}")
        return True

    except Exception as e:
        logger.error(f"Error enviando email de pago aprobado para orden {order.order_number}: {str(e)}", exc_info=True)
        return False


def send_new_order_admin_email(order):
    """
    Enviar email de notificación de nueva orden al admin
    """
    try:
        # Email de admin desde settings
        admin_email = getattr(settings, 'ADMIN_ORDER_EMAIL', 'info@gatewayit.com.co')

        subject = f'Nuevo pedido #{order.order_number} - Gateway IT'

        # Renderizar template HTML
        html_content = render_to_string('emails/new_order_admin.html', {
            'order': order,
        })

        # Crear email
        email = EmailMultiAlternatives(
            subject=subject,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email de nueva orden enviado al admin para orden {order.order_number}")
        return True

    except Exception as e:
        logger.error(f"Error enviando email al admin para orden {order.order_number}: {str(e)}", exc_info=True)
        return False