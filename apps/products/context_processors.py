# apps/products/context_processors.py
from .models import Cart

def cart_context(request):
    """
    Agrega el carrito al contexto de todas las plantillas.
    """
    session_key = request.session.session_key
    if not session_key:
        return {'cart': None}
        
    try:
        cart = Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        cart = None
        
    return {'cart': cart}
