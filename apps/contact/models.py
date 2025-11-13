# apps/contact/models.py
from django.db import models

class ContactMessage(models.Model):
    """Mensajes del formulario de contacto"""
    
    STATUS_CHOICES = [
        ('new', 'Nuevo'),
        ('read', 'Leído'),
        ('in_progress', 'En Progreso'),
        ('replied', 'Respondido'),
        ('closed', 'Cerrado'),
    ]
    
    # Información del contacto
    name = models.CharField(max_length=200, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Correo Electrónico")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    message = models.TextField(verbose_name="Mensaje")
    
    # Estado y gestión
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name="Estado"
    )
    notes = models.TextField(
        blank=True, 
        verbose_name="Notas internas",
        help_text="Notas para uso interno del equipo"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de envío")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de respuesta")
    
    # IP del usuario (opcional, para seguridad)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
    
    def __str__(self):
        return f"{self.name} - {self.email} ({self.get_status_display()})"
    
    def mark_as_read(self):
        """Marcar mensaje como leído"""
        if self.status == 'new':
            self.status = 'read'
            self.save()
    
    def mark_as_replied(self):
        """Marcar mensaje como respondido"""
        from django.utils import timezone
        self.status = 'replied'
        self.replied_at = timezone.now()
        self.save()