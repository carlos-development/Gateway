from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, ShippingAddress, BusinessProfile, LoginHistory


# ==========================================
# ADMIN DE USUARIO EXTENDIDO
# ==========================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para el modelo de Usuario extendido
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_business', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'is_business', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'document_number']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('phone', 'document_type', 'document_number', 'avatar')
        }),
        ('Preferencias', {
            'fields': ('receive_newsletter', 'receive_promotions', 'is_business')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'date_joined']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


# ==========================================
# ADMIN DE DIRECCIÓN DE ENVÍO
# ==========================================
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    """
    Admin para el modelo de Direcciones de Envío
    """
    list_display = ['recipient_name', 'user', 'city', 'state', 'is_default', 'created_at']
    list_filter = ['is_default', 'address_type', 'country', 'state']
    search_fields = ['recipient_name', 'user__username', 'user__email', 'city', 'address_line1']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información del Destinatario', {
            'fields': ('recipient_name', 'recipient_phone')
        }),
        ('Dirección', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Opciones', {
            'fields': ('is_default', 'address_type')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


# ==========================================
# ADMIN DE PERFIL EMPRESARIAL
# ==========================================
@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    """
    Admin para el modelo de Perfil Empresarial
    """
    list_display = ['company_name', 'nit', 'user', 'business_type', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'business_type', 'tax_regime']
    search_fields = ['company_name', 'nit', 'user__username', 'user__email', 'legal_representative']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de la Empresa', {
            'fields': ('company_name', 'nit', 'business_type', 'tax_regime')
        }),
        ('Dirección Fiscal', {
            'fields': ('fiscal_address', 'fiscal_city', 'fiscal_state', 'fiscal_postal_code')
        }),
        ('Contacto Empresarial', {
            'fields': ('business_phone', 'business_email', 'website')
        }),
        ('Representante Legal', {
            'fields': ('legal_representative', 'representative_document')
        }),
        ('Documentos', {
            'fields': ('rut_document', 'chamber_commerce'),
            'classes': ('collapse',)
        }),
        ('Verificación', {
            'fields': ('is_verified', 'verified_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['verify_business', 'unverify_business']

    def verify_business(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_verified=True, verified_at=timezone.now())
        self.message_user(request, f'{updated} empresas verificadas exitosamente.')
    verify_business.short_description = "Verificar empresas seleccionadas"

    def unverify_business(self, request, queryset):
        updated = queryset.update(is_verified=False, verified_at=None)
        self.message_user(request, f'{updated} empresas marcadas como no verificadas.')
    unverify_business.short_description = "Desverificar empresas seleccionadas"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


# ==========================================
# ADMIN DE HISTORIAL DE INICIO DE SESIÓN
# ==========================================
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """
    Admin para el modelo de Historial de Inicio de Sesión
    """
    list_display = ['user', 'ip_address', 'location', 'success_icon', 'timestamp']
    list_filter = ['success', 'timestamp']
    search_fields = ['user__username', 'user__email', 'ip_address', 'location']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'location', 'success', 'timestamp']
    date_hierarchy = 'timestamp'

    def success_icon(self, obj):
        if obj.success:
            return format_html('<span style="color: green;">✓ Exitoso</span>')
        return format_html('<span style="color: red;">✗ Fallido</span>')
    success_icon.short_description = 'Estado'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
