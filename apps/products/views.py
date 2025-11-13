# apps/products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, ProductCategory, Cart, CartItem

def product_list(request):
    """
    Lista todos los productos activos.
    """
    products = Product.objects.filter(active=True)
    categories = ProductCategory.objects.filter(active=True)
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    """
    Muestra el detalle de un producto.
    """
    product = get_object_or_404(Product, slug=slug, active=True)
    related_products = Product.objects.filter(category=product.category, active=True).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def product_category(request, slug):
    """
    Filtra productos por categoría.
    """
    category = get_object_or_404(ProductCategory, slug=slug, active=True)
    products = Product.objects.filter(category=category, active=True)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/product_list.html', context)

# --- Vistas del Carrito ---

def get_cart(request):
    """
    Obtiene o crea un carrito de compras basado en la sesión.
    """
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id):
    """
    Agrega un producto al carrito.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        
    if request.htmx:
        return render(request, 'partials/cart_icon.html', {'cart': cart})
    
    return redirect('products:cart_detail')

def remove_from_cart(request, item_id):
    """
    Elimina un item del carrito.
    """
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    
    if request.htmx:
        cart = get_cart(request)
        return render(request, 'partials/cart_detail.html', {'cart': cart})
        
    return redirect('products:cart_detail')

def update_cart(request, item_id):
    """
    Actualiza la cantidad de un item en el carrito.
    """
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
        
    if request.htmx:
        cart = get_cart(request)
        return render(request, 'partials/cart_detail.html', {'cart': cart})

    return redirect('products:cart_detail')

def cart_detail(request):
    """
    Muestra el detalle del carrito.
    """
    cart = get_cart(request)
    context = {
        'cart': cart
    }
    return render(request, 'products/cart_detail.html', context)