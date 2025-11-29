/**
 * theme.js
 * Handles light/dark mode toggling with security and persistence.
 * Implements "Separation of Concerns" as recommended by @skill-building-maven.
 */
(function() {
    // strict allow-list for theme values (Security recommendation by @monitor-champion)
    const THEMES = ['light', 'dark'];
    const DEFAULT_THEME = 'dark';
    const STORAGE_KEY = 'theme';

    function getSystemPreference() {
        return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }

    function getStoredTheme() {
        const stored = localStorage.getItem(STORAGE_KEY);
        return THEMES.includes(stored) ? stored : null;
    }

    function setTheme(theme) {
        if (!THEMES.includes(theme)) return;

        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);
        
        // Update toggle button accessibility/icon if it exists
        updateToggleButton(theme);
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        setTheme(next);
    }

    function updateToggleButton(theme) {
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.setAttribute('aria-label', `Switch to ${theme === 'light' ? 'dark' : 'light'} mode`);
            // If current is light, show Moon (to switch to dark). 
            // If current is dark, show Sun (to switch to light).
            btn.textContent = theme === 'light' ? '🌙' : '☀️'; 
            btn.title = `Switch to ${theme === 'light' ? 'dark' : 'light'} mode`;
        }
    }

    function initTheme() {
        const stored = getStoredTheme();
        const system = getSystemPreference();
        const initial = stored || system || DEFAULT_THEME;
        
        // Apply immediately
        setTheme(initial);

        // Expose toggle function globally for the button
        window.toggleTheme = toggleTheme;
    }

    // Run immediately to prevent FOUC
    initTheme();
    
    // Also run on DOMContentLoaded to ensure button is updated once DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        const current = document.documentElement.getAttribute('data-theme') || DEFAULT_THEME;
        updateToggleButton(current);
        
        // Bind click event if button exists (safer than onclick attribute)
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.addEventListener('click', toggleTheme);
        }
    });

})();
