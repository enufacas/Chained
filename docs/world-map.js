/**
 * Chained World Map - Leaflet Implementation
 * Real-time Agent Explorer with Interactive Mapping
 * @investigate-champion implementation
 */

let map = null;
let worldState = null;
let knowledge = null;
let issuesData = null; // Store issues data for linking
let pullsData = null; // Store PRs data for linking
let agentMarkers = null;
let pathLayerGroup = null; // Layer group for agent paths
let regionsLayerGroup = null; // Layer group for regions
let learningsLayerGroup = null; // Layer group for learnings/work
let gcpLayerGroup = null; // Layer group for GCP infrastructure (@integrate-specialist)
let a2aLayerGroup = null; // Layer group for A2A communications (@integrate-specialist)
let layerControl = null; // Leaflet layer control
let agentLocations = {}; // Map agent names to locations
let allMarkers = []; // Store all marker references for filtering
let searchQuery = ''; // Current search query
let showActive = true; // Filter: show active agents
let showInactive = true; // Filter: show inactive agents

// Score-based filters (@support-master enhancement)
let showHOF = true; // Show Hall of Fame agents (≥85%)
let showGood = true; // Show good agents (≥50%)
let showOK = true; // Show OK agents (≥30%)
let showAtRisk = true; // Show at-risk agents (<30%)

// Default locations for agents (diverse global distribution)
const DEFAULT_AGENT_LOCATIONS = {
    // Performance & Optimization
    'accelerate-master': { lat: 37.7749, lng: -122.4194, city: 'San Francisco, CA' },
    'accelerate-specialist': { lat: 47.6062, lng: -122.3321, city: 'Seattle, WA' },
    
    // Testing & Quality
    'assert-specialist': { lat: 40.7128, lng: -74.0060, city: 'New York, NY' },
    'assert-whiz': { lat: 42.3601, lng: -71.0589, city: 'Boston, MA' },
    'validator-pro': { lat: 41.8781, lng: -87.6298, city: 'Chicago, IL' },
    'edge-cases-pro': { lat: 30.2672, lng: -97.7431, city: 'Austin, TX' },
    
    // Infrastructure & Creation
    'create-guru': { lat: 37.7749, lng: -122.4194, city: 'San Francisco, CA' },
    'create-champion': { lat: 47.6062, lng: -122.3321, city: 'Seattle, WA' },
    'infrastructure-specialist': { lat: 47.6740, lng: -122.1215, city: 'Redmond, WA' },
    'construct-specialist': { lat: 45.5152, lng: -122.6784, city: 'Portland, OR' },
    
    // Engineering & APIs
    'engineer-master': { lat: 51.5074, lng: -0.1278, city: 'London, UK' },
    'engineer-wizard': { lat: 48.8566, lng: 2.3522, city: 'Paris, France' },
    'develop-specialist': { lat: 52.5200, lng: 13.4050, city: 'Berlin, Germany' },
    
    // Integration & Communication
    'bridge-master': { lat: 35.6762, lng: 139.6503, city: 'Tokyo, Japan' },
    'integrate-specialist': { lat: 37.5665, lng: 126.9780, city: 'Seoul, South Korea' },
    
    // Investigation & Analysis
    'investigate-champion': { lat: 35.2271, lng: -80.8431, city: 'Charlotte, NC' },
    'investigate-specialist': { lat: 33.4484, lng: -112.0740, city: 'Phoenix, AZ' },
    
    // Organization & Structure
    'organize-guru': { lat: 39.9042, lng: 116.4074, city: 'Beijing, China' },
    'organize-specialist': { lat: 31.2304, lng: 121.4737, city: 'Shanghai, China' },
    'organize-expert': { lat: 22.3193, lng: 114.1694, city: 'Hong Kong' },
    'simplify-pro': { lat: 1.3521, lng: 103.8198, city: 'Singapore' },
    'restructure-master': { lat: -33.8688, lng: 151.2093, city: 'Sydney, Australia' },
    'refactor-champion': { lat: -37.8136, lng: 144.9631, city: 'Melbourne, Australia' },
    
    // Security
    'secure-specialist': { lat: 47.6062, lng: -122.3321, city: 'Seattle, WA' },
    'secure-ninja': { lat: 32.7767, lng: -96.7970, city: 'Dallas, TX' },
    'secure-pro': { lat: 37.3382, lng: -121.8863, city: 'San Jose, CA' },
    'monitor-champion': { lat: 38.9072, lng: -77.0369, city: 'Washington, DC' },
    
    // Code Cleanup
    'cleaner-master': { lat: 39.7392, lng: -104.9903, city: 'Denver, CO' },
    
    // Network & Connectivity
    'connector-ninja': { lat: 34.0522, lng: -118.2437, city: 'Los Angeles, CA' },
    
    // Documentation & Support
    'clarify-champion': { lat: 49.2827, lng: -123.1207, city: 'Vancouver, Canada' },
    'document-ninja': { lat: 43.6532, lng: -79.3832, city: 'Toronto, Canada' },
    'communicator-maestro': { lat: 45.5017, lng: -73.5673, city: 'Montreal, Canada' },
    'support-master': { lat: 51.5074, lng: -0.1278, city: 'London, UK' },
    
    // Coordination & Workflow
    'coordinate-wizard': { lat: 55.7558, lng: 37.6173, city: 'Moscow, Russia' },
    'align-wizard': { lat: 52.3676, lng: 4.9041, city: 'Amsterdam, Netherlands' },
    'meta-coordinator': { lat: 50.1109, lng: 8.6821, city: 'Frankfurt, Germany' },
    
    // Coaching & Mentorship
    'coach-master': { lat: 59.3293, lng: 18.0686, city: 'Stockholm, Sweden' },
    'coach-wizard': { lat: 60.1699, lng: 24.9384, city: 'Helsinki, Finland' },
    'guide-wizard': { lat: 55.6761, lng: 12.5683, city: 'Copenhagen, Denmark' },
    
    // Innovation & Exploration
    'pioneer-pro': { lat: -23.5505, lng: -46.6333, city: 'São Paulo, Brazil' },
    'pioneer-sage': { lat: -22.9068, lng: -43.1729, city: 'Rio de Janeiro, Brazil' },
    'steam-machine': { lat: 19.4326, lng: -99.1332, city: 'Mexico City, Mexico' },
    
    // Specialized
    'tools-analyst': { lat: 28.6139, lng: 77.2090, city: 'New Delhi, India' },
    'cloud-architect': { lat: 12.9716, lng: 77.5946, city: 'Bangalore, India' },
    'troubleshoot-expert': { lat: 47.6062, lng: -122.3321, city: 'Seattle, WA' }
};

