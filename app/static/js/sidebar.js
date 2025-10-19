/**
 * Controls the sidebar collapse/expand functionality
 */
class SidebarController {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        // We'll remove the toggle button and rely only on hover behavior
        this.init();
    }
    
    init() {
        // Start with collapsed sidebar by default
        this.sidebar.classList.add('collapsed');
        
        // Add hover listeners to show/hide sidebar
        this.sidebar.addEventListener('mouseenter', () => {
            if (window.innerWidth > 768) { // Only on desktop
                this.expandSidebar();
            }
        });
        
        this.sidebar.addEventListener('mouseleave', () => {
            if (window.innerWidth > 768) { // Only on desktop
                this.collapseSidebar();
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                // On mobile, don't collapse automatically
                this.sidebar.classList.remove('collapsed');
            } else {
                this.sidebar.classList.add('collapsed');
            }
        });
    }
    
    expandSidebar() {
        this.sidebar.classList.add('expanded');
    }
    
    collapseSidebar() {
        this.sidebar.classList.remove('expanded');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('sidebar')) {
        window.sidebarController = new SidebarController();
    }
});