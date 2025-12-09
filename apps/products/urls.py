# apps/products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.product_category, name='product_category'),

    # Carrito - HTML Views
    path('cart/', views.cart_detail, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),

    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),

    # API Endpoints - JSON
    path('api/cart/', views.api_get_cart, name='api_get_cart'),
    path('api/cart/add/<int:product_id>/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/remove/<int:item_id>/', views.api_remove_from_cart, name='api_remove_from_cart'),
    path('api/cart/update/<int:item_id>/', views.api_update_cart_item, name='api_update_cart_item'),

    # Detalle de producto (debe ir al final para no conflictuar con otras rutas)
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
