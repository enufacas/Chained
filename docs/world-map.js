/**
 * Chained World Map - Simplified self-contained version
 * Using simple SVG-based visualization (no external dependencies)
 */

let worldState = null;
let knowledge = null;
let selectedFeature = null;

// Map projection helpers (simple Mercator-like)
function projectLonLat(lon, lat) {
    // Simple equirectangular projection
    const x = (lon + 180) * (800 / 360);
    const y = (90 - lat) * (400 / 180);
    return { x, y };
}

// Initialize simple SVG map
function initMap() {
    const mapDiv = document.getElementById('map');
    
    // Create SVG element
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.setAttribute('viewBox', '0 0 800 400');
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.style.background = '#1a2332';
    svg.style.borderRadius = '12px';
    
    // Create world outline (simple rectangle with grid)
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const pattern = document.createElementNS('http://www.w3.org/2000/svg', 'pattern');
    pattern.setAttribute('id', 'grid');
    pattern.setAttribute('width', '40');
    pattern.setAttribute('height', '40');
    pattern.setAttribute('patternUnits', 'userSpaceOnUse');
    
    const line1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line1.setAttribute('x1', '40');
    line1.setAttribute('y1', '0');
    line1.setAttribute('x2', '40');
    line1.setAttribute('y2', '40');
    line1.setAttribute('stroke', 'rgba(255,255,255,0.1)');
    line1.setAttribute('stroke-width', '1');
    
    const line2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line2.setAttribute('x1', '0');
    line2.setAttribute('y1', '40');
    line2.setAttribute('x2', '40');
    line2.setAttribute('y2', '40');
    line2.setAttribute('stroke', 'rgba(255,255,255,0.1)');
    line2.setAttribute('stroke-width', '1');
    
    pattern.appendChild(line1);
    pattern.appendChild(line2);
    defs.appendChild(pattern);
    svg.appendChild(defs);
    
    // Background
    const background = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    background.setAttribute('width', '800');
    background.setAttribute('height', '400');
    background.setAttribute('fill', 'url(#grid)');
    svg.appendChild(background);
    
    // Add continents (simplified shapes)
    drawContinents(svg);
    
    // Store SVG for later use
    mapDiv.innerHTML = '';
    mapDiv.appendChild(svg);
    
    return true;
}

// Draw simplified continent outlines
function drawContinents(svg) {
    const continents = [
        // North America
        { path: 'M 100,100 L 120,90 L 180,95 L 200,110 L 210,150 L 190,170 L 150,175 L 120,160 Z', color: '#2d3748' },
        // South America
        { path: 'M 200,210 L 215,200 L 230,220 L 235,270 L 215,285 L 205,275 L 195,240 Z', color: '#2d3748' },
        // Europe
        { path: 'M 380,90 L 420,85 L 450,100 L 440,130 L 400,135 L 375,120 Z', color: '#2d3748' },
        // Africa
        { path: 'M 390,150 L 420,145 L 450,180 L 455,240 L 430,260 L 400,250 L 385,200 Z', color: '#2d3748' },
        // Asia
        { path: 'M 470,80 L 580,75 L 650,90 L 680,130 L 700,160 L 680,190 L 620,200 L 550,180 L 480,150 L 455,120 Z', color: '#2d3748' },
        // Australia
        { path: 'M 630,270 L 680,265 L 710,285 L 700,310 L 660,315 L 625,295 Z', color: '#2d3748' }
    ];
    
    continents.forEach(continent => {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', continent.path);
        path.setAttribute('fill', continent.color);
        path.setAttribute('stroke', '#1a2332');
        path.setAttribute('stroke-width', '2');
        svg.appendChild(path);
    });
}

// Load world data
async function loadWorldData() {
    try {
        const stateResponse = await fetch('./world/world_state.json');
        worldState = await stateResponse.json();
        
        const knowledgeResponse = await fetch('./world/knowledge.json');
        knowledge = await knowledgeResponse.json();
        
        return true;
    } catch (error) {
        console.error('Error loading world data:', error);
        return false;
    }
}

// Clear all map features
function clearMapFeatures() {
    const svg = document.querySelector('#map svg');
    if (!svg) return;
    
    // Remove all circles and markers (keep background and continents)
    const elements = svg.querySelectorAll('.region-circle, .agent-marker, .popup-group');
    elements.forEach(el => el.remove());
}

// Render regions on map
function renderRegions() {
    if (!worldState || !worldState.regions) return;
    
    const svg = document.querySelector('#map svg');
    if (!svg) return;
    
    worldState.regions.forEach(region => {
        const ideaCount = region.idea_count || 0;
        const pos = projectLonLat(region.lng, region.lat);
        
        // Size circle by idea count
        const radius = Math.max(3, Math.min(30, ideaCount * 5 + 5));
        
        // Color by idea density
        const color = ideaCount > 0 ? '#0891b2' : '#4b5563';
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', pos.x);
        circle.setAttribute('cy', pos.y);
        circle.setAttribute('r', radius);
        circle.setAttribute('fill', color);
        circle.setAttribute('fill-opacity', '0.4');
        circle.setAttribute('stroke', color);
        circle.setAttribute('stroke-width', '2');
        circle.classList.add('region-circle');
        circle.style.cursor = 'pointer';
        
        // Add click handler
        circle.addEventListener('click', () => showRegionPopup(region, pos));
        circle.addEventListener('mouseenter', function() {
            this.setAttribute('fill-opacity', '0.6');
        });
        circle.addEventListener('mouseleave', function() {
            this.setAttribute('fill-opacity', '0.4');
        });
        
        svg.appendChild(circle);
    });
}

