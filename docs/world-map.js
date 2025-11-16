/**
 * Chained World Map - Leaflet Implementation
 * Real-time Agent Explorer with Interactive Mapping
 * @investigate-champion implementation
 */

let map = null;
let worldState = null;
let knowledge = null;
let agentMarkers = null;
let agentLocations = {}; // Map agent names to locations
let allMarkers = []; // Store all marker references for filtering
let searchQuery = ''; // Current search query
let showActive = true; // Filter: show active agents
let showInactive = true; // Filter: show inactive agents

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
    
    map.addLayer(agentMarkers);
    
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
    // PRIORITY 1: Check if agent has location in world state (source of truth)
    if (worldState && worldState.agents && worldState.regions) {
        const agent = worldState.agents.find(a => a.label === agentLabel);
        if (agent && agent.location_region_id) {
            const region = worldState.regions.find(r => r.id === agent.location_region_id);
            if (region) {
                return {
                    lat: region.lat,
                    lng: region.lng,
                    city: region.label,
                    region_id: region.id
                };
            }
        }
    }
    
    // PRIORITY 2: Fall back to default locations for inactive agents
    const agentKey = findAgentKey(agentLabel);
    if (agentKey && DEFAULT_AGENT_LOCATIONS[agentKey]) {
        return DEFAULT_AGENT_LOCATIONS[agentKey];
    }
    
    // PRIORITY 3: Default to Charlotte, NC if no location found
    return { lat: 35.2271, lng: -80.8431, city: 'Charlotte, NC' };
}

// Find agent key from label (fuzzy matching)
function findAgentKey(label) {
    // Extract meaningful words from label
    const labelLower = label.toLowerCase();
    
    // Direct mapping for known patterns
    const nameMap = {
        'robert martin': 'organize-guru',
        'tesla': 'create-guru',
        'turing': 'meta-coordinator',
        'liskov': 'coach-master',
        'moxie marlinspike': 'secure-ninja',
        'linus torvalds': 'construct-specialist',
        'ada': 'investigate-champion',
        'einstein': 'pioneer-sage',
        'martin fowler': 'organize-specialist',
        'steam machine': 'steam-machine'
    };
    
    // Check direct mappings
    for (const [key, value] of Object.entries(nameMap)) {
        if (labelLower.includes(key)) {
            return value;
        }
    }
    
    // Try to match by emoji or keywords
    if (labelLower.includes('🧹') || labelLower.includes('clean')) return 'organize-guru';
    if (labelLower.includes('🧪') || labelLower.includes('test')) return 'assert-specialist';
    if (labelLower.includes('💭') || labelLower.includes('think')) return 'meta-coordinator';
    if (labelLower.includes('🎯') || labelLower.includes('target')) return 'investigate-champion';
    if (labelLower.includes('🔒') || labelLower.includes('secur')) return 'secure-specialist';
    if (labelLower.includes('🔨') || labelLower.includes('build')) return 'construct-specialist';
    if (labelLower.includes('⚙️') || labelLower.includes('engineer')) return 'engineer-master';
    if (labelLower.includes('📖') || labelLower.includes('document')) return 'document-ninja';
    
    return null;
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

// Layer groups for different visualizations
let pathLayers = null;
let regionLayers = null;

// Filter and search functions
function applyFilters() {
    showActive = document.getElementById('filter-active').checked;
    showInactive = document.getElementById('filter-inactive').checked;
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

function shouldShowAgent(agent, isActive) {
    // Check search filter
    if (!matchesSearch(agent.label || agent)) return false;
    
    // Check active/inactive filter
    if (isActive && !showActive) return false;
    if (!isActive && !showInactive) return false;
    
    return true;
}

// Render all agents on map
function renderAgents() {
    if (!worldState || !worldState.agents || !map) return;
    
    // Clear existing markers
    agentMarkers.clearLayers();
    
    // Clear and recreate path layers
    if (pathLayers) {
        map.removeLayer(pathLayers);
    }
    pathLayers = L.layerGroup().addTo(map);
    
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
        
        // Create popup content
        const score = agent.metrics?.overall_score || 0;
        const specialization = agent.specialization || 'general';
        const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
        
        const popupContent = `
            <div style="min-width: 200px;">
                <h3 style="margin: 0 0 8px 0; color: #0891b2; font-size: 16px;">🤖 ${agent.label}</h3>
                <p style="margin: 4px 0; font-size: 13px;"><strong>🏷️ Specialization:</strong> ${specialization}</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>📍 Location:</strong> ${location.city}</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>📊 Status:</strong> ${agent.status}</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>⭐ Score:</strong> ${(score * 100).toFixed(0)}%</p>
                <p style="margin: 4px 0; font-size: 13px;"><strong>📈 Metrics:</strong> ${agent.metrics?.issues_resolved || 0} issues | ${agent.metrics?.prs_merged || 0} PRs</p>
                ${idea ? `<p style="margin: 4px 0; font-size: 13px;"><strong>💡 Current Idea:</strong> ${idea.title}</p>` : ''}
                ${agent.path && agent.path.length > 0 ? `<p style="margin: 4px 0; font-size: 13px;"><strong>🗺️ Journey:</strong> ${agent.path.length} stops remaining</p>` : ''}
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
    
    pathLayers.addLayer(polyline);
    
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
            
            pathLayers.addLayer(waypointMarker);
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
        
        pathLayers.addLayer(destinationMarker);
    }
}

// Render regions with idea counts and enhanced metadata
function renderRegions() {
    if (!worldState || !worldState.regions) return;
    
    // Clear and recreate region layers
    if (regionLayers) {
        map.removeLayer(regionLayers);
    }
    regionLayers = L.layerGroup().addTo(map);
    
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
        regionLayers.addLayer(circle);
        
        // Add label for significant regions or home base
        if (activityScore > 5 || region.is_home_base) {
            const label = L.marker([region.lat, region.lng], {
                icon: L.divIcon({
                    html: `<div style="background: ${circleColor}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${regionIcon} ${region.label}</div>`,
                    className: 'region-label',
                    iconSize: null
                })
            });
            regionLayers.addLayer(label);
        }
    });
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
