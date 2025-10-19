/**
 * Sidebar Controller
 */
class SidebarController {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        if (!this.sidebar) return;
        
        this.collapsed = true;
        this.init();
        this.bindEvents();
    }
    
    init() {
        // Sidebar collapsed by default
        this.sidebar.classList.add('collapsed');
    }
    
    bindEvents() {
        // Expand on hover (desktop)
        if (window.innerWidth > 768) {
            this.sidebar.addEventListener('mouseenter', () => {
                this.sidebar.classList.remove('collapsed');
            });
            
            this.sidebar.addEventListener('mouseleave', () => {
                this.sidebar.classList.add('collapsed');
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        window.sidebarController = new SidebarController();
    }
});