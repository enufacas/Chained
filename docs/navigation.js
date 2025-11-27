/**
 * Chained Documentation Navigation
 * Handles dynamic navigation injection and interactive features
 */

const NAVIGATION_HTML = `
<a href="index.html" class="nav-link">🏠 Home</a>

<!-- Primary Features - Always Visible -->
<div class="nav-section">
    <div class="nav-section-title">🎯 Core Features</div>
    <a href="world-map.html" class="nav-link nav-primary">🌍 World Map</a>
    <a href="agents.html" class="nav-link nav-primary highlight-agents">🤖 Agents</a>
    <a href="lifecycle.html" class="nav-link nav-primary highlight-lifecycle">🔄 Lifecycle</a>
    <a href="organism.html" class="nav-link nav-primary nav-special">🌐 Organism</a>
    <a href="agentops.html" class="nav-link nav-primary">📊 AgentOps</a>
    <a href="ai-knowledge-graph.html" class="nav-link nav-primary">🌐 Knowledge Graph</a>
</div>

<!-- Analytics & Insights - Collapsible -->
<div class="nav-section nav-collapsible">
    <button class="nav-section-toggle" aria-expanded="false" aria-controls="analytics-section">
        <span class="toggle-icon">▶</span>
        <span class="toggle-text">📊 Analytics & Insights</span>
    </button>
    <div class="nav-section-content" id="analytics-section">
        <a href="ab-testing-dashboard.html" class="nav-link">🔬 A/B Testing</a>
        <a href="architecture-evolution.html" class="nav-link">🏗️ Architecture</a>
        <a href="workflow-schedule.html" class="nav-link">🕐 Workflows</a>
        <a href="copilot-instructions.html" class="nav-link">📚 Instructions</a>
    </div>
</div>

<!-- Community & Media - Collapsible -->
<div class="nav-section nav-collapsible">
    <button class="nav-section-toggle" aria-expanded="false" aria-controls="community-section">
        <span class="toggle-icon">▶</span>
        <span class="toggle-text">🎬 Community & Media</span>
    </button>
    <div class="nav-section-content" id="community-section">
        <a href="tv.html" class="nav-link">📺 Chained TV</a>
        <a href="ai-friends.html" class="nav-link">💬 AI Friends</a>
    </div>
</div>

<!-- Quick Links -->
<div class="nav-section nav-footer">
    <div class="nav-section-title">🔗 Quick Links</div>
    <a href="#stats" class="nav-link nav-anchor">📊 Stats</a>
    <a href="#timeline" class="nav-link nav-anchor">⏰ Recent Activity</a>
    <a href="https://github.com/enufacas/Chained" target="_blank" rel="noopener noreferrer" class="nav-link">📂 GitHub</a>
</div>
`;

function injectNavigation() {
    const header = document.querySelector('header');
    if (!header) return;

    // Check if nav already exists (in case of static fallback or previous injection)
    let nav = document.querySelector('.main-nav');
    
    if (!nav) {
        nav = document.createElement('nav');
        nav.className = 'main-nav';
        header.appendChild(nav);
    }

    // Inject content
    nav.innerHTML = NAVIGATION_HTML;

    // Highlight current page
    highlightCurrentPage(nav);
}

function highlightCurrentPage(nav) {
    const currentPath = window.location.pathname;
    const filename = currentPath.split('/').pop() || 'index.html';
    
    const links = nav.querySelectorAll('a.nav-link');
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href === filename) {
            link.classList.add('active');
            // If inside a collapsible section, expand it
            const sectionContent = link.closest('.nav-section-content');
            if (sectionContent) {
                sectionContent.classList.add('expanded');
                const toggle = document.querySelector(`button[aria-controls="${sectionContent.id}"]`);
                if (toggle) {
                    toggle.setAttribute('aria-expanded', 'true');
                }
            }
        }
    });
}

// Navigation Toggle for Mobile/Tablet
document.addEventListener('DOMContentLoaded', function() {
    // 1. Inject Navigation
    injectNavigation();

    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('.main-nav');
    
    // Create and add backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'nav-backdrop';
    document.body.appendChild(backdrop);
    
    if (hamburger && nav) {
        // Toggle menu
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            this.classList.toggle('active');
            nav.classList.toggle('active');
            backdrop.classList.toggle('active');
            
            // Prevent body scroll when menu is open
            if (nav.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when clicking backdrop
        backdrop.addEventListener('click', function() {
            hamburger.classList.remove('active');
            nav.classList.remove('active');
            backdrop.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        // Close menu when clicking outside (keeping for compatibility)
        document.addEventListener('click', function(event) {
            if (!nav.contains(event.target) && !hamburger.contains(event.target)) {
                hamburger.classList.remove('active');
                nav.classList.remove('active');
                backdrop.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when clicking a link
        const navLinks = nav.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                nav.classList.remove('active');
                backdrop.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
        
        // Handle escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && nav.classList.contains('active')) {
                hamburger.classList.remove('active');
                nav.classList.remove('active');
                backdrop.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
    
    // Collapsible Navigation Sections
    const toggleButtons = document.querySelectorAll('.nav-section-toggle');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            const contentId = this.getAttribute('aria-controls');
            const content = document.getElementById(contentId);
            
            if (content) {
                if (isExpanded) {
                    // Collapse
                    this.setAttribute('aria-expanded', 'false');
                    content.classList.remove('expanded');
                } else {
                    // Expand
                    this.setAttribute('aria-expanded', 'true');
                    content.classList.add('expanded');
                }
            }
        });
    });
});
