// Base JavaScript for the application
class App {
    constructor() {
        this.theme = localStorage.getItem('app-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme();
        this.bindEvents();
        this.initComponents();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);

        // Update theme toggle buttons
        document.querySelectorAll('#theme-toggle').forEach(btn => {
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = this.theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
            btn.setAttribute('title', this.theme === 'light' ? 'Chuyển sang chế độ tối' : 'Chuyển sang chế độ sáng');
        });
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('app-theme', this.theme);
        this.applyTheme();
    }

    bindEvents() {
        // Theme toggles
        document.addEventListener('click', (e) => {
            if (e.target.closest('#theme-toggle')) {
                this.toggleTheme();
            }
        });

        // Flash messages auto dismiss
        this.autoDismissFlash();

        // Smooth scrolling for anchor links
        document.addEventListener('click', (e) => {
            if (e.target.closest('a[href^="#"]')) {
                e.preventDefault();
                const target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });

        // Form enhancements
        this.enhanceForms();
    }

    autoDismissFlash() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.animation = 'slideInRight 0.3s ease reverse';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
    }

    enhanceForms() {
        // Add loading states to forms
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('needs-loading')) {
                this.showFormLoading(form);
            }
        });

        // Password visibility toggle
        document.addEventListener('click', (e) => {
            if (e.target.closest('.toggle-password')) {
                const button = e.target.closest('.toggle-password');
                const input = button.previousElementSibling;
                const icon = button.querySelector('i');

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.className = 'fas fa-eye-slash';
                } else {
                    input.type = 'password';
                    icon.className = 'fas fa-eye';
                }
            }
        });
    }

    showFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        submitBtn.innerHTML = `
            <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            Đang xử lý...
        `;
        submitBtn.disabled = true;

        // Revert after form submission (you might want to handle this differently based on your form handling)
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    }

    initComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Utility methods
    showToast(message, type = 'info') {
        // You can implement a toast notification system here
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    formatDate(date) {
        return new Date(date).toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

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
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
}

// Scroll buttons functionality
document.addEventListener('DOMContentLoaded', function() {
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    const scrollBottomBtn = document.getElementById('scrollBottomBtn');

    // Show/hide scroll top button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollTopBtn.classList.remove('hidden');
        } else {
            scrollTopBtn.classList.add('hidden');
        }
    });

    // Scroll to top
    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Scroll to bottom
    scrollBottomBtn.addEventListener('click', function() {
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    });

    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update button icon
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }

        // Update button title
        themeToggle.setAttribute('title', newTheme === 'dark' ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối');
    }

    // Initialize theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Update theme toggle icon based on saved theme
    const themeIcon = themeToggle.querySelector('i');
    if (themeIcon) {
        themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    themeToggle.setAttribute('title', savedTheme === 'dark' ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối');

    // Add event listener for theme toggle
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // Flash messages auto close
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        const closeBtn = message.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        }

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (message.parentNode) {
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (message.parentNode) {
                        message.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
});