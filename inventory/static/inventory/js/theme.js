/**
 * NetDevFlow Theme Management
 * Handles theme switching and persistence
 */

// Initialize theme on page load (before DOM ready to prevent flash)
(function() {
    const savedTheme = localStorage.getItem('site-theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

// Theme toggle functionality
window.addEventListener('DOMContentLoaded', () => {
    // Create and append theme toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'theme-toggle-btn';
    toggleBtn.setAttribute('type', 'button');
    toggleBtn.innerHTML = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀️' : '🌙';
    toggleBtn.setAttribute('title', 'Toggle theme');
    toggleBtn.setAttribute('aria-label', 'Toggle dark/light theme');
    document.body.appendChild(toggleBtn);

    // Toggle theme on button click
    toggleBtn.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('site-theme', next);
        toggleBtn.innerHTML = next === 'dark' ? '☀️' : '🌙';
    });

    // Update theme label in user menu if it exists
    const updateThemeUI = (theme) => {
        const labels = document.querySelectorAll('.theme-label');
        labels.forEach(label => {
            label.textContent = theme === 'dark' ? '☀️ Switch to Light Mode' : '🌙 Switch to Dark Mode';
        });
    };

    const toggleTheme = () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('site-theme', next);
        updateThemeUI(next);
    };

    // Initial UI state
    updateThemeUI(document.documentElement.getAttribute('data-theme'));

    // Attach listeners to all theme toggle triggers
    document.querySelectorAll('.theme-toggle-trigger').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleTheme();
        });
    });
});
