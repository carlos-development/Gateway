# ==========================================
# apps/contact/views.py - OPTIMIZADO
# ==========================================

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from email.mime.image import MIMEImage
import os
from .forms import ContactForm
from .models import ContactMessage

@require_http_methods(["GET", "POST"])
def contact_form(request):
    """
    Formulario de contacto con validación optimizada.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Crear mensaje de contacto
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                message=form.cleaned_data['message'],
                ip_address=get_client_ip(request)
            )

            # Enviar email al gerente con estilos
            send_contact_email_to_manager(contact_message)

            # Enviar email de confirmación al cliente
            send_confirmation_email_to_client(contact_message)

            messages.success(
                request,
                '¡Mensaje enviado con éxito! Te contactaremos pronto.'
            )
            return redirect('contact:contact_success')
        else:
            messages.error(
                request,
                'Por favor corrige los errores en el formulario.'
            )
    else:
        form = ContactForm()

    context = {
        'form': form
    }
    return render(request, 'contact/contact_form.html', context)


def get_client_ip(request):
    """
    Obtiene la IP del cliente de forma segura.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def contact_success(request):
    """
    Página de éxito después de enviar el formulario.
    """
    return render(request, 'contact/contact_success.html')


def send_contact_email_to_manager(contact_message):
    """
    Envía email con estilos al gerente cuando un cliente envía mensaje de contacto.
    """
    subject = f'Nuevo mensaje de contacto - {contact_message.name}'

    # Renderizar template HTML
    html_content = render_to_string('contact/emails/contact_manager.html', {
        'contact': contact_message
    })

    # Texto plano como fallback
    text_content = f"""
    Nuevo mensaje de contacto recibido:

    Nombre: {contact_message.name}
    Email: {contact_message.email}
    Teléfono: {contact_message.phone}

    Mensaje:
    {contact_message.message}

    Fecha: {contact_message.created_at.strftime('%d/%m/%Y %H:%M')}
    """

    # Crear email con HTML
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.EMAIL_HOST_USER]  # Email del gerente
    )
    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
    except Exception as e:
        print(f"Error sending email to manager: {e}")


def send_confirmation_email_to_client(contact_message):
    """
    Envía email de confirmación con estilos al cliente.
    """
    subject = '¡Gracias por contactarnos! - Gateway IT'

    # Renderizar template HTML
    html_content = render_to_string('contact/emails/contact_confirmation.html', {
        'contact': contact_message
    })

    # Texto plano como fallback
    text_content = f"""
    Hola {contact_message.name},

    Gracias por contactarnos. Hemos recibido tu mensaje correctamente.

    Nuestro equipo lo revisará y te responderemos a la brevedad posible.

    Saludos,
    El equipo de Gateway IT
    """

    # Crear email con HTML
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[contact_message.email]
    )
    email.attach_alternative(html_content, "text/html")

    # Adjuntar logo como imagen embebida
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'Logo_Gateway.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as img:
            logo_img = MIMEImage(img.read())
            logo_img.add_header('Content-ID', '<logo>')
            logo_img.add_header('Content-Disposition', 'inline', filename='logo.png')
            email.attach(logo_img)

    # Adjuntar logo de WhatsApp
    whatsapp_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'whatsapp.png')
    if os.path.exists(whatsapp_path):
        with open(whatsapp_path, 'rb') as img:
            whatsapp_img = MIMEImage(img.read())
            whatsapp_img.add_header('Content-ID', '<whatsapp>')
            whatsapp_img.add_header('Content-Disposition', 'inline', filename='whatsapp.png')
            email.attach(whatsapp_img)

    # Adjuntar logo de Facebook
    facebook_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'facebook.png')
    if os.path.exists(facebook_path):
        with open(facebook_path, 'rb') as img:
            facebook_img = MIMEImage(img.read())
            facebook_img.add_header('Content-ID', '<facebook>')
            facebook_img.add_header('Content-Disposition', 'inline', filename='facebook.png')
            email.attach(facebook_img)

    try:
        email.send()
    except Exception as e:
        print(f"Error sending confirmation email to client: {e}")