// Render agents on map
function renderAgents() {
    if (!worldState || !worldState.agents) return;
    
    const svg = document.querySelector('#map svg');
    if (!svg) return;
    
    worldState.agents.forEach(agent => {
        const region = getRegionById(agent.location_region_id);
        if (!region) return;
        
        const pos = projectLonLat(region.lng, region.lat);
        
        // Create agent marker group
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.classList.add('agent-marker');
        group.style.cursor = 'pointer';
        
        // Background circle
        const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        bgCircle.setAttribute('cx', pos.x);
        bgCircle.setAttribute('cy', pos.y);
        bgCircle.setAttribute('r', '12');
        bgCircle.setAttribute('fill', '#0891b2');
        bgCircle.setAttribute('stroke', '#fff');
        bgCircle.setAttribute('stroke-width', '2');
        group.appendChild(bgCircle);
        
        // Robot emoji as text
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pos.x);
        text.setAttribute('y', pos.y + 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '16');
        text.textContent = '🤖';
        group.appendChild(text);
        
        // Add click handler
        group.addEventListener('click', () => showAgentPopup(agent, region, pos));
        group.addEventListener('mouseenter', function() {
            bgCircle.setAttribute('r', '14');
        });
        group.addEventListener('mouseleave', function() {
            bgCircle.setAttribute('r', '12');
        });
        
        svg.appendChild(group);
    });
}

// Show region popup
function showRegionPopup(region, pos) {
    hidePopup();
    
    const svg = document.querySelector('#map svg');
    if (!svg) return;
    
    const ideas = getIdeasForRegion(region.id);
    
    let content = `<tspan x="10" dy="1.2em" font-weight="bold" font-size="14">${region.label}</tspan>`;
    content += `<tspan x="10" dy="1.4em" font-size="12">💡 Ideas: ${region.idea_count || 0}</tspan>`;
    
    if (ideas.length > 0) {
        content += `<tspan x="10" dy="1.4em" font-size="11" font-weight="bold">Recent Ideas:</tspan>`;
        ideas.slice(0, 3).forEach((idea, i) => {
            const title = idea.title.length > 30 ? idea.title.substring(0, 30) + '...' : idea.title;
            content += `<tspan x="15" dy="1.3em" font-size="10">• ${title}</tspan>`;
        });
    }
    
    createPopup(svg, pos.x, pos.y, content);
}

// Show agent popup
function showAgentPopup(agent, region, pos) {
    hidePopup();
    
    const svg = document.querySelector('#map svg');
    if (!svg) return;
    
    const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
    const score = agent.metrics?.overall_score || 0;
    const specialization = agent.specialization || 'general';
    
    let content = `<tspan x="10" dy="1.2em" font-weight="bold" font-size="14">🤖 ${agent.label}</tspan>`;
    content += `<tspan x="10" dy="1.4em" font-size="11">🏷️ ${specialization}</tspan>`;
    content += `<tspan x="10" dy="1.3em" font-size="12">📍 ${region.label}</tspan>`;
    content += `<tspan x="10" dy="1.3em" font-size="12">📊 ${agent.status}</tspan>`;
    content += `<tspan x="10" dy="1.3em" font-size="11">⭐ Score: ${(score * 100).toFixed(0)}%</tspan>`;
    content += `<tspan x="10" dy="1.3em" font-size="10">📈 ${agent.metrics?.issues_resolved || 0} issues | ${agent.metrics?.prs_merged || 0} PRs</tspan>`;
    
    if (idea) {
        const title = idea.title.length > 25 ? idea.title.substring(0, 25) + '...' : idea.title;
        content += `<tspan x="10" dy="1.3em" font-size="11">💡 ${title}</tspan>`;
    }
    
    if (agent.path && agent.path.length > 0) {
        content += `<tspan x="10" dy="1.3em" font-size="11">🗺️ ${agent.path.length} stops remaining</tspan>`;
    }
    
    createPopup(svg, pos.x, pos.y, content);
}

