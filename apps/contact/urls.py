# apps/contact/urls.py
from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_form, name='contact'),  # Cambiado a 'contact' para coincidir con la plantilla
    path('success/', views.contact_success, name='contact_success'),
]
