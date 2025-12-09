# ==========================================
# CONTEXT PROCESSOR OPTIMIZADO
# apps/products/context_processors.py
# ==========================================

from .models import Cart

def cart_context(request):
    """
    Context processor optimizado para el carrito.
    
    Optimizaciones:
    1. Caché del conteo de items
    2. Solo carga el conteo, no todos los items
    """
    session_key = request.session.session_key
    if not session_key:
        return {'cart': None, 'cart_items_count': 0}
    
    try:
        # Solo obtener el conteo, no los items completos
        cart = Cart.objects.only('id').get(session_key=session_key)
        items_count = cart.item_count  # Property que hace la suma
        
        return {
            'cart': cart,
            'cart_items_count': items_count
        }
    except Cart.DoesNotExist:
        return {'cart': None, 'cart_items_count': 0}