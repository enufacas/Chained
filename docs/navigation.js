// ===========================================================================
// NAVIGATION CONFIGURATION
// ===========================================================================
// This configuration is used for both dynamic navigation generation and
// breadcrumb navigation. Update this to change navigation structure.
// ===========================================================================
const navConfig = [
    {
        title: "Core",
        items: [
            { text: "Dashboard", url: "index.html", icon: "📊" },
            { text: "Agents", url: "agents.html", icon: "🤖" },
            { text: "Organism", url: "organism.html", icon: "🧬" },
            { text: "World Map", url: "world-map.html", icon: "🌍" },
            { text: "Episodes", url: "episodes.html", icon: "🎬" },
            { text: "TV Mode", url: "tv.html", icon: "📺" }
        ]
    },
    {
        title: "Intelligence",
        items: [
            { text: "Knowledge Graph", url: "ai-knowledge-graph.html", icon: "🧠" },
            { text: "AI Friends", url: "ai-friends.html", icon: "👥" },
            { text: "Architecture", url: "architecture-evolution.html", icon: "🏗️" },
            { text: "AgentOps", url: "agentops.html", icon: "⚙️" },
            { text: "A2A System", url: "a2a.html", icon: "🤝" },
            { text: "A2A Visualization", url: "a2a-visualization.html", icon: "🔄" },
            { text: "A/B Testing", url: "ab-testing-dashboard.html", icon: "🧪" }
        ]
    },
    {
        title: "Reviews",
        items: [
            { text: "Reviewer", url: "reviewer-dashboard.html", icon: "📝" },
            { text: "Workflows", url: "workflow-schedule.html", icon: "📅" },
            { text: "Lifecycle", url: "lifecycle.html", icon: "🔄" }
        ]
    }
];

// Navigation Toggle for Mobile/Tablet
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('.main-nav');
    
    // Create and add backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'nav-backdrop';
    document.body.appendChild(backdrop);
    
    // ===========================================================================
    // BREADCRUMBS NAVIGATION
    // ===========================================================================
    // Generates breadcrumb navigation based on the current page location
    // and the navConfig structure. Shows: Home > Section > Current Page
    // ===========================================================================
    function generateBreadcrumbs() {
        // Don't show breadcrumbs on the homepage
        const currentPath = window.location.pathname;
        const currentPage = currentPath.split('/').pop() || 'index.html';
        
        if (currentPage === 'index.html' || currentPage === '') {
            return; // No breadcrumbs on homepage
        }
        
        // Find the current page in navConfig
        let currentItem = null;
        let currentSection = null;
        
        for (const section of navConfig) {
            for (const item of section.items) {
                if (currentPage === item.url || currentPath.endsWith(item.url)) {
                    currentItem = item;
                    currentSection = section;
                    break;
                }
            }
            if (currentItem) break;
        }
        
        // Create breadcrumb container
        const breadcrumbNav = document.createElement('nav');
        breadcrumbNav.className = 'breadcrumbs';
        breadcrumbNav.setAttribute('aria-label', 'Breadcrumb navigation');
        
        const breadcrumbList = document.createElement('ol');
        breadcrumbList.className = 'breadcrumb-list';
        
        // Home link (always present)
        const homeLi = document.createElement('li');
        homeLi.className = 'breadcrumb-item';
        const homeLink = document.createElement('a');
        homeLink.href = 'index.html';
        homeLink.className = 'breadcrumb-link';
        homeLink.innerHTML = '<span class="breadcrumb-icon">🏠</span> Home';
        homeLi.appendChild(homeLink);
        breadcrumbList.appendChild(homeLi);
        
        // Section (if found in navConfig)
        if (currentSection) {
            const sectionLi = document.createElement('li');
            sectionLi.className = 'breadcrumb-item';
            const separator1 = document.createElement('span');
            separator1.className = 'breadcrumb-separator';
            separator1.setAttribute('aria-hidden', 'true');
            separator1.textContent = '›';
            sectionLi.appendChild(separator1);
            
            const sectionSpan = document.createElement('span');
            sectionSpan.className = 'breadcrumb-section';
            sectionSpan.textContent = currentSection.title;
            sectionLi.appendChild(sectionSpan);
            breadcrumbList.appendChild(sectionLi);
        }
        
        // Current page
        const currentLi = document.createElement('li');
        currentLi.className = 'breadcrumb-item breadcrumb-current';
        currentLi.setAttribute('aria-current', 'page');
        
        const separator2 = document.createElement('span');
        separator2.className = 'breadcrumb-separator';
        separator2.setAttribute('aria-hidden', 'true');
        separator2.textContent = '›';
        currentLi.appendChild(separator2);
        
        const currentSpan = document.createElement('span');
        currentSpan.className = 'breadcrumb-text';
        
        if (currentItem) {
            currentSpan.innerHTML = `<span class="breadcrumb-icon">${currentItem.icon}</span> ${currentItem.text}`;
        } else {
            // Fallback: generate from page title or filename
            const pageTitle = document.title || currentPage.replace('.html', '').replace(/-/g, ' ');
            currentSpan.textContent = pageTitle.split(' | ')[0] || pageTitle;
        }
        currentLi.appendChild(currentSpan);
        breadcrumbList.appendChild(currentLi);
        
        breadcrumbNav.appendChild(breadcrumbList);
        
        // Insert breadcrumbs after the header
        const header = document.querySelector('header');
        if (header && header.nextSibling) {
            header.parentNode.insertBefore(breadcrumbNav, header.nextSibling);
        } else if (header) {
            header.parentNode.appendChild(breadcrumbNav);
        } else {
            // Fallback: insert at beginning of body
            document.body.insertBefore(breadcrumbNav, document.body.firstChild);
        }
    }
    
    // Generate breadcrumbs on page load
    generateBreadcrumbs();
    
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

    // Inject Standard Footer if missing
    if (!document.querySelector('footer')) {
        const footer = document.createElement('footer');
        footer.innerHTML = `
            <div class="footer-info">
                <p>&copy; ${new Date().getFullYear()} Chained - The Perpetual AI Motion Machine</p>
                <p>
                    <a href="https://github.com/enufacas/Chained" target="_blank">View on GitHub</a> • 
                    <a href="agents.html">Agent Leaderboard</a> • 
                    <a href="organism.html">Digital Organism</a>
                </p>
            </div>
        `;
        document.body.appendChild(footer);
    }
});

