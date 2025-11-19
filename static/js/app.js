document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts después de 5 segundos
    autoDismissAlerts();
    
    // Smooth scroll para anchors
    enableSmoothScroll();
    
    // Confirmación para acciones importantes
    enableConfirmations();
    
    // Actualizar hora actual en tiempo real
    updateCurrentTime();
    
    // Efectos hover mejorados
    enhanceCardHover();
    
    // Validación de formularios en tiempo real
    enableFormValidation();
});

// Auto-dismiss para alerts
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Smooth scroll para mejor UX
function enableSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Confirmaciones para acciones importantes
function enableConfirmations() {
    const reserveButtons = document.querySelectorAll('.btn-reserve-confirm');
    reserveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres reservar esta sala?')) {
                e.preventDefault();
            }
        });
    });
}

// Actualizar hora actual en tiempo real
function updateCurrentTime() {
    const timeElements = document.querySelectorAll('.current-time');
    if (timeElements.length > 0) {
        function updateTime() {
            const now = new Date();
            const timeString = now.toLocaleTimeString('es-CL', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            const dateString = now.toLocaleDateString('es-CL', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
            
            timeElements.forEach(element => {
                element.textContent = `${dateString} ${timeString}`;
            });
        }
        
        updateTime();
        setInterval(updateTime, 1000);
    }
}

// Efectos hover mejorados para cards
function enhanceCardHover() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
}

// Validación de formularios en tiempo real
function enableFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldValidation(this);
            });
        });
    });
}

// Validar campo individual
function validateField(field) {
    const value = field.value.trim();
    const feedback = field.parentNode.querySelector('.invalid-feedback') || createFeedbackElement(field);
    
    if (!value) {
        markFieldInvalid(field, feedback, 'Este campo es obligatorio');
        return false;
    }
    
    // Validación específica para RUT
    if (field.name === 'rut_reservante') {
        if (!validateRUT(value)) {
            markFieldInvalid(field, feedback, 'Por favor ingresa un RUT válido');
            return false;
        }
    }
    
    markFieldValid(field, feedback);
    return true;
}

// Validar RUT 
function validateRUT(rut) {
    // Limpiar y formatear RUT
    const cleanRUT = rut.replace(/[\.\-]/g, '').toUpperCase();
    
    if (cleanRUT.length < 8) return false;
    
    // Validar formato básico
    const rutRegex = /^[0-9]+[0-9kK]{1}$/;
    return rutRegex.test(cleanRUT);
}

// Crear elemento de feedback
function createFeedbackElement(field) {
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    field.parentNode.appendChild(feedback);
    return feedback;
}

// Marcar campo como inválido
function markFieldInvalid(field, feedback, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    feedback.textContent = message;
    feedback.style.display = 'block';
}

// Marcar campo como válido
function markFieldValid(field, feedback) {
    field.classList.add('is-valid');
    field.classList.remove('is-invalid');
    feedback.style.display = 'none';
}

// Limpiar validación del campo
function clearFieldValidation(field) {
    field.classList.remove('is-invalid', 'is-valid');
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.style.display = 'none';
    }
}

// Función para mostrar loading en botones
function showButtonLoading(button, text = 'Procesando...') {
    const originalText = button.innerHTML;
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        ${text}
    `;
    button.disabled = true;
    return originalText;
}

// Función para restaurar botón
function restoreButton(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}

// Exportar funciones para uso global (si es necesario)
window.app = {
    showButtonLoading,
    restoreButton,
    validateRUT
};