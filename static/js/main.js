/* ==========================================
   GATEWAY IT - MAIN.JS
   Funcionalidad principal del sitio
   ========================================== */

/**
 * Módulo Principal de Gateway IT
 */
const GatewayMain = (() => {
    'use strict';

    // ==========================================
    // NAVEGACIÓN
    // ==========================================
    
    /**
     * Inicializa el menú de navegación
     */
    const initNavigation = () => {
        const menuToggle = document.getElementById('menuToggle');
        const navLinks = document.getElementById('navLinks');
        const navbar = document.getElementById('navbar');

        if (!menuToggle || !navLinks || !navbar) return;

        // Toggle menú móvil
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });

        // Cerrar menú al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!navLinks.contains(e.target) && !menuToggle.contains(e.target)) {
                navLinks.classList.remove('active');
                menuToggle.classList.remove('active');
            }
        });

        // Efecto scroll en navbar (throttled para mejor performance)
        const handleScroll = GatewayUtils.throttle(() => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }, 100);

        window.addEventListener('scroll', handleScroll, { passive: true });

        // User dropdown menu
        const userMenuToggle = document.getElementById('userMenuToggle');
        const userDropdown = document.getElementById('userDropdown');

        if (userMenuToggle && userDropdown) {
            userMenuToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('active');
            });

            // Cerrar dropdown al hacer click fuera
            document.addEventListener('click', (e) => {
                if (!userDropdown.contains(e.target) && !userMenuToggle.contains(e.target)) {
                    userDropdown.classList.remove('active');
                }
            });
        }

        // Scroll suave para enlaces de navegación
        initSmoothScroll();
    };

    /**
     * Inicializa scroll suave para todos los enlaces de ancla
     */
    const initSmoothScroll = () => {
        // Seleccionar todos los enlaces (incluyendo los que tienen URL + ancla)
        const allLinks = document.querySelectorAll('a[href*="#"]');

        allLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');

                // Ignorar enlaces vacíos o solo "#"
                if (!href || href === '#') return;

                // Extraer la parte del ancla
                const hashIndex = href.indexOf('#');
                if (hashIndex === -1) return;

                const targetId = href.substring(hashIndex + 1);
                const urlPart = href.substring(0, hashIndex);

                // Si el enlace es a la misma página o no tiene URL
                const currentPath = window.location.pathname;
                // Normalizar paths removiendo trailing slashes para comparación
                const normalizePath = (path) => path.replace(/\/$/, '') || '/';
                const normalizedCurrent = normalizePath(currentPath);
                const normalizedUrl = normalizePath(urlPart);

                const isSamePage = !urlPart ||
                                  normalizedUrl === normalizedCurrent ||
                                  urlPart === window.location.origin + currentPath ||
                                  normalizedUrl === window.location.origin + normalizedCurrent;

                if (isSamePage) {
                    const targetElement = document.getElementById(targetId);

                    if (targetElement) {
                        e.preventDefault();

                        // Cerrar menú móvil si está abierto
                        const navLinks = document.getElementById('navLinks');
                        const menuToggle = document.getElementById('menuToggle');
                        if (navLinks && menuToggle) {
                            navLinks.classList.remove('active');
                            menuToggle.classList.remove('active');
                        }

                        // Calcular offset del navbar
                        const navbar = document.getElementById('navbar');
                        const navbarHeight = navbar ? navbar.offsetHeight : 80;
                        const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;

                        // Scroll suave
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });

                        // Actualizar URL sin recargar
                        if (window.history && window.history.pushState) {
                            window.history.pushState(null, null, '#' + targetId);
                        }
                    }
                }
            });
        });

        // Manejar scroll al cargar si hay hash en la URL
        if (window.location.hash) {
            setTimeout(() => {
                const targetId = window.location.hash.substring(1);
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    const navbar = document.getElementById('navbar');
                    const navbarHeight = navbar ? navbar.offsetHeight : 80;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }, 100);
        }
    };

    // ==========================================
    // MODO OSCURO
    // ==========================================
    
    /**
     * Inicializa el modo oscuro
     */
    const initDarkMode = () => {
        const toggleButton = document.getElementById('darkModeToggle');
        const icon = document.getElementById('darkModeIcon');

        if (!toggleButton || !icon) return;

        // Cargar preferencia guardada
        const darkMode = GatewayUtils.getFromStorage('darkMode', 'disabled');
        if (darkMode === 'enabled') {
            enableDarkMode();
        }

        // Toggle al hacer click
        toggleButton.addEventListener('click', () => {
            if (document.body.classList.contains('dark-mode')) {
                disableDarkMode();
            } else {
                enableDarkMode();
            }
        });

        /**
         * Activa el modo oscuro
         */
        function enableDarkMode() {
            document.body.classList.add('dark-mode');
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
            GatewayUtils.saveToStorage('darkMode', 'enabled');
        }

        /**
         * Desactiva el modo oscuro
         */
        function disableDarkMode() {
            document.body.classList.remove('dark-mode');
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
            GatewayUtils.saveToStorage('darkMode', 'disabled');
        }
    };

    // ==========================================
    // FORMULARIOS
    // ==========================================
    
    /**
     * Inicializa validación de formularios
     */
    const initFormValidation = () => {
        const forms = document.querySelectorAll('form[data-validate]');

        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                }
            });

            // Validación en tiempo real
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateInput(this);
                });

                input.addEventListener('input', function() {
                    if (this.classList.contains('error')) {
                        validateInput(this);
                    }
                });
            });
        });

        /**
         * Valida un formulario completo
         * @param {HTMLFormElement} form - Formulario a validar
         */
        function validateForm(form) {
            let isValid = true;
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');

            inputs.forEach(input => {
                if (!validateInput(input)) {
                    isValid = false;
                }
            });

            return isValid;
        }

        /**
         * Valida un input individual
         * @param {HTMLInputElement} input - Input a validar
         */
        function validateInput(input) {
            const value = input.value.trim();
            let isValid = true;
            let errorMessage = '';

            // Verificar si es requerido
            if (input.hasAttribute('required') && !value) {
                isValid = false;
                errorMessage = 'Este campo es requerido';
            }

            // Validación de email
            if (input.type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    isValid = false;
                    errorMessage = 'Por favor ingrese un email válido';
                }
            }

            // Validación de teléfono
            if (input.type === 'tel' && value) {
                const phoneRegex = /^[+]?[\d\s\-()]+$/;
                if (!phoneRegex.test(value) || value.length < 7) {
                    isValid = false;
                    errorMessage = 'Por favor ingrese un teléfono válido';
                }
            }

            // Validación de longitud mínima
            if (input.hasAttribute('minlength')) {
                const minLength = parseInt(input.getAttribute('minlength'));
                if (value.length < minLength) {
                    isValid = false;
                    errorMessage = `Mínimo ${minLength} caracteres`;
                }
            }

            // Aplicar clases de error
            if (!isValid) {
                input.classList.add('error');
                showInputError(input, errorMessage);
            } else {
                input.classList.remove('error');
                hideInputError(input);
            }

            return isValid;
        }

        /**
         * Muestra mensaje de error en un input
         * @param {HTMLInputElement} input - Input
         * @param {string} message - Mensaje de error
         */
        function showInputError(input, message) {
            let errorElement = input.parentElement.querySelector('.error-message');
            
            if (!errorElement) {
                errorElement = document.createElement('span');
                errorElement.className = 'error-message';
                errorElement.style.cssText = `
                    color: #dc3545;
                    font-size: 0.85rem;
                    margin-top: 0.3rem;
                    display: block;
                `;
                input.parentElement.appendChild(errorElement);
            }
            
            errorElement.textContent = message;
        }

        /**
         * Oculta mensaje de error de un input
         * @param {HTMLInputElement} input - Input
         */
        function hideInputError(input) {
            const errorElement = input.parentElement.querySelector('.error-message');
            if (errorElement) {
                errorElement.remove();
            }
        }
    };

    // ==========================================
    // ANIMACIONES CSS
    // ==========================================
    
    /**
     * Inyecta animaciones CSS necesarias
     */
    const injectAnimations = () => {
        if (document.getElementById('gateway-animations')) return;

        const style = document.createElement('style');
        style.id = 'gateway-animations';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                    opacity: 0.5;
                }
                50% {
                    transform: scale(1.1);
                    opacity: 0.8;
                }
            }
            
            /* Animación del contador del carrito */
            @keyframes cartBounce {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.2); }
            }
            
            /* Loader genérico */
            .gateway-loader {
                border: 3px solid rgba(245, 134, 53, 0.1);
                border-top: 3px solid var(--primary-color);
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Efecto de hover suave para cards */
            .card-hover-effect {
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card-hover-effect:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(245, 134, 53, 0.15);
            }
        `;
        document.head.appendChild(style);
    };

    // ==========================================
    // PERFORMANCE MONITORING
    // ==========================================
    
    /**
     * Monitorea el performance de la página
     */
    const monitorPerformance = () => {
        if (!window.performance || !console.log) return;

        window.addEventListener('load', () => {
            // Esperar un poco para que todas las métricas estén disponibles
            setTimeout(() => {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                const connectTime = perfData.responseEnd - perfData.requestStart;
                const renderTime = perfData.domComplete - perfData.domLoading;

                console.log('📊 Performance Metrics:');
                console.log(`⏱️ Page Load Time: ${pageLoadTime}ms`);
                console.log(`🔌 Connect Time: ${connectTime}ms`);
                console.log(`🎨 Render Time: ${renderTime}ms`);
            }, 0);
        });
    };

    // ==========================================
    // INICIALIZACIÓN
    // ==========================================
    
    /**
     * Inicializa todo el módulo
     */
    const init = () => {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                initAll();
            });
        } else {
            initAll();
        }

        function initAll() {
            injectAnimations();
            initNavigation();
            initDarkMode();
            initFormValidation();
            monitorPerformance();

            // Log de inicialización
            console.log('✅ Gateway IT initialized successfully');
        }
    };

    // ==========================================
    // API PÚBLICA
    // ==========================================
    
    return {
        init,
        initNavigation,
        initDarkMode,
        initFormValidation
    };
})();

// Auto-inicializar
GatewayMain.init();

// Exportar para uso global
window.GatewayMain = GatewayMain;
