# ==========================================
# apps/products/views.py - OPTIMIZADO
# ==========================================

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from decimal import Decimal
from .models import Product, ProductCategory, Cart, CartItem

def product_list(request):
    """
    Lista de productos optimizada con paginación.
    
    Optimizaciones:
    1. select_related('category') - Elimina N+1 queries
    2. Paginación - Limita resultados por página
    3. only() - Carga solo campos necesarios
    """
    # Obtener productos activos con categoría en 1 query
    products = Product.objects.filter(
        active=True
    ).select_related('category').only(
        'id', 'name', 'slug', 'price', 'sale_price',
        'short_description', 'image', 'icon', 'stock',
        'category__name', 'category__icon', 'category__slug'
    ).order_by('-created_at')
    
    # Paginación - 12 productos por página
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Categorías activas
    categories = ProductCategory.objects.filter(
        active=True
    ).only('id', 'name', 'slug', 'icon')
    
    context = {
        'products': page_obj,
        'categories': categories,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Detalle de producto optimizado.
    
    Optimizaciones:
    1. select_related() para categoría
    2. Productos relacionados con límite
    """
    # Obtener producto con categoría en 1 query
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        active=True
    )
    
    # Productos relacionados de la misma categoría
    related_products = Product.objects.filter(
        category=product.category,
        active=True
    ).exclude(
        id=product.id
    ).select_related('category').only(
        'id', 'name', 'slug', 'price', 'image', 'icon',
        'category__name', 'category__icon'
    )[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)


def product_category(request, slug):
    """
    Filtrar productos por categoría - Optimizado.
    """
    # Obtener categoría
    category = get_object_or_404(
        ProductCategory,
        slug=slug,
        active=True
    )
    
    # Productos de esta categoría con select_related
    products = Product.objects.filter(
        category=category,
        active=True
    ).select_related('category').only(
        'id', 'name', 'slug', 'price', 'sale_price',
        'short_description', 'image', 'icon',
        'category__name', 'category__icon'
    )
    
    # Paginación
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Todas las categorías para el menú
    categories = ProductCategory.objects.filter(
        active=True
    ).only('id', 'name', 'slug', 'icon')
    
    context = {
        'category': category,
        'products': page_obj,
        'categories': categories,
        'selected_category': category,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'products/product_list.html', context)


def cart_detail(request):
    """
    Vista del carrito optimizada.
    
    Optimizaciones:
    1. prefetch_related() para items del carrito
    2. select_related() para productos y categorías
    """
    cart = get_cart(request)
    
    if cart:
        # Prefetch items con sus productos y categorías
        cart = Cart.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=CartItem.objects.select_related(
                    'product',
                    'product__category'
                ).only(
                    'id', 'quantity', 'price',
                    'product__id', 'product__name', 'product__image',
                    'product__category__name', 'product__category__icon'
                )
            )
        ).get(id=cart.id)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all() if cart else [],
        'cart_items_count': cart.item_count if cart else 0,
        'cart_subtotal': cart.total if cart else 0,
        'cart_tax': cart.total * Decimal('0.19') if cart else 0,  # IVA 19%
        'cart_total': cart.total * Decimal('1.19') if cart else 0,
    }
    
    return render(request, 'products/cart_detail.html', context)


def get_cart(request):
    """
    Obtiene o crea el carrito del usuario - Optimizado.
    """
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    # Usar get_or_create con prefetch para evitar queries adicionales
    cart, created = Cart.objects.prefetch_related(
        Prefetch(
            'items',
            queryset=CartItem.objects.select_related('product')
        )
    ).get_or_create(session_key=session_key)
    
    return cart


def add_to_cart(request, product_id):
    """
    Añade un producto al carrito o incrementa su cantidad.
    Soporta AJAX para actualización en tiempo real.
    """
    product = get_object_or_404(Product, id=product_id, active=True)
    cart = get_cart(request)

    # Obtener cantidad del request (default: 1)
    quantity = int(request.POST.get('quantity', 1))

    # Usar get_or_create para el item del carrito
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'price': product.sale_price or product.price,
            'quantity': quantity
        }
    )

    # Si no es nuevo, incrementar la cantidad
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Obtener datos del carrito actualizados
        cart_items = cart.items.select_related('product')
        items_data = []

        for item in cart_items:
            items_data.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_image': item.product.primary_image if item.product.primary_image else None,
                'quantity': item.quantity,
                'price': float(item.price),
                'subtotal': float(item.subtotal)
            })

        return JsonResponse({
            'success': True,
            'message': f'{product.name} agregado al carrito',
            'cart': {
                'total_items': cart.total_items,
                'total': float(cart.total),
                'items': items_data
            }
        })

    # Si no es AJAX, redirigir a la página anterior o a productos
    messages.success(request, f'{product.name} agregado al carrito')

    # Obtener la página de referencia (de donde vino el usuario)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('products:product_list')


def remove_from_cart(request, item_id):
    """
    Elimina un item del carrito.
    """
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    
    return redirect('products:cart_view')


def update_cart(request, item_id):
    """
    Actualiza la cantidad de un item en el carrito.
    """
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            # Si la cantidad es 0 o menos, eliminar el item
            cart_item.delete()

    return redirect('products:cart_view')


# ==========================================
# API ENDPOINTS PARA CARRITO (JSON)
# ==========================================

@require_POST
def api_add_to_cart(request, product_id):
    """
    API endpoint para agregar producto al carrito.
    Retorna JSON con el estado del carrito.
    """
    try:
        product = get_object_or_404(Product, id=product_id, active=True)
        cart = get_cart(request)

        # Verificar stock
        if product.stock <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Producto sin stock disponible'
            }, status=400)

        # Obtener o crear el item del carrito
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'price': product.final_price}
        )

        # Si no es nuevo, incrementar la cantidad
        if not created:
            # Verificar que no exceda el stock
            if cart_item.quantity >= product.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Stock máximo alcanzado ({product.stock} unidades)'
                }, status=400)

            cart_item.quantity += 1
            cart_item.save()

        # Retornar datos del carrito actualizados
        return JsonResponse({
            'success': True,
            'message': f'{product.name} agregado al carrito',
            'cart': {
                'item_count': cart.item_count,
                'total': float(cart.total),
                'formatted_total': cart.formatted_total,
            },
            'item': {
                'id': cart_item.id,
                'product_name': product.name,
                'quantity': cart_item.quantity,
                'price': float(cart_item.price),
                'subtotal': float(cart_item.subtotal),
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al agregar producto: {str(e)}'
        }, status=500)


@require_POST
def api_remove_from_cart(request, item_id):
    """
    API endpoint para eliminar item del carrito.
    """
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        product_name = cart_item.product.name
        cart = cart_item.cart
        cart_item.delete()

        return JsonResponse({
            'success': True,
            'message': f'{product_name} eliminado del carrito',
            'cart': {
                'item_count': cart.item_count,
                'total': float(cart.total),
                'formatted_total': cart.formatted_total,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al eliminar producto: {str(e)}'
        }, status=500)


@require_POST
def api_update_cart_item(request, item_id):
    """
    API endpoint para actualizar cantidad de un item.
    """
    try:
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)

        if quantity <= 0:
            # Si la cantidad es 0 o menos, eliminar
            product_name = cart_item.product.name
            cart = cart_item.cart
            cart_item.delete()

            return JsonResponse({
                'success': True,
                'message': f'{product_name} eliminado del carrito',
                'cart': {
                    'item_count': cart.item_count,
                    'total': float(cart.total),
                    'formatted_total': cart.formatted_total,
                }
            })

        # Verificar stock
        if quantity > cart_item.product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Stock máximo: {cart_item.product.stock} unidades'
            }, status=400)

        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({
            'success': True,
            'message': 'Cantidad actualizada',
            'cart': {
                'item_count': cart_item.cart.item_count,
                'total': float(cart_item.cart.total),
                'formatted_total': cart_item.cart.formatted_total,
            },
            'item': {
                'id': cart_item.id,
                'quantity': cart_item.quantity,
                'subtotal': float(cart_item.subtotal),
                'formatted_subtotal': cart_item.formatted_subtotal,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar: {str(e)}'
        }, status=500)


def api_get_cart(request):
    """
    API endpoint para obtener el estado actual del carrito.
    """
    try:
        cart = get_cart(request)

        if not cart or cart.item_count == 0:
            return JsonResponse({
                'success': True,
                'cart': {
                    'item_count': 0,
                    'total': 0,
                    'formatted_total': '$0',
                    'items': []
                }
            })

        # Serializar items del carrito
        items = []
        for item in cart.items.select_related('product').all():
            # Obtener imagen del producto
            product_image = None
            if item.product.primary_image:
                product_image = item.product.primary_image
            elif item.product.image:
                product_image = item.product.image.url

            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_icon': item.product.icon,
                'product_image': product_image,
                'quantity': item.quantity,
                'price': float(item.price),
                'subtotal': float(item.subtotal),
                'formatted_subtotal': item.formatted_subtotal,
            })

        return JsonResponse({
            'success': True,
            'cart': {
                'item_count': cart.item_count,
                'total': float(cart.total),
                'formatted_total': cart.formatted_total,
                'items': items
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener carrito: {str(e)}'
        }, status=500)


# ==========================================
# CHECKOUT
# ==========================================

def checkout_view(request):
    """
    Vista de checkout - Requiere autenticación.
    """
    # Redirigir al nuevo checkout de pagos con Wompi
    return redirect('payments:checkout')