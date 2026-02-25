/**
 * NetDevFlow Theme Management
 * Handles theme switching and persistence
 * Supports: light, dark, aether
 */

// Initialize theme on page load (before DOM ready to prevent flash)
(function() {
    const savedTheme = localStorage.getItem('site-theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

// Theme selection functionality
window.addEventListener('DOMContentLoaded', () => {
    /**
     * Set the theme and save to localStorage
     * @param {string} theme - 'light', 'dark', or 'aether'
     */
    window.setTheme = function(theme) {
        if (!['light', 'dark', 'aether'].includes(theme)) {
            console.warn(`Invalid theme: ${theme}`);
            return;
        }
        
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('site-theme', theme);
        updateThemeUI(theme);
    };

    /**
     * Update the visual state of theme selector buttons
     * @param {string} currentTheme - The currently active theme
     */
    const updateThemeUI = (currentTheme) => {
        // Update active state for all theme selector buttons
        document.querySelectorAll('.theme-selector').forEach(button => {
            const buttonTheme = button.getAttribute('data-theme');
            const textContent = button.textContent.trim();
            
            if (buttonTheme === currentTheme) {
                button.classList.add('active');
                button.setAttribute('aria-pressed', 'true');
                // Add checkmark if not already present
                if (!textContent.startsWith('✓')) {
                    button.innerHTML = button.innerHTML.replace(textContent, '✓ ' + textContent);
                }
            } else {
                button.classList.remove('active');
                button.setAttribute('aria-pressed', 'false');
                // Remove checkmark if present
                if (textContent.startsWith('✓')) {
                    button.innerHTML = button.innerHTML.replace('✓ ', '');
                }
            }
        });
    };

    // Attach listeners to all theme selector buttons
    document.querySelectorAll('.theme-selector').forEach(button => {
        // Add aria-pressed attribute for accessibility
        button.setAttribute('aria-pressed', 'false');
        
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const theme = button.getAttribute('data-theme');
            window.setTheme(theme);
        });
    });

    // Initialize UI state on page load
    const currentTheme = document.documentElement.getAttribute('data-theme');
    updateThemeUI(currentTheme);
});


