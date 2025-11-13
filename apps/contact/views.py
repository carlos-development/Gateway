# apps/contact/views.py
from django.shortcuts import render, redirect
from .forms import ContactForm
from .models import ContactMessage

def contact_form(request):
    """
    Renderiza y procesa el formulario de contacto.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Guardar el mensaje
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                message=form.cleaned_data['message'],
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return redirect('contact:contact_success')
    else:
        form = ContactForm()
        
    context = {
        'form': form
    }
    return render(request, 'contact/contact_form.html', context)

def contact_success(request):
    """
    Muestra la página de éxito después de enviar el formulario.
    """
    return render(request, 'contact/contact_success.html')