// Create popup
function createPopup(svg, x, y, content) {
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.classList.add('popup-group');
    
    // Background - increased height for more content
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('x', x - 110);
    bg.setAttribute('y', y - 180);
    bg.setAttribute('width', '220');
    bg.setAttribute('height', '170');
    bg.setAttribute('rx', '8');
    bg.setAttribute('fill', 'white');
    bg.setAttribute('stroke', '#0891b2');
    bg.setAttribute('stroke-width', '2');
    bg.setAttribute('filter', 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))');
    group.appendChild(bg);
    
    // Close button
    const closeBtn = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    closeBtn.setAttribute('x', x + 95);
    closeBtn.setAttribute('y', y - 160);
    closeBtn.setAttribute('font-size', '18');
    closeBtn.setAttribute('fill', '#666');
    closeBtn.setAttribute('cursor', 'pointer');
    closeBtn.textContent = '✖';
    closeBtn.addEventListener('click', hidePopup);
    group.appendChild(closeBtn);
    
    // Content
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', x - 100);
    text.setAttribute('y', y - 175);
    text.setAttribute('fill', '#000');
    text.innerHTML = content;
    group.appendChild(text);
    
    // Pointer
    const pointer = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    pointer.setAttribute('points', `${x},${y - 10} ${x - 8},${y - 18} ${x + 8},${y - 18}`);
    pointer.setAttribute('fill', 'white');
    pointer.setAttribute('stroke', '#0891b2');
    pointer.setAttribute('stroke-width', '2');
    group.appendChild(pointer);
    
    svg.appendChild(group);
}

// Hide popup
function hidePopup() {
    const popups = document.querySelectorAll('.popup-group');
    popups.forEach(p => p.remove());
}

// Update sidebar
function updateSidebar() {
    if (!worldState) return;
    
    // Update metrics
    document.getElementById('tick-value').textContent = worldState.tick || 0;
    document.getElementById('ideas-value').textContent = worldState.metrics?.total_ideas || 0;
    document.getElementById('regions-value').textContent = worldState.metrics?.total_regions || 0;
    document.getElementById('agents-value').textContent = worldState.agents?.length || 0;
    document.getElementById('hof-value').textContent = worldState.metrics?.hall_of_fame_count || 0;
    
    // Update scoring thresholds with color coding
    const promotionThreshold = worldState.metrics?.promotion_threshold || 0.85;
    const eliminationThreshold = worldState.metrics?.elimination_threshold || 0.3;
    document.getElementById('promotion-threshold').innerHTML = 
        `<span style="color: #10b981;">${(promotionThreshold * 100).toFixed(0)}%</span>`;
    document.getElementById('elimination-threshold').innerHTML = 
        `<span style="color: #ef4444;">${(eliminationThreshold * 100).toFixed(0)}%</span>`;
    
    // Update agents list
    const agentsList = document.getElementById('agents-list');
    if (worldState.agents && worldState.agents.length > 0) {
        // Sort by overall score descending
        const sortedAgents = [...worldState.agents].sort((a, b) => 
            (b.metrics?.overall_score || 0) - (a.metrics?.overall_score || 0)
        );
        
        agentsList.innerHTML = sortedAgents.map(agent => {
            const region = getRegionById(agent.location_region_id);
            const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
            const score = agent.metrics?.overall_score || 0;
            const specialization = agent.specialization || 'general';
            
            // Color code by score
            let scoreColor = '#666';
            if (score >= 0.85) scoreColor = '#10b981'; // green for hall of fame
            else if (score >= 0.5) scoreColor = '#0891b2'; // cyan for good
            else if (score >= 0.3) scoreColor = '#f59e0b'; // amber for ok
            else scoreColor = '#ef4444'; // red for at risk
            
            return `
                <div class="agent-card">
                    <div class="agent-name">${agent.label}</div>
                    <div class="agent-info">
                        🏷️ ${specialization}<br>
                        📍 ${region ? region.label : 'Unknown'}<br>
                        📊 ${agent.status}<br>
                        ⭐ Score: <span style="color: ${scoreColor}; font-weight: bold;">${(score * 100).toFixed(0)}%</span><br>
                        📈 Resolved: ${agent.metrics?.issues_resolved || 0} | PRs: ${agent.metrics?.prs_merged || 0}<br>
                        ${idea ? `💡 ${idea.title.substring(0, 30)}...` : ''}
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
    if (!region) return;
    
    // Highlight the region briefly
    const svg = document.querySelector('#map svg');
    if (!svg) return;
    
    const circles = svg.querySelectorAll('.region-circle');
    circles.forEach(circle => {
        const cx = parseFloat(circle.getAttribute('cx'));
        const cy = parseFloat(circle.getAttribute('cy'));
        const pos = projectLonLat(region.lng, region.lat);
        
        if (Math.abs(cx - pos.x) < 1 && Math.abs(cy - pos.y) < 1) {
            circle.setAttribute('stroke-width', '4');
            circle.setAttribute('fill-opacity', '0.8');
            setTimeout(() => {
                circle.setAttribute('stroke-width', '2');
                circle.setAttribute('fill-opacity', '0.4');
            }, 1000);
        }
    });
}

// Refresh world data
async function refreshWorldData() {
    const button = document.querySelector('.refresh-button');
    button.textContent = '⏳ Loading...';
    button.disabled = true;
    
    const success = await loadWorldData();
    
    if (success) {
        clearMapFeatures();
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
