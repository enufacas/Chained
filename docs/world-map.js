/**
 * Chained World Map - Real-time visualization of agents and ideas
 */

let map;
let markers = {
    regions: [],
    agents: []
};
let worldState = null;
let knowledge = null;

// Custom marker icons
const agentIcon = L.icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
            <circle cx="20" cy="20" r="18" fill="#0891b2" stroke="#fff" stroke-width="3"/>
            <text x="20" y="28" font-size="20" text-anchor="middle" fill="#fff">🤖</text>
        </svg>
    `),
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40]
});

// Initialize map
function initMap() {
    map = L.map('map').setView([30, 0], 2);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
}

// Load world data
async function loadWorldData() {
    try {
        const stateResponse = await fetch('../world/world_state.json');
        worldState = await stateResponse.json();
        
        const knowledgeResponse = await fetch('../world/knowledge.json');
        knowledge = await knowledgeResponse.json();
        
        return true;
    } catch (error) {
        console.error('Error loading world data:', error);
        return false;
    }
}

// Clear all markers
function clearMarkers() {
    markers.regions.forEach(m => map.removeLayer(m));
    markers.agents.forEach(m => map.removeLayer(m));
    markers.regions = [];
    markers.agents = [];
}

// Render regions on map
function renderRegions() {
    if (!worldState || !worldState.regions) return;
    
    worldState.regions.forEach(region => {
        const ideaCount = region.idea_count || 0;
        
        // Size circle by idea count (min 5000, max 50000)
        const radius = Math.max(5000, Math.min(50000, ideaCount * 10000));
        
        // Color by idea density
        const color = ideaCount > 0 ? '#0891b2' : '#4b5563';
        
        const circle = L.circle([region.lat, region.lng], {
            radius: radius,
            color: color,
            fillColor: color,
            fillOpacity: 0.3,
            weight: 2
        }).addTo(map);
        
        // Create popup content
        const ideas = getIdeasForRegion(region.id);
        let popupContent = `
            <div style="color: #000;">
                <h3 style="margin: 0 0 10px 0;">${region.label}</h3>
                <p><strong>💡 Ideas:</strong> ${ideaCount}</p>
        `;
        
        if (ideas.length > 0) {
            popupContent += '<div style="max-height: 150px; overflow-y: auto; margin-top: 10px;">';
            popupContent += '<strong>Recent Ideas:</strong><ul style="margin: 5px 0; padding-left: 20px;">';
            ideas.slice(0, 5).forEach(idea => {
                popupContent += `<li style="margin: 3px 0; font-size: 0.9em;">${idea.title}</li>`;
            });
            popupContent += '</ul></div>';
        }
        
        popupContent += '</div>';
        circle.bindPopup(popupContent);
        
        markers.regions.push(circle);
    });
}

// Render agents on map
function renderAgents() {
    if (!worldState || !worldState.agents) return;
    
    worldState.agents.forEach(agent => {
        const region = getRegionById(agent.location_region_id);
        if (!region) return;
        
        const marker = L.marker([region.lat, region.lng], {
            icon: agentIcon
        }).addTo(map);
        
        // Create popup content
        const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
        let popupContent = `
            <div style="color: #000;">
                <h3 style="margin: 0 0 10px 0;">🤖 ${agent.label}</h3>
                <p><strong>Location:</strong> ${region.label}</p>
                <p><strong>Status:</strong> ${agent.status}</p>
        `;
        
        if (idea) {
            popupContent += `<p><strong>Exploring:</strong> ${idea.title}</p>`;
        }
        
        if (agent.path && agent.path.length > 0) {
            popupContent += `<p><strong>Path remaining:</strong> ${agent.path.length} stops</p>`;
            popupContent += '<div style="font-size: 0.9em; margin-top: 5px;">Next stops:<ul style="margin: 5px 0; padding-left: 20px;">';
            agent.path.slice(0, 3).forEach(regionId => {
                const r = getRegionById(regionId);
                if (r) popupContent += `<li>${r.label}</li>`;
            });
            if (agent.path.length > 3) {
                popupContent += `<li>...and ${agent.path.length - 3} more</li>`;
            }
            popupContent += '</ul></div>';
        }
        
        popupContent += '</div>';
        marker.bindPopup(popupContent);
        
        markers.agents.push(marker);
    });
}

// Update sidebar
function updateSidebar() {
    if (!worldState) return;
    
    // Update metrics
    document.getElementById('tick-value').textContent = worldState.tick || 0;
    document.getElementById('ideas-value').textContent = worldState.metrics?.total_ideas || 0;
    document.getElementById('regions-value').textContent = worldState.metrics?.total_regions || 0;
    document.getElementById('agents-value').textContent = worldState.agents?.length || 0;
    
    // Update agents list
    const agentsList = document.getElementById('agents-list');
    if (worldState.agents && worldState.agents.length > 0) {
        agentsList.innerHTML = worldState.agents.map(agent => {
            const region = getRegionById(agent.location_region_id);
            const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
            
            return `
                <div class="agent-card">
                    <div class="agent-name">${agent.label}</div>
                    <div class="agent-info">
                        📍 ${region ? region.label : 'Unknown'}<br>
                        📊 ${agent.status}<br>
                        ${idea ? `💡 ${idea.title.substring(0, 40)}...` : ''}
                        ${agent.path && agent.path.length > 0 ? `<br>🗺️ ${agent.path.length} stops remaining` : ''}
                    </div>
                </div>
            `;
        }).join('');
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
            <div class="region-item" onclick="zoomToRegion('${region.id}')">
                <div class="region-name">${region.label}</div>
                <div class="region-count">💡 ${region.idea_count || 0} ideas</div>
            </div>
        `).join('');
    } else {
        regionsList.innerHTML = '<p style="color: var(--text-muted);">No regions yet</p>';
    }
}

// Helper functions
function getRegionById(regionId) {
    if (!worldState || !worldState.regions) return null;
    return worldState.regions.find(r => r.id === regionId);
}

function getIdeaById(ideaId) {
    if (!knowledge || !knowledge.ideas) return null;
    return knowledge.ideas.find(i => i.id === ideaId);
}

function getIdeasForRegion(regionId) {
    if (!knowledge || !knowledge.ideas) return [];
    return knowledge.ideas.filter(idea => 
        idea.inspiration_regions?.some(r => r.region_id === regionId)
    );
}

function zoomToRegion(regionId) {
    const region = getRegionById(regionId);
    if (region) {
        map.setView([region.lat, region.lng], 6);
    }
}

// Refresh world data
async function refreshWorldData() {
    const button = document.querySelector('.refresh-button');
    button.textContent = '⏳ Loading...';
    button.disabled = true;
    
    const success = await loadWorldData();
    
    if (success) {
        clearMarkers();
        renderRegions();
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
    
    const success = await loadWorldData();
    if (success) {
        renderRegions();
        renderAgents();
        updateSidebar();
    } else {
        document.getElementById('agents-list').innerHTML = 
            '<p class="loading">⚠️ Could not load world data. Make sure world_state.json exists.</p>';
    }
});
