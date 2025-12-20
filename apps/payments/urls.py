"""
URLs for payments app
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Checkout - Widget (NUEVO)
    path('checkout-widget/', views.checkout_widget_view, name='checkout_widget'),
    path('create-order-from-widget/', views.create_order_from_widget, name='create_order_from_widget'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),

    # Checkout - Original (mantener para compatibilidad)
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/process/', views.process_payment, name='process_payment'),

    # Payment status
    path('payment/success/<uuid:order_id>/', views.payment_success, name='payment_success'),
    path('payment/pending/<uuid:order_id>/', views.payment_pending, name='payment_pending'),
    path('payment/failed/<uuid:order_id>/', views.payment_failed, name='payment_failed'),

    # Webhooks
    path('webhook/wompi/', views.wompi_webhook, name='wompi_webhook'),

    # Customer order views
    path('mi-cuenta/pedidos/', views.my_orders_view, name='my_orders'),
    path('mi-cuenta/pedidos/<uuid:order_id>/', views.order_detail_view, name='order_detail'),

    # API endpoints para AJAX
    path('api/pse-banks/', views.get_pse_banks, name='get_pse_banks'),
    path('api/tokenize-card/', views.tokenize_card, name='tokenize_card'),
    path('api/tokenize-nequi/', views.tokenize_nequi, name='tokenize_nequi'),
]
