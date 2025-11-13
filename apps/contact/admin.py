# apps/contact/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin para mensajes de contacto"""
    list_display = ['name', 'email', 'phone', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at', 'updated_at', 'replied_at', 'ip_address']
    
    fieldsets = (
        ('Información del Contacto', {
            'fields': ('name', 'email', 'phone', 'message')
        }),
        ('Gestión', {
            'fields': ('status', 'notes')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at', 'replied_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_closed']
    
    def status_badge(self, obj):
        """Mostrar badge colorido según el estado"""
        colors = {
            'new': '#dc3545',
            'read': '#ffc107',
            'in_progress': '#17a2b8',
            'replied': '#28a745',
            'closed': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def mark_as_read(self, request, queryset):
        queryset.filter(status='new').update(status='read')
    mark_as_read.short_description = "Marcar como leído"
    
    def mark_as_replied(self, request, queryset):
        for message in queryset:
            message.mark_as_replied()
    mark_as_replied.short_description = "Marcar como respondido"
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_as_closed.short_description = "Marcar como cerrado"