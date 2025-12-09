/* ==========================================
   GATEWAY IT - HOME.JS
   Funcionalidad específica para la página de inicio
   ========================================== */

/**
 * Módulo de la página Home
 */
const GatewayHome = (() => {
    'use strict';

    // ==========================================
    // ANIMACIÓN DE CONTADOR
    // ==========================================

    /**
     * Anima números incrementales en las métricas
     */
    const animateCounters = () => {
        const counters = document.querySelectorAll('.metric-item h3[data-target]');
        const support247 = document.querySelector('.metric-item h3[data-support247]');

        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                    animateCounter(entry.target);
                    entry.target.classList.add('counted');
                }
            });
        }, observerOptions);

        counters.forEach(counter => observer.observe(counter));

        // Observar el 24/7 también
        if (support247) {
            observer.observe(support247);
        }

        /**
         * Anima un contador individual
         * @param {HTMLElement} element - Elemento a animar
         */
        function animateCounter(element) {
            // Caso especial para 24/7
            if (element.hasAttribute('data-support247')) {
                animate247(element);
                return;
            }

            const target = parseInt(element.getAttribute('data-target'));
            const duration = 2000; // 2 segundos
            const start = 0;
            const increment = target / (duration / 16); // 60fps
            let current = start;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    element.textContent = target + (element.textContent.includes('+') ? '+' : '%');
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current) + (element.textContent.includes('+') ? '+' : '%');
                }
            }, 16);
        }

        /**
         * Anima el valor 24/7
         * @param {HTMLElement} element - Elemento a animar
         */
        function animate247(element) {
            const duration = 2000; // 2 segundos total
            const increment24 = 24 / (duration / 16);
            const increment7 = 7 / (duration / 16);
            let current24 = 0;
            let current7 = 0;

            const timer = setInterval(() => {
                current24 += increment24;
                current7 += increment7;

                if (current24 >= 24 && current7 >= 7) {
                    element.textContent = '24/7';
                    clearInterval(timer);
                } else {
                    const val24 = Math.min(Math.floor(current24), 24);
                    const val7 = Math.min(Math.floor(current7), 7);
                    element.textContent = val24 + '/' + val7;
                }
            }, 16);
        }
    };

    // ==========================================
    // PARALLAX SUAVE EN HERO
    // ==========================================

    /**
     * Aplica efecto parallax al hero
     */
    const initParallax = () => {
        const hero = document.querySelector('.hero');
        if (!hero) return;

        const handleParallax = GatewayUtils.throttle(() => {
            const scrolled = window.pageYOffset;
            const parallaxSpeed = 0.5;

            // Solo aplicar si está en viewport
            if (scrolled < window.innerHeight) {
                hero.style.transform = `translateY(${scrolled * parallaxSpeed}px)`;
            }
        }, 10);

        window.addEventListener('scroll', handleParallax, { passive: true });
    };

    // ==========================================
    // PAUSAR/REANUDAR CARRUSEL AL HOVER
    // ==========================================

    /**
     * Pausa el carrusel cuando el usuario hace hover
     */
    const initCarouselControls = () => {
        const carousels = document.querySelectorAll('.logos-track');

        carousels.forEach(carousel => {
            carousel.addEventListener('mouseenter', () => {
                carousel.style.animationPlayState = 'paused';
            });

            carousel.addEventListener('mouseleave', () => {
                carousel.style.animationPlayState = 'running';
            });
        });
    };

    // ==========================================
    // ANIMACIÓN DE ENTRADA PARA CARDS
    // ==========================================

    /**
     * Anima la entrada de las cards de valores
     */
    const animateValueCards = () => {
        const cards = document.querySelectorAll('.value-card');

        const observerOptions = {
            threshold: 0.2,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Agregar delay escalonado
                    setTimeout(() => {
                        entry.target.style.opacity = '0';
                        entry.target.style.transform = 'translateY(30px)';
                        entry.target.style.transition = 'all 0.6s ease';

                        setTimeout(() => {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        }, 50);
                    }, index * 150);

                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        cards.forEach(card => observer.observe(card));
    };

    // ==========================================
    // EFECTO TYPING EN HERO (Opcional)
    // ==========================================

    /**
     * Crea un efecto de escritura en el subtítulo del hero
     */
    const initTypingEffect = () => {
        const subtitle = document.querySelector('.hero p');
        if (!subtitle || subtitle.getAttribute('data-typed')) return;

        const text = subtitle.textContent;
        subtitle.textContent = '';
        subtitle.setAttribute('data-typed', 'true');

        let index = 0;
        const speed = 50; // ms por carácter

        function type() {
            if (index < text.length) {
                subtitle.textContent += text.charAt(index);
                index++;
                setTimeout(type, speed);
            }
        }

        // Esperar un poco antes de empezar
        setTimeout(type, 500);
    };

    // ==========================================
    // SMOOTH REVEAL ON SCROLL
    // ==========================================

    /**
     * Revela secciones suavemente al hacer scroll
     */
    const initSectionReveal = () => {
        const sections = document.querySelectorAll('.about, .clients');

        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '0';
                    entry.target.style.transform = 'translateY(30px)';
                    entry.target.style.transition = 'all 0.8s ease';

                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, 100);

                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        sections.forEach(section => observer.observe(section));
    };

    // ==========================================
    // PRELOAD DE IMÁGENES CRÍTICAS
    // ==========================================

    /**
     * Precarga imágenes importantes para mejor UX
     */
    const preloadCriticalImages = () => {
        const criticalImages = document.querySelectorAll('.hero img, .about img');

        criticalImages.forEach(img => {
            if (img.complete) return;

            const placeholder = document.createElement('div');
            placeholder.style.cssText = `
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: inherit;
            `;

            img.addEventListener('load', () => {
                img.style.opacity = '1';
            });

            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s';
        });
    };

    // ==========================================
    // ESTADÍSTICAS DE PERFORMANCE (Dev)
    // ==========================================

    /**
     * Muestra estadísticas de carga de la página
     */
    const logPerformanceStats = () => {
        if (!window.performance) return;

        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;

                console.log('🏠 Home Page Performance:');
                console.log(`⏱️ Total Load Time: ${pageLoadTime}ms`);

                // Métricas específicas
                const domContentLoaded = perfData.domContentLoadedEventEnd - perfData.navigationStart;
                console.log(`📄 DOM Content Loaded: ${domContentLoaded}ms`);

                // First Paint (si está disponible)
                if (window.performance.getEntriesByType) {
                    const paintMetrics = window.performance.getEntriesByType('paint');
                    paintMetrics.forEach(metric => {
                        console.log(`🎨 ${metric.name}: ${metric.startTime.toFixed(2)}ms`);
                    });
                }
            }, 0);
        });
    };

    // ==========================================
    // INICIALIZACIÓN
    // ==========================================

    /**
     * Inicializa todas las funcionalidades de la página home
     */
    const init = () => {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAll);
        } else {
            initAll();
        }

        function initAll() {
            console.log('🏠 Initializing Home page...');

            // Funcionalidades core
            animateCounters();
            initCarouselControls();
            animateValueCards();
            initSectionReveal();
            preloadCriticalImages();

            // Efectos opcionales (comentar si causan problemas de performance)
            // initParallax();
            // initTypingEffect();

            // Solo en desarrollo
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                logPerformanceStats();
            }

            console.log('✅ Home page initialized');
        }
    };

    // ==========================================
    // API PÚBLICA
    // ==========================================

    return {
        init,
        animateCounters,
        initCarouselControls
    };
})();

// Auto-inicializar
GatewayHome.init();

// Exportar para uso global
window.GatewayHome = GatewayHome;
