# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('tienda/', include('apps.products.urls')),
    path('services/', include('apps.services.urls')),
    path('contact/', include('apps.contact.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('payments/', include('apps.payments.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)