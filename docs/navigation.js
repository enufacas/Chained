// Navigation Toggle for Mobile/Tablet
document.addEventListener('DOMContentLoaded', function() {
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

// Dynamically generate navigation
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


// Breadcrumb generation
function generateBreadcrumbs() {
    const main = document.querySelector("main");
    if (!main) return;

    // Get current filename
    const path = window.location.pathname;
    const filename = path.split("/").pop() || "index.html";
    
    // Basic breadcrumb structure
    let breadcrumbs = [{ text: "Home", url: "index.html" }];
    
    // If we are on home page, we can choose to show just "Home" or nothing
    if (filename === "index.html" || filename === "") {
        breadcrumbs[0].active = true;
    } else {
        // Find current page in navConfig
        let found = false;
        
        // We need to iterate sections
        if (typeof navConfig !== "undefined") {
            for (const section of navConfig) {
                if (section.items) {
                    const item = section.items.find(i => i.url === filename);
                    if (item) {
                        // Found it
                        // Add Section
                        breadcrumbs.push({ text: section.title, url: null });
                        // Add Page
                        breadcrumbs.push({ text: item.text, url: filename, active: true });
                        found = true;
                        break;
                    }
                }
            }
        }
        
        // Fallback if not in navConfig
        if (!found) {
            let title = filename.replace(".html", "").replace(/-/g, " ");
            // Capitalize words
            title = title.replace(/\b\w/g, l => l.toUpperCase());
            breadcrumbs.push({ text: title, url: filename, active: true });
        }
    }

    // Construct HTML
    const nav = document.createElement("nav");
    nav.className = "breadcrumb";
    nav.setAttribute("aria-label", "Breadcrumb");
    
    const list = document.createElement("ol");
    list.className = "breadcrumb-list";
    
    breadcrumbs.forEach((item, index) => {
        const li = document.createElement("li");
        li.className = "breadcrumb-item";
        if (item.active) li.classList.add("active");
        
        if (item.active) {
            li.setAttribute("aria-current", "page");
            li.textContent = item.text;
        } else if (item.url) {
            const a = document.createElement("a");
            a.href = item.url;
            a.textContent = item.text;
            li.appendChild(a);
        } else {
            // Text only (like section title)
            li.textContent = item.text;
        }
        
        list.appendChild(li);
        
        // Separator
        if (index < breadcrumbs.length - 1) {
            const sep = document.createElement("li");
            sep.className = "breadcrumb-separator";
            sep.setAttribute("aria-hidden", "true");
            sep.textContent = "/";
            list.appendChild(sep);
        }
    });
    
    nav.appendChild(list);
    
    // Insert at top of main
    main.insertBefore(nav, main.firstChild);
}

document.addEventListener("DOMContentLoaded", generateBreadcrumbs);