// ===========================================================================
// DYNAMIC NAVIGATION GENERATION
// ===========================================================================
function generateNavigation() {
    const nav = document.querySelector('.main-nav');
    if (!nav) return;
    
    // Clear existing content except the header
    const header = nav.querySelector('.nav-header');
    nav.innerHTML = '';
    if (header) nav.appendChild(header);

    navConfig.forEach(section => {
        const sectionEl = document.createElement('div');
        sectionEl.className = 'nav-section';
        
        const titleId = section.title.toLowerCase().replace(/\s+/g, '-') + '-nav';
        const contentId = section.title.toLowerCase().replace(/\s+/g, '-') + '-content';
        
        // Create header
        const headerEl = document.createElement('button');
        headerEl.className = 'nav-section-toggle';
        headerEl.setAttribute('aria-expanded', 'true');
        headerEl.setAttribute('aria-controls', contentId);
        headerEl.innerHTML = `
            <span class="nav-section-title">${section.title}</span>
            <span class="nav-section-icon">▼</span>
        `;
        
        // Create links container
        const contentEl = document.createElement('div');
        contentEl.id = contentId;
        contentEl.className = 'nav-section-content expanded';
        
        section.items.forEach(item => {
            const link = document.createElement('a');
            link.href = item.url;
            link.className = 'nav-link';
            if (window.location.pathname.endsWith(item.url)) {
                link.classList.add('active');
            }
            link.innerHTML = `<span class="nav-icon">${item.icon}</span> ${item.text}`;
            contentEl.appendChild(link);
        });
        
        sectionEl.appendChild(headerEl);
        sectionEl.appendChild(contentEl);
        nav.appendChild(sectionEl);
    });
    
    // Re-initialize listeners for the new elements
    const toggleButtons = nav.querySelectorAll('.nav-section-toggle');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            const contentId = this.getAttribute('aria-controls');
            const content = document.getElementById(contentId);
            
            if (content) {
                if (isExpanded) {
                    this.setAttribute('aria-expanded', 'false');
                    content.classList.remove('expanded');
                } else {
                    this.setAttribute('aria-expanded', 'true');
                    content.classList.add('expanded');
                }
            }
        });
    });
}

// Call on load
document.addEventListener('DOMContentLoaded', generateNavigation);
