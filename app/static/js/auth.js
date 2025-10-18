// Authentication related JavaScript
class AuthApp {
    constructor() {
        this.theme = localStorage.getItem('auth-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme();
        this.bindEvents();
        this.initFormValidations();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);

        const themeToggle = document.getElementById('auth-theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            themeToggle.querySelector('span').textContent = this.theme === 'light' ? 'Chế độ tối' : 'Chế độ sáng';
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('auth-theme', this.theme);
        this.applyTheme();
    }

    bindEvents() {
        // Theme toggle
        const themeToggle = document.getElementById('auth-theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Auto-dismiss flash messages
        this.autoDismissFlash();

        // Form enhancements
        this.enhanceForms();

        // Password strength indicator
        this.initPasswordStrength();

        // Real-time validation
        this.initRealTimeValidation();
    }

    autoDismissFlash() {
        const flashMessages = document.querySelectorAll('.auth-flash-message');
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.animation = 'authSlideInRight 0.3s ease reverse';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
    }

    enhanceForms() {
        // Add loading states to forms
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('auth-form')) {
                this.showFormLoading(form);
            }
        });

        // Input animations
        this.initInputAnimations();
    }

    showFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        submitBtn.innerHTML = `
            <div class="auth-spinner"></div>
            Đang xử lý...
        `;
        submitBtn.disabled = true;

        // Re-enable after 5 seconds (fallback)
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 5000);
    }

    initInputAnimations() {
        const inputs = document.querySelectorAll('.form-control');

        inputs.forEach(input => {
            // Add focus effects
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('focused');
                }
            });

            // Check initial value
            if (input.value) {
                input.parentElement.classList.add('focused');
            }
        });
    }

    initPasswordStrength() {
        const passwordInput = document.getElementById('password');
        if (!passwordInput) return;

        const strengthBar = document.querySelector('.strength-fill');
        const strengthText = document.querySelector('.strength-text');

        passwordInput.addEventListener('input', (e) => {
            const password = e.target.value;
            const strength = this.calculatePasswordStrength(password);

            if (strengthBar) {
                strengthBar.style.width = strength.percentage + '%';
                strengthBar.className = 'strength-fill ' + strength.class;
            }

            if (strengthText) {
                strengthText.textContent = strength.text;
                strengthText.className = 'strength-text ' + strength.class;
            }
        });
    }

    calculatePasswordStrength(password) {
        let score = 0;
        let feedback = {
            class: 'very-weak',
            text: 'Rất yếu',
            percentage: 0
        };

        if (!password) return feedback;

        // Length check
        if (password.length >= 4) score++;
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;

        // Character variety
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^a-zA-Z0-9]/.test(password)) score++;

        // Determine strength
        if (score >= 6) {
            feedback = { class: 'strong', text: 'Rất mạnh', percentage: 100 };
        } else if (score >= 4) {
            feedback = { class: 'medium', text: 'Mạnh', percentage: 75 };
        } else if (score >= 2) {
            feedback = { class: 'weak', text: 'Trung bình', percentage: 50 };
        } else {
            feedback = { class: 'very-weak', text: 'Yếu', percentage: 25 };
        }

        return feedback;
    }

    initRealTimeValidation() {
        // Email validation
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', (e) => {
                this.validateEmail(e.target);
            });
        }

        // Phone validation
        const phoneInput = document.getElementById('phone_number');
        if (phoneInput) {
            phoneInput.addEventListener('blur', (e) => {
                this.validatePhone(e.target);
            });
        }

        // Password confirmation
        const passwordInput = document.getElementById('password');
        const confirmInput = document.getElementById('confirm_password');

        if (passwordInput && confirmInput) {
            confirmInput.addEventListener('input', (e) => {
                this.validatePasswordMatch(passwordInput.value, e.target);
            });
        }
    }

    validateEmail(input) {
        const email = input.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (email && !emailRegex.test(email)) {
            this.showFieldError(input, 'Email không hợp lệ');
        } else {
            this.clearFieldError(input);
        }
    }

    validatePhone(input) {
        const phone = input.value;
        const phoneRegex = /^(?:\+84|0)(?:\d){9,10}$/;

        if (phone && !phoneRegex.test(phone)) {
            this.showFieldError(input, 'Số điện thoại không hợp lệ');
        } else {
            this.clearFieldError(input);
        }
    }

    validatePasswordMatch(password, confirmInput) {
        if (confirmInput.value && password !== confirmInput.value) {
            this.showFieldError(confirmInput, 'Mật khẩu không khớp');
        } else {
            this.clearFieldError(confirmInput);
        }
    }

    showFieldError(input, message) {
        this.clearFieldError(input);

        input.classList.add('is-invalid');

        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;

        input.parentNode.appendChild(errorDiv);
    }

    clearFieldError(input) {
        input.classList.remove('is-invalid');

        const existingError = input.parentNode.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    showNotification(message, type = 'info') {
        // Implement a toast notification system
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.authApp = new AuthApp();
});