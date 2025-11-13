# apps/core/models.py
from django.db import models

class CompanyInfo(models.Model):
    """Información general de la empresa (singleton)"""
    name = models.CharField(max_length=200, default="Gateway IT")
    slogan = models.CharField(max_length=200, default="Soluciones Tecnológicas Eficientes")
    description = models.TextField()
    
    # Contacto
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=300)
    
    # Redes sociales
    facebook_url = models.URLField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Horarios
    business_hours = models.CharField(max_length=200, default="Lunes a Viernes: 8:00 AM - 6:00 PM")
    
    # Métricas del hero
    years_experience = models.IntegerField(default=15)
    security_percentage = models.IntegerField(default=100)
    support_availability = models.CharField(max_length=10, default="24/7")
    
    class Meta:
        verbose_name = "Información de la Empresa"
        verbose_name_plural = "Información de la Empresa"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Asegurar que solo existe una instancia (singleton)
        if not self.pk and CompanyInfo.objects.exists():
            return CompanyInfo.objects.first()
        return super().save(*args, **kwargs)


class ValueCard(models.Model):
    """Valores de la empresa (Seguridad, Garantía, Innovación)"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Clase de Font Awesome, ej: fas fa-shield-alt")
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Valor de la Empresa"
        verbose_name_plural = "Valores de la Empresa"
    
    def __str__(self):
        return self.title


class Client(models.Model):
    """Clientes de la empresa"""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='clients/')
    website = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    """Marcas con las que trabajan"""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='brands/')
    website = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
    
    def __str__(self):
        return self.name