/* ==========================================
   GATEWAY IT - UTILS.JS
   Funciones utilitarias reutilizables
   ========================================== */

/**
 * Módulo de Utilidades
 * Contiene funciones helper usadas en toda la aplicación
 */
const GatewayUtils = (() => {
    'use strict';

    // ==========================================
    // NOTIFICACIONES
    // ==========================================
    
    /**
     * Muestra una notificación toast
     * @param {string} message - Mensaje a mostrar
     * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duración en ms (default: 3000)
     */
    const showNotification = (message, type = 'success', duration = 3000) => {
        // Prevenir múltiples notificaciones
        const existingNotification = document.querySelector('.gateway-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const colors = {
            success: 'var(--gradient-primary)',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };

        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };

        const notification = document.createElement('div');
        notification.className = 'gateway-notification';
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${colors[type] || colors.success};
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            z-index: 10001;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
            word-wrap: break-word;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${icons[type] || icons.success}" style="font-size: 1.2rem;"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    };

    // ==========================================
    // SMOOTH SCROLL
    // ==========================================
    
    /**
     * Scroll suave a un elemento
     * @param {string} target - Selector del elemento
     * @param {number} offset - Offset del scroll (default: 80)
     */
    const smoothScrollTo = (target, offset = 80) => {
        const element = document.querySelector(target);
        if (!element) return;

        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    };

    /**
     * Inicializa smooth scroll para todos los links con hash
     */
    const initSmoothScroll = () => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '') return;
                
                e.preventDefault();
                smoothScrollTo(href);
                
                // Cerrar menú móvil si está abierto
                const navLinks = document.getElementById('navLinks');
                if (navLinks && navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                }
            });
        });
    };

    // ==========================================
    // LAZY LOADING DE IMÁGENES
    // ==========================================
    
    /**
     * Inicializa lazy loading para imágenes
     */
    const initLazyLoading = () => {
        // Verificar si el navegador soporta lazy loading nativo
        if ('loading' in HTMLImageElement.prototype) {
            // Agregar atributo loading="lazy" a todas las imágenes
            document.querySelectorAll('img:not([loading])').forEach(img => {
                img.loading = 'lazy';
            });
        } else {
            // Fallback para navegadores sin soporte
            const images = document.querySelectorAll('img[data-src]');
            
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        }
    };

    // ==========================================
    // ANIMACIONES DE SCROLL REVEAL
    // ==========================================
    
    /**
     * Revela elementos al hacer scroll
     */
    const revealOnScroll = () => {
        const reveals = document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right');
        
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        reveals.forEach(element => revealObserver.observe(element));
    };

    // ==========================================
    // DEBOUNCE UTILITY
    // ==========================================
    
    /**
     * Debounce function para optimizar eventos
     * @param {Function} func - Función a ejecutar
     * @param {number} wait - Tiempo de espera en ms
     */
    const debounce = (func, wait = 300) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    // ==========================================
    // THROTTLE UTILITY
    // ==========================================
    
    /**
     * Throttle function para limitar ejecuciones
     * @param {Function} func - Función a ejecutar
     * @param {number} limit - Límite de tiempo en ms
     */
    const throttle = (func, limit = 300) => {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    };

    // ==========================================
    // FORMATEO DE PRECIOS
    // ==========================================
    
    /**
     * Formatea un número como precio en COP
     * @param {number} price - Precio a formatear
     */
    const formatPrice = (price) => {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0
        }).format(price);
    };

    // ==========================================
    // DETECCIÓN DE DISPOSITIVO MÓVIL
    // ==========================================
    
    /**
     * Detecta si el dispositivo es móvil
     */
    const isMobile = () => {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    };

    // ==========================================
    // LOCAL STORAGE CON MANEJO DE ERRORES
    // ==========================================
    
    /**
     * Guarda datos en localStorage con manejo de errores
     * @param {string} key - Clave
     * @param {any} value - Valor a guardar
     */
    const saveToStorage = (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Error saving to localStorage:', e);
            return false;
        }
    };

    /**
     * Obtiene datos de localStorage con manejo de errores
     * @param {string} key - Clave
     * @param {any} defaultValue - Valor por defecto si no existe
     */
    const getFromStorage = (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    };

    // ==========================================
    // INICIALIZACIÓN
    // ==========================================
    
    /**
     * Inicializa todas las utilidades
     */
    const init = () => {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                initSmoothScroll();
                initLazyLoading();
                revealOnScroll();
            });
        } else {
            initSmoothScroll();
            initLazyLoading();
            revealOnScroll();
        }
    };

    // ==========================================
    // API PÚBLICA
    // ==========================================
    
    return {
        showNotification,
        smoothScrollTo,
        initSmoothScroll,
        initLazyLoading,
        revealOnScroll,
        debounce,
        throttle,
        formatPrice,
        isMobile,
        saveToStorage,
        getFromStorage,
        init
    };
})();

// Auto-inicializar
GatewayUtils.init();

// Exportar para uso global
window.GatewayUtils = GatewayUtils;
