from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone

from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    ShippingAddressForm, BusinessProfileForm
)
from .models import User, ShippingAddress, BusinessProfile, LoginHistory


# ==========================================
# FUNCIÓN AUXILIAR PARA REGISTRAR LOGIN
# ==========================================
def log_login_attempt(request, user, success=True):
    """
    Registra intentos de inicio de sesión en el historial
    """
    # Obtener IP del usuario
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    # Obtener User Agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Crear registro en el historial
    LoginHistory.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success
    )


# ==========================================
# VISTA DE REGISTRO
# ==========================================
@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Vista para registro de nuevos usuarios
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Iniciar sesión automáticamente después del registro
            login(request, user)
            log_login_attempt(request, user, success=True)

            messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.')

            # Si es cuenta empresarial, redirigir a completar perfil
            if user.is_business:
                messages.info(request, 'Por favor completa tu perfil empresarial para acceder a todas las funcionalidades.')
                return redirect('accounts:profile')

            return redirect('core:home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/auth.html', {'form': form, 'is_login': False})


# ==========================================
# VISTA DE INICIO DE SESIÓN
# ==========================================
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista para inicio de sesión de usuarios
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                log_login_attempt(request, user, success=True)

                # Configurar duración de la sesión
                if not remember_me:
                    request.session.set_expiry(0)  # Cerrar al cerrar navegador

                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')

                # Redirigir a la página solicitada o al home
                next_url = request.GET.get('next', 'core:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/auth.html', {'form': form, 'is_login': True})


# ==========================================
# VISTA DE CIERRE DE SESIÓN
# ==========================================
@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('core:home')


# ==========================================
# VISTA DE PERFIL DE USUARIO
# ==========================================
@login_required
def profile_view(request):
    """
    Vista principal del perfil del usuario con tabs
    """
    user = request.user

    # Obtener o crear perfil empresarial si aplica
    business_profile = None
    if user.is_business:
        business_profile = BusinessProfile.objects.filter(user=user).first()

    # Obtener direcciones de envío
    shipping_addresses = ShippingAddress.objects.filter(user=user)

    # Obtener historial de login (últimos 10)
    login_history = LoginHistory.objects.filter(user=user)[:10]

    context = {
        'user': user,
        'business_profile': business_profile,
        'shipping_addresses': shipping_addresses,
        'login_history': login_history,
    }

    return render(request, 'accounts/profile.html', context)


# ==========================================
# VISTA DE ACTUALIZACIÓN DE PERFIL
# ==========================================
@login_required
@require_http_methods(["GET", "POST"])
def profile_update_view(request):
    """
    Vista para actualizar información personal del usuario
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile_update.html', {'form': form})


# ==========================================
# VISTAS DE DIRECCIONES DE ENVÍO
# ==========================================
@login_required
@require_http_methods(["GET", "POST"])
def address_create_view(request):
    """
    Vista para crear una nueva dirección de envío
    """
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Dirección agregada exitosamente.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ShippingAddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'is_create': True})


@login_required
@require_http_methods(["GET", "POST"])
def address_update_view(request, address_id):
    """
    Vista para actualizar una dirección de envío existente
    """
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada exitosamente.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ShippingAddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'is_create': False})


@login_required
@require_http_methods(["POST"])
def address_delete_view(request, address_id):
    """
    Vista para eliminar una dirección de envío
    """
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Dirección eliminada exitosamente.')
    return redirect('accounts:profile')


# ==========================================
# VISTAS DE PERFIL EMPRESARIAL
# ==========================================
@login_required
@require_http_methods(["GET", "POST"])
def business_profile_view(request):
    """
    Vista para crear o actualizar perfil empresarial
    """
    if not request.user.is_business:
        messages.error(request, 'Necesitas una cuenta empresarial para acceder a esta sección.')
        return redirect('accounts:profile')

    # Obtener perfil empresarial si existe
    try:
        business_profile = BusinessProfile.objects.get(user=request.user)
        created = False
    except BusinessProfile.DoesNotExist:
        business_profile = None
        created = True

    if request.method == 'POST':
        if business_profile:
            # Actualizar perfil existente
            form = BusinessProfileForm(request.POST, request.FILES, instance=business_profile)
        else:
            # Crear nuevo perfil
            form = BusinessProfileForm(request.POST, request.FILES)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Perfil empresarial guardado exitosamente.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        if business_profile:
            form = BusinessProfileForm(instance=business_profile)
        else:
            form = BusinessProfileForm()

    return render(request, 'accounts/business_profile.html', {
        'form': form,
        'is_create': created
    })


# ==========================================
# VISTA DE CAMBIO DE CONTRASEÑA
# ==========================================
@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    """
    Vista para cambiar la contraseña del usuario
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener la sesión activa después del cambio de contraseña
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
