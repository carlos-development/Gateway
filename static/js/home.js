// ==========================================
// ANIMACIÓN DE CONTADORES
// ==========================================
const counters = document.querySelectorAll('.metric-item h3[data-target]');

const animateCounter = (counter) => {
    const target = +counter.getAttribute('data-target');
    const duration = 2000; // 2 segundos
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = target / steps;
    let current = 0;

    const updateCounter = () => {
        current += increment;
        if (current < target) {
            if (counter.innerText.includes('%')) {
                counter.innerText = Math.ceil(current) + '%';
            } else if (counter.innerText.includes('+')) {
                counter.innerText = Math.ceil(current) + '+';
            } else {
                counter.innerText = Math.ceil(current);
            }
            setTimeout(updateCounter, stepTime);
        } else {
            if (counter.innerText.includes('%')) {
                counter.innerText = target + '%';
            } else if (counter.innerText.includes('+')) {
                counter.innerText = target + '+';
            } else {
                counter.innerText = target;
            }
        }
    };

    updateCounter();
};

// Observador para iniciar animación cuando sea visible
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            counters.forEach(counter => {
                animateCounter(counter);
            });
            observer.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.5
});

const metricsSection = document.querySelector('.hero-metrics');
if (metricsSection) {
    observer.observe(metricsSection);
}
