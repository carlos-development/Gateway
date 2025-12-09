from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User, ShippingAddress, BusinessProfile


# ==========================================
# FORMULARIO DE REGISTRO DE USUARIO
# ==========================================
class UserRegistrationForm(UserCreationForm):
    """
    Formulario para registro de nuevos usuarios
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Apellido'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+57 300 123 4567'
        })
    )
    is_business = forms.BooleanField(
        required=False,
        label='¿Cuenta empresarial?',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )
    receive_promotions = forms.BooleanField(
        required=False,
        initial=True,
        label='Recibir promociones y ofertas',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone',
                  'password1', 'password2', 'is_business', 'receive_promotions']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de usuario'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirmar contraseña'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email


# ==========================================
# FORMULARIO DE INICIO DE SESIÓN
# ==========================================
class UserLoginForm(AuthenticationForm):
    """
    Formulario para inicio de sesión de usuarios
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Usuario o correo electrónico',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        })
    )


# ==========================================
# FORMULARIO DE PERFIL DE USUARIO
# ==========================================
class UserProfileForm(forms.ModelForm):
    """
    Formulario para actualizar información del perfil de usuario
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'document_type',
                  'document_number', 'receive_newsletter', 'receive_promotions']  # 'avatar' comentado temporalmente
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+57 300 123 4567'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Número de documento'}),
            'receive_newsletter': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'receive_promotions': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise ValidationError('Este correo electrónico ya está en uso.')
        return email


# ==========================================
# FORMULARIO DE DIRECCIÓN DE ENVÍO
# ==========================================
class ShippingAddressForm(forms.ModelForm):
    """
    Formulario para crear o actualizar direcciones de envío
    """
    class Meta:
        model = ShippingAddress
        fields = ['recipient_name', 'recipient_phone', 'address_line1', 'address_line2',
                  'city', 'state', 'country', 'address_type', 'is_default']
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre completo del destinatario'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+57 300 123 4567'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Calle, número, barrio'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Apartamento, suite, unidad (opcional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ciudad'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Departamento'
            }),
            #? Se comenta el código postal temporalmente
            # 'postal_code': forms.TextInput(attrs={
            #     'class': 'form-input',
            #     'placeholder': 'Código postal'
            # }),
            'country': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'País'
            }),
            'address_type': forms.Select(attrs={'class': 'form-select'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


# ==========================================
# FORMULARIO DE PERFIL EMPRESARIAL
# ==========================================
class BusinessProfileForm(forms.ModelForm):
    """
    Formulario para crear o actualizar perfil empresarial
    """
    class Meta:
        model = BusinessProfile
        fields = [
            'company_name', 'nit', 'business_type', 'tax_regime',
            'fiscal_address', 'fiscal_city', 'fiscal_state',
            'business_phone', 'business_email', 'website',
            'legal_representative', 'representative_document',
            'rut_document', 'chamber_commerce'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Razón Social'
            }),
            'nit': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '123456789-0'
            }),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'tax_regime': forms.Select(attrs={'class': 'form-select'}),
            'fiscal_address': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Dirección fiscal de la empresa'
            }),
            'fiscal_city': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ciudad'
            }),
            'fiscal_state': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Departamento'
            }),
            #? Se comenta el código postal temporalmente
            # 'fiscal_postal_code': forms.TextInput(attrs={
            #     'class': 'form-input',
            #     'placeholder': 'Código postal'
            # }),
            'business_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+57 1 234 5678'
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'contacto@empresa.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://www.empresa.com'
            }),
            'legal_representative': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del representante legal'
            }),
            'representative_document': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Cédula del representante'
            }),
            'rut_document': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': '.pdf'
            }),
            'chamber_commerce': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': '.pdf'
            }),
        }

    def clean_nit(self):
        nit = self.cleaned_data.get('nit')
        # Si es actualización, excluir el perfil actual
        if self.instance.pk:
            if BusinessProfile.objects.filter(nit=nit).exclude(pk=self.instance.pk).exists():
                raise ValidationError('Este NIT ya está registrado.')
        else:
            if BusinessProfile.objects.filter(nit=nit).exists():
                raise ValidationError('Este NIT ya está registrado.')
        return nit
