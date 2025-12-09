/**
 * CHECKOUT PAGE - GATEWAY IT
 * Optimized JavaScript for payment checkout
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('checkoutForm');
    const submitBtn = document.getElementById('submitBtn');
    const paymentMethods = document.querySelectorAll('.payment-method');
    const paymentForms = document.querySelectorAll('.payment-form');

    // ==========================================
    // PAYMENT METHOD SWITCHING
    // ==========================================
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            const methodType = this.dataset.method;

            // Update active states
            paymentMethods.forEach(m => m.classList.remove('active'));
            this.classList.add('active');

            // Show corresponding form
            paymentForms.forEach(f => f.classList.remove('active'));
            document.getElementById(methodType + 'Form').classList.add('active');

            // Clear required attributes from hidden forms
            paymentForms.forEach(formDiv => {
                const inputs = formDiv.querySelectorAll('input, select');
                inputs.forEach(input => {
                    if (formDiv.classList.contains('active')) {
                        if (input.dataset.originalRequired !== undefined) {
                            input.required = input.dataset.originalRequired === 'true';
                        }
                    } else {
                        input.dataset.originalRequired = input.required;
                        input.required = false;
                    }
                });
            });
        });
    });

    // ==========================================
    // CARD NUMBER FORMATTING
    // ==========================================
    const cardNumber = document.getElementById('card_number');
    if (cardNumber) {
        cardNumber.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;
        });
    }

    // ==========================================
    // PHONE NUMBER VALIDATION (NEQUI)
    // ==========================================
    const nequiPhone = document.getElementById('nequi_phone');
    if (nequiPhone) {
        nequiPhone.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }

    // ==========================================
    // SAVED ADDRESS SELECTOR
    // ==========================================
    const savedAddressSelect = document.getElementById('saved_address');
    if (savedAddressSelect) {
        savedAddressSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];

            if (this.value) {
                // Fill address fields with saved data
                document.getElementById('address_line1').value = selectedOption.dataset.line1 || '';
                document.getElementById('address_line2').value = selectedOption.dataset.line2 || '';
                document.getElementById('city').value = selectedOption.dataset.city || '';
                document.getElementById('state').value = selectedOption.dataset.state || '';
            } else {
                // Clear fields for new address
                document.getElementById('address_line1').value = '';
                document.getElementById('address_line2').value = '';
                document.getElementById('city').value = '';
                document.getElementById('state').value = '';
            }
        });
    }

    // ==========================================
    // FORM VALIDATION BEFORE SUBMIT
    // ==========================================
    form.addEventListener('submit', function(e) {
        const selectedMethod = document.querySelector('input[name="payment_method"]:checked').value;
        let isValid = true;
        let errorMessage = '';

        // Customer info validation
        const customerName = document.getElementById('customer_name').value.trim();
        const customerEmail = document.getElementById('customer_email').value.trim();
        const customerPhone = document.getElementById('customer_phone').value.trim();

        if (!customerName || !customerEmail || !customerPhone) {
            isValid = false;
            errorMessage = 'Por favor completa toda la información del cliente';
        }

        // Address validation
        const addressLine1 = document.getElementById('address_line1').value.trim();
        const city = document.getElementById('city').value.trim();
        const state = document.getElementById('state').value.trim();

        if (!addressLine1 || !city || !state) {
            isValid = false;
            errorMessage = 'Por favor completa la dirección de envío';
        }

        // Method-specific validation
        if (selectedMethod === 'CARD') {
            const cardNum = document.getElementById('card_number').value.replace(/\s/g, '');
            const cardHolder = document.getElementById('card_holder').value.trim();
            const cardMonth = document.getElementById('card_exp_month').value;
            const cardYear = document.getElementById('card_exp_year').value;
            const cardCvc = document.getElementById('card_cvc').value;

            if (!cardNum || cardNum.length < 13 || !cardHolder || !cardMonth || !cardYear || !cardCvc) {
                isValid = false;
                errorMessage = 'Por favor completa todos los datos de la tarjeta';
            }
        } else if (selectedMethod === 'PSE') {
            const pseBank = document.getElementById('pse_bank').value;
            const pseDoc = document.getElementById('pse_document_number').value.trim();

            if (!pseBank || !pseDoc) {
                isValid = false;
                errorMessage = 'Por favor completa todos los datos para PSE';
            }
        } else if (selectedMethod === 'NEQUI') {
            const nequiPhone = document.getElementById('nequi_phone').value;

            if (!nequiPhone || nequiPhone.length !== 10) {
                isValid = false;
                errorMessage = 'Por favor ingresa un número de celular válido (10 dígitos)';
            }
        }

        // Terms acceptance
        const acceptTerms = document.getElementById('accept_terms').checked;
        if (!acceptTerms) {
            isValid = false;
            errorMessage = 'Debes aceptar los términos y condiciones';
        }

        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
            return false;
        }

        // Disable button to prevent double submission
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    });
});
