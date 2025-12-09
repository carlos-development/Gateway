from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# ==========================================
# MODELO DE USUARIO EXTENDIDO
# ==========================================
class User(AbstractUser):
    """
    Modelo de usuario extendido que incluye campos adicionales
    para información personal y preferencias
    """
    DOCUMENT_TYPE_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
        ('PP', 'Pasaporte'),
        ('NIT', 'NIT'),
    ]

    # Información Personal
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número de teléfono debe estar en el formato: '+999999999'. Hasta 15 dígitos permitidos."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPE_CHOICES, blank=True, null=True)
    document_number = models.CharField(max_length=20, blank=True, null=True)

    # Avatar/Foto de perfil
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    # Preferencias
    receive_newsletter = models.BooleanField(default=False)
    receive_promotions = models.BooleanField(default=True)

    # Tipo de cuenta
    is_business = models.BooleanField(default=False, verbose_name='Cuenta Empresarial')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username

    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip()


# ==========================================
# MODELO DE DIRECCIÓN DE ENVÍO
# ==========================================
class ShippingAddress(models.Model):
    """
    Modelo para almacenar direcciones de envío de los usuarios
    Un usuario puede tener múltiples direcciones
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')

    # Información del destinatario
    recipient_name = models.CharField(max_length=100, verbose_name='Nombre del destinatario')
    recipient_phone = models.CharField(max_length=17, verbose_name='Teléfono del destinatario')

    # Dirección
    address_line1 = models.CharField(max_length=255, verbose_name='Dirección línea 1')
    address_line2 = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección línea 2')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    state = models.CharField(max_length=100, verbose_name='Departamento/Estado')
    #? Se comenta el código postal temporalmente
    # postal_code = models.CharField(max_length=10, verbose_name='Código Postal')
    country = models.CharField(max_length=100, default='Colombia', verbose_name='País')

    # Opciones adicionales
    is_default = models.BooleanField(default=False, verbose_name='Dirección predeterminada')
    address_type = models.CharField(
        max_length=10,
        choices=[('home', 'Casa'), ('work', 'Trabajo'), ('other', 'Otro')],
        default='home',
        verbose_name='Tipo de dirección'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dirección de Envío'
        verbose_name_plural = 'Direcciones de Envío'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.recipient_name} - {self.city}, {self.state}"

    def save(self, *args, **kwargs):
        # Si esta dirección se marca como predeterminada,
        # desmarcar las otras direcciones del usuario
        if self.is_default:
            ShippingAddress.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def get_full_address(self):
        """Retorna la dirección completa formateada"""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.append(f"{self.city}, {self.state}")
        parts.append(self.country)
        return ", ".join(parts)


# ==========================================
# MODELO DE INFORMACIÓN EMPRESARIAL
# ==========================================
class BusinessProfile(models.Model):
    """
    Modelo para almacenar información empresarial
    para facturación y datos corporativos
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')

    # Información de la empresa
    company_name = models.CharField(max_length=255, verbose_name='Nombre de la Empresa')
    nit = models.CharField(max_length=20, unique=True, verbose_name='NIT')
    business_type = models.CharField(
        max_length=50,
        choices=[
            ('SA', 'Sociedad Anónima'),
            ('SAS', 'Sociedad por Acciones Simplificada'),
            ('LTDA', 'Sociedad Limitada'),
            ('INDIVIDUAL', 'Persona Natural'),
            ('OTHER', 'Otro'),
        ],
        verbose_name='Tipo de Empresa'
    )

    # Información fiscal
    tax_regime = models.CharField(
        max_length=50,
        choices=[
            ('RESPONSABLE_IVA', 'Responsable de IVA'),
            ('NO_RESPONSABLE_IVA', 'No Responsable de IVA'),
            ('GRAN_CONTRIBUYENTE', 'Gran Contribuyente'),
            ('REGIMEN_SIMPLE', 'Régimen Simple'),
        ],
        verbose_name='Régimen Tributario',
        blank=True,
        null=True
    )

    # Dirección fiscal
    fiscal_address = models.CharField(max_length=255, verbose_name='Dirección Fiscal')
    fiscal_city = models.CharField(max_length=100, verbose_name='Ciudad')
    fiscal_state = models.CharField(max_length=100, verbose_name='Departamento')
    #? Se comenta el código postal temporalmente
    # fiscal_postal_code = models.CharField(max_length=10, verbose_name='Código Postal', blank=True, null=True)

    # Información de contacto empresarial
    business_phone = models.CharField(max_length=17, verbose_name='Teléfono Empresarial')
    business_email = models.EmailField(verbose_name='Email Empresarial')
    website = models.URLField(blank=True, null=True, verbose_name='Sitio Web')

    # Representante legal
    legal_representative = models.CharField(max_length=255, verbose_name='Representante Legal')
    representative_document = models.CharField(max_length=20, verbose_name='Documento del Representante')

    # Documentos (opcional)
    rut_document = models.FileField(upload_to='business_documents/', blank=True, null=True, verbose_name='RUT')
    chamber_commerce = models.FileField(upload_to='business_documents/', blank=True, null=True, verbose_name='Cámara de Comercio')

    # Estado de verificación
    is_verified = models.BooleanField(default=False, verbose_name='Empresa Verificada')
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Verificación')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil Empresarial'
        verbose_name_plural = 'Perfiles Empresariales'

    def __str__(self):
        return f"{self.company_name} - {self.nit}"

    def get_fiscal_address(self):
        """Retorna la dirección fiscal completa"""
        parts = [self.fiscal_address]
        parts.append(f"{self.fiscal_city}, {self.fiscal_state}")
        return ", ".join(parts)


# ==========================================
# MODELO DE HISTORIAL DE INICIO DE SESIÓN
# ==========================================
class LoginHistory(models.Model):
    """
    Modelo para rastrear el historial de inicios de sesión
    útil para seguridad y análisis
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(verbose_name='Dirección IP')
    user_agent = models.TextField(verbose_name='User Agent')
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name='Ubicación')
    success = models.BooleanField(default=True, verbose_name='Inicio Exitoso')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')

    class Meta:
        verbose_name = 'Historial de Inicio de Sesión'
        verbose_name_plural = 'Historial de Inicios de Sesión'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
