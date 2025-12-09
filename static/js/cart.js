/* ==========================================
   GATEWAY IT - CART.JS
   Funcionalidad del carrito de compras
   ========================================== */

const GatewayCart = (() => {
    'use strict';

    // Obtener CSRF token para peticiones POST
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // ==========================================
    // ELEMENTOS DEL DOM
    // ==========================================
    let cartToggle, cartSidebar, cartOverlay, cartClose;
    let cartCount, cartItemsList, cartTotal, cartEmpty;

    /**
     * Inicializar elementos del DOM
     */
    function initElements() {
        cartToggle = document.getElementById('cartToggle');
        cartSidebar = document.getElementById('cartSidebar');
        cartOverlay = document.getElementById('cartOverlay');
        cartClose = document.getElementById('cartClose');
        cartCount = document.getElementById('cartCount');
        cartItemsList = document.getElementById('cartItemsList');
        cartTotal = document.getElementById('cartTotal');
        cartEmpty = document.getElementById('cartEmpty');
    }

    // ==========================================
    // TOGGLE SIDEBAR
    // ==========================================

    /**
     * Abre el sidebar del carrito
     */
    function openCart() {
        if (cartSidebar && cartOverlay) {
            cartSidebar.classList.add('active');
            cartOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';

            // Cargar datos del carrito
            loadCart();
        }
    }

    /**
     * Cierra el sidebar del carrito
     */
    function closeCart() {
        if (cartSidebar && cartOverlay) {
            cartSidebar.classList.remove('active');
            cartOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // ==========================================
    // API CALLS
    // ==========================================

    /**
     * Agregar producto al carrito
     */
    async function addToCart(productId) {
        try {
            const response = await fetch(`/tienda/api/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();

            if (data.success) {
                // Actualizar contador del carrito
                updateCartCount(data.cart.item_count);

                // Mostrar notificación
                if (window.GatewayUtils) {
                    GatewayUtils.showNotification(data.message, 'success');
                }

                // Si el sidebar está abierto, actualizar
                if (cartSidebar && cartSidebar.classList.contains('active')) {
                    loadCart();
                }

                return true;
            } else {
                if (window.GatewayUtils) {
                    GatewayUtils.showNotification(data.message || 'Error al agregar producto', 'error');
                }
                return false;
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            if (window.GatewayUtils) {
                GatewayUtils.showNotification('Error de conexión', 'error');
            }
            return false;
        }
    }

    /**
     * Eliminar item del carrito
     */
    async function removeFromCart(itemId) {
        try {
            const response = await fetch(`/tienda/api/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();

            if (data.success) {
                // Actualizar contador
                updateCartCount(data.cart.item_count);

                // Recargar carrito
                loadCart();

                if (window.GatewayUtils) {
                    GatewayUtils.showNotification(data.message, 'success');
                }

                return true;
            } else {
                if (window.GatewayUtils) {
                    GatewayUtils.showNotification(data.message || 'Error al eliminar', 'error');
                }
                return false;
            }
        } catch (error) {
            console.error('Error removing from cart:', error);
            if (window.GatewayUtils) {
                GatewayUtils.showNotification('Error de conexión', 'error');
            }
            return false;
        }
    }

    /**
     * Actualizar cantidad de un item
     */
    async function updateCartItem(itemId, quantity) {
        try {
            const formData = new FormData();
            formData.append('quantity', quantity);

            const response = await fetch(`/tienda/api/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                // Actualizar contador
                updateCartCount(data.cart.item_count);

                // Recargar carrito
                loadCart();

                return true;
            } else {
                if (window.GatewayUtils) {
                    GatewayUtils.showNotification(data.message || 'Error al actualizar', 'error');
                }
                return false;
            }
        } catch (error) {
            console.error('Error updating cart:', error);
            if (window.GatewayUtils) {
                GatewayUtils.showNotification('Error de conexión', 'error');
            }
            return false;
        }
    }

    /**
     * Cargar datos del carrito
     */
    async function loadCart() {
        try {
            const response = await fetch('/tienda/api/cart/');
            const data = await response.json();

            if (data.success) {
                // Siempre actualizar el contador, incluso si el sidebar está cerrado
                updateCartCount(data.cart.item_count);

                // Actualizar UI completa solo si el sidebar está abierto
                if (cartSidebar && cartSidebar.classList.contains('active')) {
                    updateCartUI(data.cart);
                }
            }
        } catch (error) {
            console.error('Error loading cart:', error);
        }
    }

    // ==========================================
    // UI UPDATES
    // ==========================================

    /**
     * Actualizar contador del carrito
     */
    function updateCartCount(count) {
        if (cartCount) {
            const oldCount = parseInt(cartCount.textContent) || 0;
            cartCount.textContent = count;
            cartCount.style.display = count > 0 ? 'flex' : 'none';

            // Animación solo si el contador aumentó
            if (count > oldCount) {
                cartCount.style.animation = 'none';
                setTimeout(() => {
                    cartCount.style.animation = 'cartBounce 0.5s ease';
                }, 10);
            }
        }
    }

    /**
     * Actualizar UI del carrito
     */
    function updateCartUI(cart) {
        if (!cartItemsList || !cartTotal || !cartEmpty) return;

        // Actualizar contador
        updateCartCount(cart.item_count);

        // Si el carrito está vacío
        if (cart.item_count === 0) {
            cartItemsList.style.display = 'none';
            cartEmpty.style.display = 'block';
            cartTotal.textContent = '$0';
            return;
        }

        // Mostrar items
        cartItemsList.style.display = 'block';
        cartEmpty.style.display = 'none';

        // Renderizar items
        cartItemsList.innerHTML = cart.items.map(item => `
            <div class="cart-item" data-item-id="${item.id}">
                <div class="cart-item-image">
                    ${item.product_image
                        ? `<img src="${item.product_image}" alt="${item.product_name}" loading="lazy">`
                        : `<i class="${item.product_icon}"></i>`
                    }
                </div>
                <div class="cart-item-details">
                    <h4>${item.product_name}</h4>
                    <p class="cart-item-price">$${item.price.toLocaleString('es-CO')}</p>
                </div>
                <div class="cart-item-quantity">
                    <button class="qty-btn" onclick="GatewayCart.decrementItem(${item.id}, ${item.quantity})">
                        <i class="fas fa-minus"></i>
                    </button>
                    <span>${item.quantity}</span>
                    <button class="qty-btn" onclick="GatewayCart.incrementItem(${item.id}, ${item.quantity})">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
                <button class="cart-item-remove" onclick="GatewayCart.removeItem(${item.id})" aria-label="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');

        // Actualizar total
        cartTotal.textContent = cart.formatted_total;
    }

    /**
     * Incrementar cantidad de un item
     */
    function incrementItem(itemId, currentQty) {
        updateCartItem(itemId, currentQty + 1);
    }

    /**
     * Decrementar cantidad de un item
     */
    function decrementItem(itemId, currentQty) {
        if (currentQty > 1) {
            updateCartItem(itemId, currentQty - 1);
        } else {
            removeFromCart(itemId);
        }
    }

    /**
     * Eliminar item (wrapper para llamar desde HTML)
     */
    function removeItem(itemId) {
        removeFromCart(itemId);
    }

    // ==========================================
    // INICIALIZACIÓN
    // ==========================================

    /**
     * Inicializar el módulo del carrito
     */
    function init() {
        initElements();

        if (!cartToggle || !cartSidebar) {
            console.warn('Cart elements not found');
            return;
        }

        // Event listeners
        cartToggle.addEventListener('click', openCart);

        if (cartClose) {
            cartClose.addEventListener('click', closeCart);
        }

        if (cartOverlay) {
            cartOverlay.addEventListener('click', closeCart);
        }

        // Cargar contador inicial
        loadCart();

        // Delegación de eventos para botones "Agregar al carrito"
        document.addEventListener('click', (e) => {
            const addBtn = e.target.closest('.add-to-cart-btn, .add-to-cart');
            if (addBtn) {
                e.preventDefault();
                const productId = addBtn.dataset.productId;
                if (productId) {
                    addToCart(productId);
                }
            }
        });

        console.log('✅ Cart module initialized');
    }

    // ==========================================
    // API PÚBLICA
    // ==========================================

    return {
        init,
        openCart,
        closeCart,
        addToCart,
        removeItem,
        incrementItem,
        decrementItem,
        loadCart,
    };
})();

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', GatewayCart.init);
} else {
    GatewayCart.init();
}

// Exportar para uso global
window.GatewayCart = GatewayCart;