// Initialize Leaflet map
function initMap() {
    const mapDiv = document.getElementById('map');
    
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('Leaflet library failed to load');
        mapDiv.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; background: #1a1a2e; border-radius: 12px; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🗺️</div>
                <h2 style="color: #0891b2; margin-bottom: 1rem;">Map Unavailable</h2>
                <p style="color: #9ca3af; text-align: center; max-width: 400px; margin-bottom: 1rem;">
                    The map library failed to load. This may be due to ad blockers or network restrictions.
                </p>
                <p style="color: #9ca3af; text-align: center; max-width: 400px; margin-bottom: 1rem;">
                    The world state is still being loaded and displayed in the sidebar. 
                    You can view agent locations and metrics there.
                </p>
                <button onclick="location.reload()" style="background: #0891b2; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; cursor: pointer; font-size: 1rem; margin-top: 1rem;">
                    🔄 Try Reloading
                </button>
            </div>
        `;
        // Still load data for sidebar
        loadWorldData().then(success => {
            if (success) {
                updateSidebar();
            }
        });
        return;
    }
    
    // Create Leaflet map
    map = L.map('map', {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 18,
        worldCopyJump: true
    });
    
    // Add OpenStreetMap tile layer (light theme for better visibility)
    // Using CARTO Positron - a clean, light-colored map that provides excellent contrast
    // with the dark UI theme, making markers and labels clearly visible
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);
    
    // Initialize marker cluster group
    agentMarkers = L.markerClusterGroup({
        iconCreateFunction: function(cluster) {
            const count = cluster.getChildCount();
            let size = 'small';
            if (count > 10) size = 'large';
            else if (count > 5) size = 'medium';
            
            return L.divIcon({
                html: `<div><span>${count}</span></div>`,
                className: `marker-cluster marker-cluster-${size}`,
                iconSize: L.point(40, 40)
            });
        },
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true
    });
    
    // Initialize layer groups for different features (@support-master enhancement)
    pathLayerGroup = L.layerGroup();
    regionsLayerGroup = L.layerGroup();
    learningsLayerGroup = L.layerGroup();
    gcpLayerGroup = L.layerGroup(); // GCP infrastructure layer (@integrate-specialist)
    a2aLayerGroup = L.layerGroup(); // A2A communications layer (@integrate-specialist)
    
    // Add base layers (always visible)
    map.addLayer(agentMarkers);
    
    // Add overlay layers (toggleable)
    const overlays = {
        "🤖 Agents": agentMarkers,
        "🗺️ Agent Paths": pathLayerGroup,
        "📍 Regions": regionsLayerGroup,
        "💡 Learnings & Work": learningsLayerGroup,
        "☁️ GCP Infrastructure": gcpLayerGroup,
        "🔄 A2A Communications": a2aLayerGroup
    };
    
    // Add layer control to map
    layerControl = L.control.layers(null, overlays, {
        collapsed: false,
        position: 'topright'
    }).addTo(map);
    
    // Add overlay layers to map by default
    pathLayerGroup.addTo(map);
    regionsLayerGroup.addTo(map);
    learningsLayerGroup.addTo(map);
    gcpLayerGroup.addTo(map); // Enable GCP layer by default (@integrate-specialist)
    a2aLayerGroup.addTo(map); // Enable A2A layer by default (@integrate-specialist)
    
    return true;
}

// Load world data
async function loadWorldData() {
    try {
        // Show loading state
        const refreshBtn = document.getElementById('refresh-btn');
        const lastUpdateEl = document.getElementById('last-update');
        if (refreshBtn) refreshBtn.textContent = '⏳ Loading...';
        
        const stateResponse = await fetch('./world/world_state.json');
        if (!stateResponse.ok) {
            throw new Error(`Failed to load world state: ${stateResponse.status}`);
        }
        worldState = await stateResponse.json();
        
        const knowledgeResponse = await fetch('./world/knowledge.json');
        if (!knowledgeResponse.ok) {
            throw new Error(`Failed to load knowledge: ${knowledgeResponse.status}`);
        }
        knowledge = await knowledgeResponse.json();
        
        // Load issues data for PR/issue links (@support-master enhancement)
        try {
            const issuesResponse = await fetch('./data/issues.json');
            if (issuesResponse.ok) {
                issuesData = await issuesResponse.json();
            }
        } catch (e) {
            console.warn('Issues data not available:', e);
        }
        
        // Load PRs data for PR links (@support-master enhancement)
        try {
            const pullsResponse = await fetch('./data/pulls.json');
            if (pullsResponse.ok) {
                pullsData = await pullsResponse.json();
            }
        } catch (e) {
            console.warn('PRs data not available:', e);
        }
        
        // Update last refresh time
        if (lastUpdateEl) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            lastUpdateEl.textContent = `Last updated: ${timeStr}`;
            lastUpdateEl.style.color = '#10b981';
        }
        
        // Update world state time if available
        if (worldState && worldState.time) {
            const stateTime = new Date(worldState.time);
            if (lastUpdateEl) {
                lastUpdateEl.textContent = `Data from: ${stateTime.toLocaleString()}`;
            }
        }
        
        if (refreshBtn) refreshBtn.textContent = '🔄 Refresh Data';
        return true;
    } catch (error) {
        console.error('Error loading world data:', error);
        
        // Show error state
        const refreshBtn = document.getElementById('refresh-btn');
        const lastUpdateEl = document.getElementById('last-update');
        if (refreshBtn) {
            refreshBtn.textContent = '⚠️ Failed to Load';
            setTimeout(() => {
                refreshBtn.textContent = '🔄 Refresh Data';
            }, 3000);
        }
        if (lastUpdateEl) {
            lastUpdateEl.textContent = `Error: ${error.message}`;
            lastUpdateEl.style.color = '#ef4444';
        }
        return false;
    }
}

// Get agent location (from world state or defaults)
function getAgentLocation(agentLabel) {
    // Check if agent has location in world state
    let worldStateLocation = null;
    if (worldState && worldState.agents && worldState.regions) {
        const agent = worldState.agents.find(a => a.label === agentLabel);
        if (agent && agent.location_region_id) {
            const region = worldState.regions.find(r => r.id === agent.location_region_id);
            if (region) {
                worldStateLocation = {
                    lat: region.lat,
                    lng: region.lng,
                    city: region.label,
                    region_id: region.id
                };
            }
        }
    }
    
    // Get default location based on agent specialization
    const agentKey = findAgentKey(agentLabel);
    const defaultLocation = agentKey && DEFAULT_AGENT_LOCATIONS[agentKey] 
        ? DEFAULT_AGENT_LOCATIONS[agentKey] 
        : null;
    
    // SMART PRIORITY: Use default location if world state shows Charlotte (spawn point)
    // This distributes agents across tech hubs based on their specialization
    // while respecting agents that have moved to other regions
    if (worldStateLocation) {
        const isCharlotte = worldStateLocation.region_id === 'US:Charlotte' || 
                          (worldStateLocation.lat === 35.2271 && worldStateLocation.lng === -80.8431);
        
        // If agent is still in Charlotte (spawn point) and we have a better default location, use it
        if (isCharlotte && defaultLocation) {
            return defaultLocation;
        }
        
        // Otherwise, use world state location (agent has moved)
        return worldStateLocation;
    }
    
    // Fall back to default location for inactive agents
    if (defaultLocation) {
        return defaultLocation;
    }
    
    // Final fallback to Charlotte, NC if no location found
    return { lat: 35.2271, lng: -80.8431, city: 'Charlotte, NC' };
}

// Find agent key from label (fuzzy matching)
function findAgentKey(label) {
    // Extract meaningful words from label
    const labelLower = label.toLowerCase();
    
    // Direct mapping for known patterns - prioritized by specificity
    const nameMap = {
        'robert martin': 'organize-guru',
        'martin fowler': 'organize-specialist',
        'linus torvalds': 'construct-specialist',
        'moxie marlinspike': 'secure-ninja',
        'bruce schneier': 'guardian-master',
        'katie moussouris': 'monitor-champion',
        'grace hopper': 'infrastructure-specialist',
        'margaret hamilton': 'APIs-architect',
        'tim berners-lee': 'bridge-master',
        'vint cerf': 'connector-ninja',
        'alan kay': 'pioneer-sage',
        'ivan sutherland': 'pioneer-pro',
        'donald knuth': 'guide-wizard',
        'neil degrasse tyson': 'clarify-champion',
        'richard feynman': 'communicator-maestro',
        'quincy jones': 'coordinate-wizard',
        'martha graham': 'align-wizard',
        'grady booch': 'coach-wizard',
        'michael feathers': 'cleaner-master',
        'nancy leveson': 'edge-cases-pro',
        'ada lovelace': 'investigate-specialist',
        'marie curie': 'accelerate-master',
        'charles darwin': 'pioneer-sage',
        'einstein': 'pioneer-sage',
        'tesla': 'create-guru',
        'turing': 'meta-coordinator',
        'liskov': 'coach-master',
        'dijkstra': 'validator-pro',
        'knuth': 'assert-specialist',
        'shannon': 'monitor-champion',
        'feynman': 'communicator-maestro',
        'hamilton': 'secure-ninja',
        'hopper': 'troubleshoot-expert',
        'darwin': 'pioneer-sage',
        'lovelace': 'investigate-specialist',
        'curie': 'accelerate-master',
        'ada': 'investigate-champion',
        'steam machine': 'steam-machine'
    };
    
    // Check direct mappings
    for (const [key, value] of Object.entries(nameMap)) {
        if (labelLower.includes(key)) {
            return value;
        }
    }
    
    // Try to match by emoji - more comprehensive mapping
    if (labelLower.includes('🧹')) return 'organize-guru';
    if (labelLower.includes('🧪')) return 'assert-specialist';
    if (labelLower.includes('💭')) return 'meta-coordinator';
    if (labelLower.includes('🎯')) return 'investigate-champion';
    if (labelLower.includes('🔒')) return 'secure-specialist';
    if (labelLower.includes('🚨')) return 'secure-specialist';
    if (labelLower.includes('🔐')) return 'monitor-champion';
    if (labelLower.includes('🔨')) return 'construct-specialist';
    if (labelLower.includes('🏭')) return 'create-guru';
    if (labelLower.includes('⚙️')) return 'engineer-master';
    if (labelLower.includes('📖')) return 'document-ninja';
    if (labelLower.includes('📝')) return 'document-ninja';
    if (labelLower.includes('🎹')) return 'coordinate-wizard';
    if (labelLower.includes('🎻')) return 'align-wizard';
    if (labelLower.includes('☁️')) return 'cloud-architect';
    if (labelLower.includes('🔌')) return 'connector-ninja';
    if (labelLower.includes('🔄')) return 'bridge-master';
    if (labelLower.includes('✨')) return 'simplify-pro';
    if (labelLower.includes('♻️')) return 'organize-expert';
    if (labelLower.includes('🗂️')) return 'organize-specialist';
    if (labelLower.includes('✔️')) return 'validator-pro';
    if (labelLower.includes('🎓')) return 'guide-wizard';
    if (labelLower.includes('🚀')) return 'pioneer-sage';
    if (labelLower.includes('🔬')) return 'edge-cases-pro';
    if (labelLower.includes('📡')) return 'steam-machine';
    if (labelLower.includes('🌟')) return 'steam-machine';
    if (labelLower.includes('🛡️')) return 'guardian-master';
    if (labelLower.includes('📈')) return 'accelerate-master';
    if (labelLower.includes('🔧')) return 'troubleshoot-expert';
    
    // Keyword matching as last resort
    if (labelLower.includes('clean')) return 'organize-guru';
    if (labelLower.includes('test')) return 'assert-specialist';
    if (labelLower.includes('secur')) return 'secure-specialist';
    if (labelLower.includes('build')) return 'construct-specialist';
    if (labelLower.includes('engineer')) return 'engineer-master';
    if (labelLower.includes('document')) return 'document-ninja';
    if (labelLower.includes('cloud')) return 'cloud-architect';
    if (labelLower.includes('architect')) return 'APIs-architect';
    
    return null;
}

// Get issues for an agent (@support-master enhancement)
function getAgentIssues(agentLabel, agentSpecialization) {
    if (!issuesData) return [];
    
    // Find issues assigned to this agent or with matching agent label
    const agentIssues = issuesData.filter(issue => {
        // Check if issue mentions the agent in body or title
        const bodyMentions = issue.body && (
            issue.body.includes(`@${agentSpecialization}`) ||
            issue.body.includes(agentLabel)
        );
        
        // Check if issue has agent label
        const hasAgentLabel = issue.labels && issue.labels.some(label => 
            label.name === `agent:${agentSpecialization}`
        );
        
        return bodyMentions || hasAgentLabel;
    });
    
    // Return most recent 5 issues
    return agentIssues
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .slice(0, 5);
}

// Get PRs for an agent (@support-master enhancement)
function getAgentPRs(agentLabel, agentSpecialization) {
    if (!pullsData) return [];
    
    // Find PRs that mention the agent or have agent label
    const agentPRs = pullsData.filter(pr => {
        const bodyMentions = pr.body && (
            pr.body.includes(`@${agentSpecialization}`) ||
            pr.body.includes(agentLabel)
        );
        
        const hasAgentLabel = pr.labels && pr.labels.some(label => 
            label.name === `agent:${agentSpecialization}`
        );
        
        return bodyMentions || hasAgentLabel;
    });
    
    // Return most recent 5 PRs
    return agentPRs
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .slice(0, 5);
}

// Get learning/work info for an idea (@support-master enhancement)
function getLearningInfo(ideaId) {
    if (!knowledge || !knowledge.ideas) return null;
    
    const idea = knowledge.ideas.find(i => i.id === ideaId);
    if (!idea) return null;
    
    // Find related issue for this idea
    let relatedIssue = null;
    if (issuesData) {
        relatedIssue = issuesData.find(issue => 
            issue.body && issue.body.includes(ideaId)
        );
    }
    
    return {
        idea: idea,
        issue: relatedIssue,
        sourceUrl: idea.source_url || null
    };
}

// Create custom agent marker icon
function createAgentIcon(agent) {
    const score = agent.metrics?.overall_score || 0;
    let color = '#6b7280'; // gray
    if (score >= 0.85) color = '#10b981'; // green for hall of fame
    else if (score >= 0.5) color = '#0891b2'; // cyan for good
    else if (score >= 0.3) color = '#f59e0b'; // amber for ok
    else color = '#ef4444'; // red for at risk
    
    return L.divIcon({
        html: `<div style="background-color: ${color}; border: 2px solid white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">🤖</div>`,
        className: 'agent-marker-icon',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12]
    });
}

// Filter and search functions
function applyFilters() {
    showActive = document.getElementById('filter-active').checked;
    showInactive = document.getElementById('filter-inactive').checked;
    
    // Score-based filters (@support-master enhancement)
    showHOF = document.getElementById('filter-hof')?.checked ?? true;
    showGood = document.getElementById('filter-good')?.checked ?? true;
    showOK = document.getElementById('filter-ok')?.checked ?? true;
    showAtRisk = document.getElementById('filter-atrisk')?.checked ?? true;
    
    if (map) {
        renderAgents();
    }
    updateSidebar();
}

function setupSearch() {
    const searchInput = document.getElementById('agent-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase();
            if (map) {
                renderAgents();
            }
            updateSidebar();
        });
    }
}

function matchesSearch(agentLabel) {
    if (!searchQuery) return true;
    return agentLabel.toLowerCase().includes(searchQuery);
}

// Get agent score category (@support-master helper)
function getAgentScoreCategory(score) {
    if (score >= 0.85) return 'hof';
    if (score >= 0.5) return 'good';
    if (score >= 0.3) return 'ok';
    return 'atrisk';
}

function shouldShowAgent(agent, isActive) {
    // Check search filter
    if (!matchesSearch(agent.label || agent)) return false;
    
    // Check active/inactive filter
    if (isActive && !showActive) return false;
    if (!isActive && !showInactive) return false;
    
    // Check score-based filters for active agents (@support-master)
    if (isActive && agent.metrics) {
        const score = agent.metrics.overall_score || 0;
        const category = getAgentScoreCategory(score);
        
        if (category === 'hof' && !showHOF) return false;
        if (category === 'good' && !showGood) return false;
        if (category === 'ok' && !showOK) return false;
        if (category === 'atrisk' && !showAtRisk) return false;
    }
    
    return true;
}

// Render all agents on map
function renderAgents() {
    if (!worldState || !worldState.agents || !map) return;
    
    // Clear existing markers and layers (@support-master layer management)
    agentMarkers.clearLayers();
    pathLayerGroup.clearLayers();
    regionsLayerGroup.clearLayers();
    learningsLayerGroup.clearLayers();
    gcpLayerGroup.clearLayers(); // Clear GCP layer (@integrate-specialist)
    a2aLayerGroup.clearLayers(); // Clear A2A layer (@integrate-specialist)
    
    // Get all agent definitions
    const allAgentKeys = Object.keys(DEFAULT_AGENT_LOCATIONS);
    
    // Track which agents are in world state
    const activeAgents = new Set(worldState.agents.map(a => a.label));
    
    // Render active agents from world state
    let visibleActiveCount = 0;
    let visibleInactiveCount = 0;
    
    worldState.agents.forEach(agent => {
        // Apply filters
        if (!shouldShowAgent(agent, true)) return;
        visibleActiveCount++;
        
        const location = getAgentLocation(agent.label);
        const icon = createAgentIcon(agent);
        
        const marker = L.marker([location.lat, location.lng], { icon });
        
        // Draw agent path if exists
        if (agent.path && agent.path.length > 0) {
            drawAgentPath(agent, location);
        }
        
        // Create popup content with enhanced PR/issue links (@support-master)
        const score = agent.metrics?.overall_score || 0;
        const specialization = agent.specialization || 'general';
        const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
        
        // Get recent issues and PRs for this agent
        const recentIssues = getAgentIssues(agent.label, specialization);
        const recentPRs = getAgentPRs(agent.label, specialization);
        
        // Build issues section
        let issuesHtml = '';
        if (recentIssues && recentIssues.length > 0) {
            issuesHtml = '<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e5e7eb;">' +
                '<p style="margin: 4px 0; font-size: 12px; font-weight: bold; color: #6b7280;">📋 Recent Issues:</p>';
            recentIssues.slice(0, 3).forEach(issue => {
                const issueUrl = issue.html_url || `https://github.com/enufacas/Chained/issues/${issue.number}`;
                issuesHtml += `<p style="margin: 2px 0; font-size: 11px;">
                    <a href="${issueUrl}" target="_blank" style="color: #0891b2; text-decoration: none;">
                        #${issue.number} - ${issue.title.substring(0, 30)}${issue.title.length > 30 ? '...' : ''}
                    </a>
                </p>`;
            });
            issuesHtml += '</div>';
        }
        
        // Build PRs section
        let prsHtml = '';
        if (recentPRs && recentPRs.length > 0) {
            prsHtml = '<div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e5e7eb;">' +
                '<p style="margin: 4px 0; font-size: 12px; font-weight: bold; color: #6b7280;">🔀 Recent PRs:</p>';
            recentPRs.slice(0, 3).forEach(pr => {
                const prUrl = pr.html_url || `https://github.com/enufacas/Chained/pull/${pr.number}`;
                const statusIcon = pr.state === 'merged' ? '✅' : pr.state === 'closed' ? '❌' : '🔄';
                prsHtml += `<p style="margin: 2px 0; font-size: 11px;">
                    <a href="${prUrl}" target="_blank" style="color: #0891b2; text-decoration: none;">
                        ${statusIcon} #${pr.number} - ${pr.title.substring(0, 30)}${pr.title.length > 30 ? '...' : ''}
                    </a>
                </p>`;
            });
            prsHtml += '</div>';
        }
        
        // Build learning/work info
        let learningHtml = '';
        if (idea) {
            const learningInfo = getLearningInfo(agent.current_idea_id);
            learningHtml = `<p style="margin: 4px 0; font-size: 13px;"><strong>💡 Current Work:</strong> ${idea.title}</p>`;
            if (learningInfo && learningInfo.sourceUrl) {
                learningHtml += `<p style="margin: 2px 0; font-size: 11px;">
                    <a href="${learningInfo.sourceUrl}" target="_blank" style="color: #10b981; text-decoration: none;">
                        🔗 View Learning Source
                    </a>
                </p>`;
            }
            if (learningInfo && learningInfo.issue) {
                const issueUrl = learningInfo.issue.html_url || `https://github.com/enufacas/Chained/issues/${learningInfo.issue.number}`;
                learningHtml += `<p style="margin: 2px 0; font-size: 11px;">
                    <a href="${issueUrl}" target="_blank" style="color: #10b981; text-decoration: none;">
                        📋 Related Issue #${learningInfo.issue.number}
                    </a>
                </p>`;
            }
        }
        
        const popupContent = `
            <div style="min-width: 250px; max-width: 350px;">
                <h3 style="margin: 0 0 8px 0; color: #0891b2; font-size: 16px;">🤖 ${agent.label}</h3>
                <p style="margin: 4px 0; font-size: 13px;"><strong>🏷️ Specialization:</strong> ${specialization}</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>📍 Location:</strong> ${location.city}</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>📊 Status:</strong> ${agent.status}</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>⭐ Score:</strong> ${(score * 100).toFixed(0)}%</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>📈 Metrics:</strong> ${agent.metrics?.issues_resolved || 0} issues | ${agent.metrics?.prs_merged || 0} PRs</p>
                ${learningHtml}
                ${agent.path && agent.path.length > 0 ? `<p style="margin: 4px 0; font-size: 13px;"><strong>🗺️ Journey:</strong> ${agent.path.length} stops remaining</p>` : ''}
                ${issuesHtml}
                ${prsHtml}
            </div>
        `;
        
        marker.bindPopup(popupContent);
        agentMarkers.addLayer(marker);
    });
    
    // Add placeholder markers for inactive agents
    allAgentKeys.forEach(agentKey => {
        // Check if this agent is already rendered
        const existingLabel = worldState.agents.find(a => {
            const key = findAgentKey(a.label);
            return key === agentKey;
        });
        
        if (!existingLabel) {
            // Apply filters for inactive agents
            if (!shouldShowAgent(agentKey, false)) return;
            visibleInactiveCount++;
            
            const location = DEFAULT_AGENT_LOCATIONS[agentKey];
            
            // Create gray marker for inactive agent
            const icon = L.divIcon({
                html: '<div style="background-color: #4b5563; border: 2px solid white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px; opacity: 0.5; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">💤</div>',
                className: 'agent-marker-icon-inactive',
                iconSize: [20, 20],
                iconAnchor: [10, 10],
                popupAnchor: [0, -10]
            });
            
            const marker = L.marker([location.lat, location.lng], { icon });
            
            const popupContent = `
                <div style="min-width: 180px;">
                    <h3 style="margin: 0 0 8px 0; color: #6b7280; font-size: 14px;">💤 ${agentKey}</h3>
                    <p style="margin: 4px 0; font-size: 12px; color: #9ca3af;"><strong>Status:</strong> Not yet spawned</p>
                    <p style="margin: 4px 0; font-size: 12px; color: #9ca3af;"><strong>📍 Location:</strong> ${location.city}</p>
                    <p style="margin: 4px 0; font-size: 12px; color: #9ca3af;"><em>This agent will activate when spawned by the system.</em></p>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            agentMarkers.addLayer(marker);
        }
    });
    
    // Update agent count display
    const agentCountEl = document.getElementById('agent-count');
    if (agentCountEl) {
        agentCountEl.textContent = visibleActiveCount + visibleInactiveCount;
    }
    
    // Render region markers
    renderRegions();
    
    // Render GCP infrastructure and A2A communications (@integrate-specialist)
    renderGCPInfrastructure();
    renderA2ACommunications();
}

// Draw agent movement path on map with improved visualization
function drawAgentPath(agent, currentLocation) {
    if (!agent.path || agent.path.length === 0 || !worldState.regions) return;
    
    const pathCoordinates = [[currentLocation.lat, currentLocation.lng]];
    const pathRegions = [];
    
    // Get coordinates and region info for each stop in the path
    agent.path.forEach(regionId => {
        const region = worldState.regions.find(r => r.id === regionId);
        if (region) {
            pathCoordinates.push([region.lat, region.lng]);
            pathRegions.push(region);
        }
    });
    
    // Draw path with color based on agent score
    const score = agent.metrics?.overall_score || 0;
    let pathColor = '#6b7280';
    if (score >= 0.85) pathColor = '#10b981';
    else if (score >= 0.5) pathColor = '#0891b2';
    else if (score >= 0.3) pathColor = '#f59e0b';
    else pathColor = '#ef4444';
    
    // Draw main path line with animation-like dashing
    const polyline = L.polyline(pathCoordinates, {
        color: pathColor,
        weight: 3,
        opacity: 0.7,
        dashArray: '10, 8',
        lineJoin: 'round',
        lineCap: 'round'
    });
    
    // Create detailed journey popup
    const journeyStops = pathRegions.map((region, idx) => 
        `<div style="padding: 4px 0; border-left: 3px solid ${pathColor}; padding-left: 8px; margin: 4px 0;">
            <strong style="color: ${pathColor};">${idx + 1}.</strong> ${region.label}
            ${region.idea_count ? `<br><small style="color: #9ca3af;">💡 ${region.idea_count} ideas here</small>` : ''}
        </div>`
    ).join('');
    
    polyline.bindPopup(`
        <div style="min-width: 200px; max-width: 280px;">
            <h4 style="margin: 0 0 8px 0; color: ${pathColor}; border-bottom: 2px solid ${pathColor}; padding-bottom: 4px;">
                🗺️ ${agent.label}'s Journey
            </h4>
            <p style="margin: 6px 0; font-size: 13px;">
                <strong>📍 Current Location:</strong> ${currentLocation.city}
            </p>
            <p style="margin: 6px 0; font-size: 13px;">
                <strong>🎯 Total Stops:</strong> ${agent.path.length}
            </p>
            <div style="margin-top: 8px; max-height: 200px; overflow-y: auto;">
                <strong style="font-size: 12px; color: #9ca3af;">JOURNEY PATH:</strong>
                ${journeyStops}
            </div>
        </div>
    `);
    
    pathLayerGroup.addLayer(polyline);
    
    // Add numbered waypoint markers with better styling
    agent.path.forEach((regionId, index) => {
        const region = worldState.regions.find(r => r.id === regionId);
        if (region) {
            // Create custom numbered marker icon
            const waypointIcon = L.divIcon({
                html: `<div style="
                    background: ${pathColor}; 
                    color: white; 
                    border: 2px solid white; 
                    border-radius: 50%; 
                    width: 24px; 
                    height: 24px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: bold; 
                    font-size: 11px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
                    ">${index + 1}</div>`,
                className: 'waypoint-marker',
                iconSize: [24, 24],
                iconAnchor: [12, 12],
                popupAnchor: [0, -12]
            });
            
            const waypointMarker = L.marker([region.lat, region.lng], { icon: waypointIcon });
            
            // Calculate ETA (estimated time of arrival) - simple calculation
            const stopsAway = index + 1;
            const etaText = stopsAway === 1 ? 'Next stop' : `${stopsAway} stops away`;
            
            waypointMarker.bindPopup(`
                <div style="min-width: 180px;">
                    <h4 style="margin: 0 0 6px 0; color: ${pathColor}; font-size: 14px;">
                        Stop #${index + 1}: ${region.label}
                    </h4>
                    <p style="margin: 4px 0; font-size: 12px; color: #9ca3af;">
                        🎯 ${etaText}
                    </p>
                    ${region.idea_count ? `<p style="margin: 4px 0; font-size: 12px;">💡 ${region.idea_count} ideas active</p>` : ''}
                    <p style="margin: 6px 0 0 0; font-size: 11px; color: #6b7280; font-style: italic;">
                        Click ${agent.label}'s marker to see full journey
                    </p>
                </div>
            `);
            
            pathLayerGroup.addLayer(waypointMarker);
        }
    });
    
    // Add direction arrow at the end of path for clarity
    if (pathRegions.length > 0) {
        const lastRegion = pathRegions[pathRegions.length - 1];
        const arrowIcon = L.divIcon({
            html: `<div style="
                color: ${pathColor}; 
                font-size: 20px;
                text-shadow: 0 0 4px white, 0 0 8px white;
                ">🎯</div>`,
            className: 'path-destination',
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
        
        const destinationMarker = L.marker([lastRegion.lat, lastRegion.lng], { icon: arrowIcon });
        destinationMarker.bindPopup(`
            <div style="text-align: center;">
                <p style="margin: 0; font-weight: bold; color: ${pathColor};">🎯 Final Destination</p>
                <p style="margin: 4px 0 0 0; font-size: 12px;">${lastRegion.label}</p>
            </div>
        `);
        
        pathLayerGroup.addLayer(destinationMarker);
    }
}

// Render regions with idea counts and enhanced metadata
function renderRegions() {
    if (!worldState || !worldState.regions) return;
    
    // Clear region layer (managed by layer control now)
    regionsLayerGroup.clearLayers();
    
    worldState.regions.forEach(region => {
        const ideaCount = region.idea_count || 0;
        const agentsHere = worldState.agents.filter(a => a.location_region_id === region.id);
        const agentCount = agentsHere.length;
        
        // Determine region color based on type
        let circleColor = '#0891b2'; // default cyan
        let regionIcon = '📍';
        
        if (region.is_home_base) {
            circleColor = '#f59e0b'; // amber for home base
            regionIcon = '🏠';
        } else if (region.region_type === 'innovation_hub') {
            circleColor = '#10b981'; // green for innovation hubs
            regionIcon = '🚀';
        } else if (region.region_type === 'tech_hub') {
            circleColor = '#0891b2'; // cyan for tech hubs
            regionIcon = '💻';
        } else if (region.region_type === 'financial_hub') {
            circleColor = '#8b5cf6'; // purple for financial
            regionIcon = '💰';
        } else if (region.region_type === 'manufacturing_hub' || region.region_type === 'hardware_hub') {
            circleColor = '#f59e0b'; // amber for manufacturing
            regionIcon = '⚙️';
        } else if (region.region_type === 'startup_hub') {
            circleColor = '#ec4899'; // pink for startups
            regionIcon = '🌟';
        }
        
        // Calculate activity level (ideas + agents)
        const activityScore = ideaCount + (agentCount * 2);
        
        // Skip empty regions unless they're home base
        if (activityScore === 0 && !region.is_home_base) return;
        
        // Size circle based on activity
        const baseRadius = 8000;
        const radius = Math.max(baseRadius, Math.min(100000, activityScore * 5000));
        
        // Create circle for region with enhanced styling
        const circle = L.circle([region.lat, region.lng], {
            radius: radius,
            color: circleColor,
            fillColor: circleColor,
            fillOpacity: Math.min(0.3, 0.1 + (activityScore * 0.02)),
            weight: 2,
            opacity: 0.6
        });
        
        // Build rich popup with metadata
        let popupContent = `
            <div style="min-width: 220px;">
                <h3 style="margin: 0 0 8px 0; color: ${circleColor}; border-bottom: 2px solid ${circleColor}; padding-bottom: 4px;">
                    ${regionIcon} ${region.label}
                </h3>
        `;
        
        // Add region type and timezone if available
        if (region.region_type) {
            const typeLabel = region.region_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            popupContent += `<p style="margin: 4px 0; font-size: 12px; color: #9ca3af;"><strong>Type:</strong> ${typeLabel}</p>`;
        }
        
        if (region.timezone) {
            popupContent += `<p style="margin: 4px 0; font-size: 12px; color: #9ca3af;"><strong>🕐 Timezone:</strong> ${region.timezone}</p>`;
        }
        
        // Add activity metrics
        popupContent += `<div style="margin: 8px 0; padding: 8px; background: rgba(0,0,0,0.1); border-radius: 4px;">`;
        popupContent += `<p style="margin: 4px 0; font-size: 13px;"><strong>💡 Ideas:</strong> ${ideaCount}</p>`;
        popupContent += `<p style="margin: 4px 0; font-size: 13px;"><strong>🤖 Agents:</strong> ${agentCount}`;
        
        if (region.agent_capacity) {
            const capacityPct = (agentCount / region.agent_capacity * 100).toFixed(0);
            popupContent += ` / ${region.agent_capacity} <span style="color: ${capacityPct > 80 ? '#ef4444' : '#10b981'}">(${capacityPct}%)</span>`;
        }
        popupContent += `</p>`;
        
        // Add tech ecosystem info if available
        if (region.tech_ecosystem) {
            const eco = region.tech_ecosystem;
            if (eco.specializations && eco.specializations.length > 0) {
                const specs = eco.specializations.slice(0, 3).map(s => s.replace(/_/g, ' ')).join(', ');
                popupContent += `<p style="margin: 4px 0; font-size: 12px; color: #9ca3af;"><strong>🎯 Focus:</strong> ${specs}</p>`;
            }
        }
        popupContent += `</div>`;
        
        // Add agents list if any
        if (agentsHere.length > 0) {
            popupContent += `<div style="margin-top: 8px;">`;
            popupContent += `<p style="margin: 4px 0; font-size: 11px; font-weight: bold; color: #9ca3af;">Active Agents:</p>`;
            agentsHere.slice(0, 5).forEach(agent => {
                const score = agent.metrics?.overall_score || 0;
                const scoreColor = score >= 0.85 ? '#10b981' : score >= 0.5 ? '#0891b2' : '#f59e0b';
                popupContent += `<p style="margin: 2px 0; font-size: 11px;">• ${agent.label} <span style="color: ${scoreColor}">(${(score * 100).toFixed(0)}%)</span></p>`;
            });
            if (agentsHere.length > 5) {
                popupContent += `<p style="margin: 2px 0; font-size: 11px; color: #9ca3af; font-style: italic;">... and ${agentsHere.length - 5} more</p>`;
            }
            popupContent += `</div>`;
        }
        
        // Add cost multiplier if available
        if (region.cost_multiplier && region.cost_multiplier !== 1.0) {
            popupContent += `<p style="margin: 6px 0 0 0; font-size: 11px; color: ${region.cost_multiplier > 1.5 ? '#ef4444' : '#9ca3af'};">
                💵 Cost: ${region.cost_multiplier}x
            </p>`;
        }
        
        // Add home base indicator
        if (region.is_home_base) {
            popupContent += `<p style="margin: 8px 0 0 0; font-size: 12px; color: ${circleColor}; font-weight: bold;">🏠 Agent Home Base</p>`;
        }
        
        popupContent += `</div>`;
        
        circle.bindPopup(popupContent);
        regionsLayerGroup.addLayer(circle);
        
        // Add label for significant regions or home base
        if (activityScore > 5 || region.is_home_base) {
            const label = L.marker([region.lat, region.lng], {
                icon: L.divIcon({
                    html: `<div style="background: ${circleColor}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${regionIcon} ${region.label}</div>`,
                    className: 'region-label',
                    iconSize: null
                })
            });
            regionsLayerGroup.addLayer(label);
        }
    });
    
    // Render learnings layer (@support-master enhancement)
    renderLearnings();
}

// Render learnings and work accomplished on the map (@support-master)
function renderLearnings() {
    if (!knowledge || !knowledge.ideas) return;
    
    learningsLayerGroup.clearLayers();
    
    // Get all ideas with location data
    knowledge.ideas.forEach(idea => {
        if (!idea.inspiration_regions || idea.inspiration_regions.length === 0) return;
        
        // Use the primary inspiration region (highest weight)
        const primaryRegion = idea.inspiration_regions.reduce((max, r) => 
            r.weight > max.weight ? r : max
        );
        
        // Get learning info with PR/issue links
        const learningInfo = getLearningInfo(idea.id);
        
        // Create learning marker
        const learningIcon = L.divIcon({
            html: '<div style="background-color: #10b981; border: 2px solid white; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-size: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">💡</div>',
            className: 'learning-marker-icon',
            iconSize: [16, 16],
            iconAnchor: [8, 8],
            popupAnchor: [0, -8]
        });
        
        const marker = L.marker([primaryRegion.lat, primaryRegion.lng], { icon: learningIcon });
        
        // Build popup with links
        let popupContent = `
            <div style="min-width: 220px; max-width: 300px;">
                <h4 style="margin: 0 0 8px 0; color: #10b981; font-size: 14px;">💡 ${idea.title}</h4>
                <p style="margin: 4px 0; font-size: 12px; color: #6b7280;">${idea.summary ? idea.summary.substring(0, 150) : 'No summary available'}${idea.summary && idea.summary.length > 150 ? '...' : ''}</p>
        `;
        
        // Add patterns/topics if available
        if (idea.patterns && idea.patterns.length > 0) {
            popupContent += `<p style="margin: 6px 0; font-size: 11px;"><strong>🏷️ Topics:</strong> ${idea.patterns.slice(0, 3).join(', ')}</p>`;
        }
        
        // Add source link if available
        if (learningInfo && learningInfo.sourceUrl) {
            popupContent += `<p style="margin: 6px 0;">
                <a href="${learningInfo.sourceUrl}" target="_blank" style="color: #10b981; text-decoration: none; font-size: 12px;">
                    🔗 View Original Source
                </a>
            </p>`;
        }
        
        // Add related issue link if available
        if (learningInfo && learningInfo.issue) {
            const issueUrl = learningInfo.issue.html_url || `https://github.com/enufacas/Chained/issues/${learningInfo.issue.number}`;
            popupContent += `<p style="margin: 6px 0;">
                <a href="${issueUrl}" target="_blank" style="color: #0891b2; text-decoration: none; font-size: 12px;">
                    📋 Issue #${learningInfo.issue.number}
                </a>
            </p>`;
        }
        
        // Add companies involved if available
        if (idea.companies && idea.companies.length > 0) {
            const companyNames = idea.companies.map(c => c.name).slice(0, 3).join(', ');
            popupContent += `<p style="margin: 6px 0; font-size: 11px; color: #9ca3af;"><strong>🏢 Companies:</strong> ${companyNames}</p>`;
        }
        
        popupContent += `</div>`;
        
        marker.bindPopup(popupContent);
        learningsLayerGroup.addLayer(marker);
    });
}

// GCP Infrastructure configuration (@integrate-specialist)
const GCP_INFRASTRUCTURE = {
    location: {
        lat: 41.2619,
        lng: -95.8608,
        city: 'Council Bluffs, Iowa',
        region: 'us-central1'
    },
    cloudRunServices: [
        'academic-research',
        'blog-writer',
        'google-trends',
        'adk-api-server',
        'ag-ui-frontend',
        'chained-website',
        'chained-agent-gateway',
        'chained-agent-worker'
    ],
    supportingServices: [
        'Firestore',
        'Pub/Sub',
        'Artifact Registry'
    ]
};

// Home base location for A2A visualization (@integrate-specialist)
const HOME_BASE = {
    lat: 35.2271,
    lng: -80.8431,
    city: 'Charlotte, NC'
};

// A2A Communication flows configuration (@integrate-specialist)
const A2A_FLOWS = [
    { source: 'academic-research', target: 'blog-writer', data: 'Research Data' },
    { source: 'google-trends', target: 'blog-writer', data: 'SEO Data' },
    { source: 'All agents', target: 'adk-api-server', data: 'Coordination' }
];

// Render GCP Infrastructure on the map (@integrate-specialist)
function renderGCPInfrastructure() {
    if (!map) return;
    
    gcpLayerGroup.clearLayers();
    
    const gcp = GCP_INFRASTRUCTURE;
    
    // Create special GCP infrastructure marker with gradient styling
    const gcpIcon = L.divIcon({
        html: `<div style="
            background: linear-gradient(135deg, #4285f4 0%, #8b5cf6 50%, #0891b2 100%);
            border: 3px solid white;
            border-radius: 12px;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(66, 133, 244, 0.5), 0 0 20px rgba(139, 92, 246, 0.3);
            animation: pulse-gcp 2s ease-in-out infinite;
        ">☁️</div>
        <style>
            @keyframes pulse-gcp {
                0%, 100% { transform: scale(1); box-shadow: 0 4px 12px rgba(66, 133, 244, 0.5); }
                50% { transform: scale(1.05); box-shadow: 0 4px 20px rgba(66, 133, 244, 0.7), 0 0 30px rgba(139, 92, 246, 0.5); }
            }
        </style>`,
        className: 'gcp-infrastructure-marker',
        iconSize: [48, 48],
        iconAnchor: [24, 24],
        popupAnchor: [0, -24]
    });
    
    const gcpMarker = L.marker([gcp.location.lat, gcp.location.lng], { icon: gcpIcon });
    
    // Build rich popup content for GCP infrastructure
    const cloudRunHtml = gcp.cloudRunServices.map(service => 
        `<div style="padding: 4px 8px; background: rgba(66, 133, 244, 0.1); border-radius: 4px; margin: 3px 0; font-size: 12px;">
            🚀 ${service}
        </div>`
    ).join('');
    
    const supportingHtml = gcp.supportingServices.map(service => 
        `<div style="padding: 4px 8px; background: rgba(139, 92, 246, 0.1); border-radius: 4px; margin: 3px 0; font-size: 12px;">
            ⚙️ ${service}
        </div>`
    ).join('');
    
    const popupContent = `
        <div style="min-width: 280px; max-width: 350px;">
            <h3 style="margin: 0 0 12px 0; color: #4285f4; font-size: 16px; border-bottom: 2px solid #4285f4; padding-bottom: 8px;">
                ☁️ GCP Infrastructure - ${gcp.location.region}
            </h3>
            <p style="margin: 4px 0; font-size: 13px; color: #6b7280;">
                📍 ${gcp.location.city}
            </p>
            
            <div style="margin-top: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #4285f4; font-size: 13px;">
                    🚀 Cloud Run Services (${gcp.cloudRunServices.length})
                </h4>
                <div style="max-height: 150px; overflow-y: auto;">
                    ${cloudRunHtml}
                </div>
            </div>
            
            <div style="margin-top: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #8b5cf6; font-size: 13px;">
                    ⚙️ Supporting Services
                </h4>
                ${supportingHtml}
            </div>
            
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 11px; color: #9ca3af;">
                <strong>Status:</strong> <span style="color: #10b981;">● Active</span>
            </div>
        </div>
    `;
    
    gcpMarker.bindPopup(popupContent);
    gcpLayerGroup.addLayer(gcpMarker);
    
    // Add a subtle pulsing circle around GCP location
    const gcpCircle = L.circle([gcp.location.lat, gcp.location.lng], {
        radius: 50000, // 50km radius
        color: '#4285f4',
        fillColor: '#4285f4',
        fillOpacity: 0.1,
        weight: 2,
        opacity: 0.5,
        dashArray: '5, 10'
    });
    gcpLayerGroup.addLayer(gcpCircle);
}

// Render A2A Communication flows on the map (@integrate-specialist)
function renderA2ACommunications() {
    if (!map) return;
    
    a2aLayerGroup.clearLayers();
    
    const gcp = GCP_INFRASTRUCTURE;
    const homeBase = HOME_BASE;
    
    // Create animated polyline from GCP to Charlotte (coordination flow)
    const connectionCoords = [
        [gcp.location.lat, gcp.location.lng],
        [homeBase.lat, homeBase.lng]
    ];
    
    // Main A2A communication line with gradient effect
    const a2aLine = L.polyline(connectionCoords, {
        color: '#8b5cf6',
        weight: 4,
        opacity: 0.7,
        dashArray: '15, 10',
        lineCap: 'round',
        lineJoin: 'round'
    });
    
    // Build A2A popup content
    const flowsHtml = A2A_FLOWS.map(flow => 
        `<div style="padding: 6px 8px; background: rgba(139, 92, 246, 0.1); border-radius: 4px; margin: 4px 0; font-size: 12px; border-left: 3px solid #8b5cf6;">
            <strong>${flow.source}</strong> → <strong>${flow.target}</strong>
            <br><span style="color: #9ca3af; font-size: 11px;">${flow.data}</span>
        </div>`
    ).join('');
    
    const a2aPopupContent = `
        <div style="min-width: 260px; max-width: 320px;">
            <h3 style="margin: 0 0 12px 0; color: #8b5cf6; font-size: 16px; border-bottom: 2px solid #8b5cf6; padding-bottom: 8px;">
                🔄 A2A Protocol Communication
            </h3>
            <p style="margin: 4px 0; font-size: 12px; color: #6b7280;">
                Agent-to-Agent communication pipeline
            </p>
            
            <div style="margin-top: 12px;">
                <h4 style="margin: 0 0 8px 0; color: #8b5cf6; font-size: 13px;">
                    📡 Active Data Flows
                </h4>
                ${flowsHtml}
            </div>
            
            <div style="margin-top: 12px; padding: 8px; background: rgba(16, 185, 129, 0.1); border-radius: 4px;">
                <p style="margin: 0; font-size: 11px; color: #10b981;">
                    <strong>📍 Route:</strong> Council Bluffs, IA ↔ Charlotte, NC
                </p>
            </div>
            
            <div style="margin-top: 8px; font-size: 11px; color: #9ca3af;">
                <strong>Protocol:</strong> A2A (Agent-to-Agent)
            </div>
        </div>
    `;
    
    a2aLine.bindPopup(a2aPopupContent);
    a2aLayerGroup.addLayer(a2aLine);
    
    // Add animated data flow markers along the line
    const numFlowMarkers = 3;
    for (let i = 0; i < numFlowMarkers; i++) {
        const progress = (i + 1) / (numFlowMarkers + 1);
        const lat = gcp.location.lat + (homeBase.lat - gcp.location.lat) * progress;
        const lng = gcp.location.lng + (homeBase.lng - gcp.location.lng) * progress;
        
        const flowIcon = L.divIcon({
            html: `<div style="
                background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
                border: 2px solid white;
                border-radius: 50%;
                width: 16px;
                height: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                box-shadow: 0 2px 6px rgba(139, 92, 246, 0.5);
                animation: flow-pulse ${1 + i * 0.3}s ease-in-out infinite;
            ">⚡</div>
            <style>
                @keyframes flow-pulse {
                    0%, 100% { opacity: 0.6; transform: scale(0.9); }
                    50% { opacity: 1; transform: scale(1.1); }
                }
            </style>`,
            className: 'a2a-flow-marker',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
        });
        
        const flowMarker = L.marker([lat, lng], { icon: flowIcon });
        flowMarker.bindPopup(`
            <div style="text-align: center; padding: 4px;">
                <strong style="color: #8b5cf6;">⚡ Data in Transit</strong>
                <p style="margin: 4px 0 0 0; font-size: 11px; color: #9ca3af;">A2A Protocol</p>
            </div>
        `);
        a2aLayerGroup.addLayer(flowMarker);
    }
    
    // Add endpoint markers for better visibility
    // GCP endpoint indicator
    const gcpEndpoint = L.circleMarker([gcp.location.lat, gcp.location.lng], {
        radius: 8,
        color: '#4285f4',
        fillColor: '#4285f4',
        fillOpacity: 0.3,
        weight: 2
    });
    a2aLayerGroup.addLayer(gcpEndpoint);
    
    // Charlotte endpoint indicator
    const charlotteEndpoint = L.circleMarker([homeBase.lat, homeBase.lng], {
        radius: 8,
        color: '#10b981',
        fillColor: '#10b981',
        fillOpacity: 0.3,
        weight: 2
    });
    a2aLayerGroup.addLayer(charlotteEndpoint);
}

// Update infrastructure sidebar section (@integrate-specialist)
function updateInfrastructureSidebar() {
    const infrastructureInfo = document.getElementById('infrastructure-info');
    if (!infrastructureInfo) return;
    
    const gcp = GCP_INFRASTRUCTURE;
    
    infrastructureInfo.innerHTML = `
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: #4285f4; font-weight: bold;">☁️ GCP Region</span>
                <span style="color: #10b981; font-size: 0.85rem;">● Active</span>
            </div>
            <p style="margin: 0; font-size: 0.9rem; color: var(--text-muted, #b0b0b0);">
                ${gcp.location.region} (${gcp.location.city})
            </p>
        </div>
        
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-muted, #b0b0b0);">🚀 Deployed Services</span>
                <span style="color: var(--primary-color, #0891b2); font-weight: bold;">${gcp.cloudRunServices.length}</span>
            </div>
        </div>
        
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: var(--text-muted, #b0b0b0);">⚙️ Supporting Services</span>
                <span style="color: var(--primary-color, #0891b2); font-weight: bold;">${gcp.supportingServices.length}</span>
            </div>
        </div>
        
        <div style="padding: 8px; background: rgba(139, 92, 246, 0.1); border-radius: 6px; border-left: 3px solid #8b5cf6;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #8b5cf6; font-weight: bold;">🔄 A2A Pipeline</span>
                <span style="color: #10b981; font-size: 0.85rem;">● Active</span>
            </div>
            <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: var(--text-muted, #b0b0b0);">
                ${A2A_FLOWS.length} active data flows
            </p>
        </div>
    `;
}

// Update sidebar
function updateSidebar() {
    if (!worldState) return;
    
    // Count total agents (active + inactive)
    const totalAgents = Object.keys(DEFAULT_AGENT_LOCATIONS).length;
    const activeAgents = worldState.agents?.length || 0;
    
    // Update metrics
    document.getElementById('tick-value').textContent = worldState.tick || 0;
    document.getElementById('ideas-value').textContent = worldState.metrics?.total_ideas || 0;
    document.getElementById('regions-value').textContent = worldState.metrics?.total_regions || 0;
    document.getElementById('agents-value').textContent = `${activeAgents}/${totalAgents}`;
    document.getElementById('hof-value').textContent = worldState.metrics?.hall_of_fame_count || 0;
    
    // Update scoring thresholds
    const promotionThreshold = worldState.metrics?.promotion_threshold || 0.85;
    const eliminationThreshold = worldState.metrics?.elimination_threshold || 0.3;
    document.getElementById('promotion-threshold').innerHTML = 
        `<span style="color: #10b981;">${(promotionThreshold * 100).toFixed(0)}%</span>`;
    document.getElementById('elimination-threshold').innerHTML = 
        `<span style="color: #ef4444;">${(eliminationThreshold * 100).toFixed(0)}%</span>`;
    
    // Update agents list
    const agentsList = document.getElementById('agents-list');
    if (worldState.agents && worldState.agents.length > 0) {
        const sortedAgents = [...worldState.agents]
            .filter(agent => shouldShowAgent(agent, true))
            .sort((a, b) => 
                (b.metrics?.overall_score || 0) - (a.metrics?.overall_score || 0)
            );
        
        if (sortedAgents.length > 0) {
            agentsList.innerHTML = sortedAgents.map(agent => {
                const location = getAgentLocation(agent.label);
                const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
                const score = agent.metrics?.overall_score || 0;
                const specialization = agent.specialization || 'general';
                
                let scoreColor = '#666';
                if (score >= 0.85) scoreColor = '#10b981';
                else if (score >= 0.5) scoreColor = '#0891b2';
                else if (score >= 0.3) scoreColor = '#f59e0b';
                else scoreColor = '#ef4444';
                
                // Build journey information if path exists
                let journeyInfo = '';
                if (agent.path && agent.path.length > 0) {
                    const nextRegion = worldState.regions?.find(r => r.id === agent.path[0]);
                    const nextStop = nextRegion ? nextRegion.label : 'Unknown';
                    journeyInfo = `<div style="margin-top: 6px; padding: 6px; background: rgba(8, 145, 178, 0.1); border-radius: 4px; border-left: 3px solid ${scoreColor};">
                        <div style="font-size: 0.85rem; margin-bottom: 3px;">
                            <strong>🗺️ Active Journey</strong>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">
                            📍 Next: ${nextStop}<br>
                            🎯 ${agent.path.length} stop${agent.path.length > 1 ? 's' : ''} remaining
                        </div>
                    </div>`;
                }
                
                return `
                    <div class="agent-card" onclick="focusAgent('${agent.label}')">
                        <div class="agent-name">${agent.label}</div>
                        <div class="agent-info">
                            🏷️ ${specialization}<br>
                            📍 ${location.city}<br>
                            📊 ${agent.status}<br>
                            ⭐ Score: <span style="color: ${scoreColor}; font-weight: bold;">${(score * 100).toFixed(0)}%</span><br>
                            📈 Resolved: ${agent.metrics?.issues_resolved || 0} | PRs: ${agent.metrics?.prs_merged || 0}<br>
                            ${idea ? `💡 ${idea.title.substring(0, 30)}...` : ''}
                            ${journeyInfo}
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            agentsList.innerHTML = '<p style="color: var(--text-muted);">No agents match filters</p>';
        }
    } else {
        agentsList.innerHTML = '<p style="color: var(--text-muted);">No active agents</p>';
    }
    
    // Update regions list
    const regionsList = document.getElementById('regions-list');
    if (worldState.regions && worldState.regions.length > 0) {
        const sortedRegions = [...worldState.regions].sort((a, b) => 
            (b.idea_count || 0) - (a.idea_count || 0)
        );
        
        regionsList.innerHTML = sortedRegions.slice(0, 10).map(region => `
            <div class="region-item" onclick="focusRegion(${region.lat}, ${region.lng})">
                <div class="region-name">${region.label}</div>
                <div class="region-count">💡 ${region.idea_count || 0} ideas</div>
            </div>
        `).join('');
    } else {
        regionsList.innerHTML = '<p style="color: var(--text-muted);">No regions yet</p>';
    }
    
    // Update infrastructure sidebar section (@integrate-specialist)
    updateInfrastructureSidebar();
}

// Helper functions
function getIdeaById(ideaId) {
    if (!knowledge || !knowledge.ideas) return null;
    return knowledge.ideas.find(i => i.id === ideaId);
}

function focusAgent(agentLabel) {
    const location = getAgentLocation(agentLabel);
    if (map && location) {
        map.setView([location.lat, location.lng], 10);
    }
}

function focusRegion(lat, lng) {
    if (map) {
        map.setView([lat, lng], 8);
    }
}

// Refresh world data
async function refreshWorldData() {
    const button = document.querySelector('.refresh-button');
    button.textContent = '⏳ Loading...';
    button.disabled = true;
    
    const success = await loadWorldData();
    
    if (success) {
        renderAgents();
        updateSidebar();
        button.textContent = '✅ Refreshed!';
        setTimeout(() => {
            button.textContent = '🔄 Refresh Data';
            button.disabled = false;
        }, 2000);
    } else {
        button.textContent = '❌ Error';
        setTimeout(() => {
            button.textContent = '🔄 Refresh Data';
            button.disabled = false;
        }, 2000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    initMap();
    setupSearch(); // Setup search input handler
    
    const success = await loadWorldData();
    if (success) {
        renderAgents();
        updateSidebar();
    } else {
        document.getElementById('agents-list').innerHTML = 
            '<p class="loading">⚠️ Could not load world data. Make sure world_state.json exists.</p>';
    }
});
