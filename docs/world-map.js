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

// Draw simplified continent outlines with more realistic shapes
function drawContinents(svg) {
    const continents = [
        // North America - improved shape
        { 
            path: 'M 80,60 Q 90,50 110,55 L 140,50 Q 160,48 175,55 L 200,60 Q 215,65 220,80 L 225,100 Q 228,120 225,140 L 220,160 Q 215,175 205,185 L 190,195 Q 175,200 160,198 L 140,195 Q 125,192 115,185 L 100,175 Q 85,160 82,145 L 80,120 Q 78,90 80,60 Z', 
            color: '#2d3748' 
        },
        // South America - improved shape  
        { 
            path: 'M 185,200 Q 195,195 205,200 L 220,210 Q 228,220 230,235 L 232,250 Q 233,265 230,280 L 225,295 Q 218,305 208,310 L 195,312 Q 185,310 178,305 L 170,295 Q 165,280 165,265 L 167,245 Q 170,225 175,210 Q 180,200 185,200 Z', 
            color: '#2d3748' 
        },
        // Europe - improved shape
        { 
            path: 'M 380,75 Q 395,70 410,72 L 435,75 Q 455,78 470,85 L 485,95 Q 492,105 490,118 L 485,132 Q 478,142 465,145 L 445,147 Q 425,145 410,140 L 390,132 Q 378,120 376,105 L 375,90 Q 377,80 380,75 Z', 
            color: '#2d3748' 
        },
        // Africa - improved shape
        { 
            path: 'M 385,145 Q 395,142 410,145 L 430,150 Q 445,155 455,165 L 465,180 Q 470,195 470,210 L 468,230 Q 465,245 458,258 L 448,270 Q 435,278 420,280 L 405,278 Q 390,272 382,262 L 375,245 Q 372,225 375,205 L 380,185 Q 383,165 385,145 Z', 
            color: '#2d3748' 
        },
        // Asia - improved larger shape
        { 
            path: 'M 475,60 Q 495,55 520,58 L 555,62 Q 585,65 610,70 L 640,78 Q 665,88 685,102 L 705,120 Q 718,138 720,158 L 718,178 Q 712,195 698,208 L 675,220 Q 650,228 625,230 L 595,228 Q 565,223 540,215 L 515,205 Q 495,192 485,175 L 478,155 Q 475,135 475,115 L 475,90 Q 475,70 475,60 Z', 
            color: '#2d3748' 
        },
        // Australia - improved shape
        { 
            path: 'M 620,265 Q 635,262 650,265 L 675,270 Q 695,275 708,285 L 715,300 Q 717,312 710,322 L 698,330 Q 680,333 665,332 L 645,328 Q 630,320 622,308 L 618,290 Q 618,275 620,265 Z', 
            color: '#2d3748' 
        },
        // Antarctica - add bottom continent
        { 
            path: 'M 50,360 L 750,360 Q 745,370 735,375 L 700,380 Q 650,382 600,380 L 500,378 Q 400,380 300,378 L 200,380 Q 150,382 100,378 L 65,373 Q 55,368 50,360 Z', 
            color: '#2d3748' 
        }
    ];
    
    continents.forEach(continent => {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', continent.path);
        path.setAttribute('fill', continent.color);
        path.setAttribute('stroke', '#1a2332');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('opacity', '0.8');
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
    
    const lines = [
        { text: region.label, size: '14', bold: true },
        { text: `💡 Ideas: ${region.idea_count || 0}`, size: '12' }
    ];
    
    if (ideas.length > 0) {
        lines.push({ text: 'Recent Ideas:', size: '11', bold: true });
        ideas.slice(0, 3).forEach((idea, i) => {
            const title = idea.title.length > 30 ? idea.title.substring(0, 30) + '...' : idea.title;
            lines.push({ text: `• ${title}`, size: '10', indent: 15 });
        });
    }
    
    createPopup(svg, pos.x, pos.y, lines);
}

// Show agent popup
function showAgentPopup(agent, region, pos) {
    hidePopup();
    
    const svg = document.querySelector('#map svg');
    if (!svg) return;
    
    const idea = agent.current_idea_id ? getIdeaById(agent.current_idea_id) : null;
    const score = agent.metrics?.overall_score || 0;
    const specialization = agent.specialization || 'general';
    
    // Determine score color
    let scoreColor = '#666';
    if (score >= 0.85) scoreColor = '#10b981'; // green
    else if (score >= 0.5) scoreColor = '#0891b2'; // cyan
    else if (score >= 0.3) scoreColor = '#f59e0b'; // amber
    else scoreColor = '#ef4444'; // red
    
    const lines = [
        { text: `🤖 ${agent.label}`, size: '14', bold: true },
        { text: `🏷️ ${specialization}`, size: '11' },
        { text: `📍 ${region.label}`, size: '11' },
        { text: `📊 ${agent.status}`, size: '11' },
        { text: `⭐ Score: ${(score * 100).toFixed(0)}%`, size: '11', color: scoreColor },
        { text: `📈 ${agent.metrics?.issues_resolved || 0} issues | ${agent.metrics?.prs_merged || 0} PRs`, size: '10' }
    ];
    
    if (idea) {
        const title = idea.title.length > 28 ? idea.title.substring(0, 28) + '...' : idea.title;
        lines.push({ text: `💡 ${title}`, size: '10' });
    }
    
    if (agent.path && agent.path.length > 0) {
        lines.push({ text: `🗺️ ${agent.path.length} stops remaining`, size: '10' });
    }
    
    createPopup(svg, pos.x, pos.y, lines);
}

// Create popup with better positioning and formatting
function createPopup(svg, x, y, lines) {
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.classList.add('popup-group');
    
    // Adjust position to keep popup in view
    const viewBox = svg.viewBox.baseVal;
    const popupWidth = 240;
    const popupHeight = Math.max(120, lines.length * 20 + 40); // Dynamic height based on content
    
    // Calculate popup position to stay within bounds
    let popupX = x - popupWidth / 2;
    let popupY = y - popupHeight - 20; // Position above the marker
    
    // Keep popup within SVG bounds
    if (popupX < 10) popupX = 10;
    if (popupX + popupWidth > viewBox.width - 10) popupX = viewBox.width - popupWidth - 10;
    if (popupY < 10) popupY = y + 30; // If no room above, show below
    
    // Background
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('x', popupX);
    bg.setAttribute('y', popupY);
    bg.setAttribute('width', popupWidth);
    bg.setAttribute('height', popupHeight);
    bg.setAttribute('rx', '8');
    bg.setAttribute('fill', 'white');
    bg.setAttribute('stroke', '#0891b2');
    bg.setAttribute('stroke-width', '2');
    bg.setAttribute('filter', 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))');
    group.appendChild(bg);
    
    // Close button
    const closeBtn = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    closeBtn.setAttribute('x', popupX + popupWidth - 20);
    closeBtn.setAttribute('y', popupY + 20);
    closeBtn.setAttribute('font-size', '16');
    closeBtn.setAttribute('fill', '#666');
    closeBtn.setAttribute('cursor', 'pointer');
    closeBtn.setAttribute('font-weight', 'bold');
    closeBtn.textContent = '✖';
    closeBtn.addEventListener('click', hidePopup);
    group.appendChild(closeBtn);
    
    // Content - create text element with tspan children
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', popupX + 10);
    text.setAttribute('y', popupY + 25);
    text.setAttribute('fill', '#000');
    
    // Add each line as a tspan element
    lines.forEach((line, index) => {
        const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
        tspan.setAttribute('x', popupX + (line.indent || 10));
        tspan.setAttribute('dy', index === 0 ? '0' : '1.4em');
        tspan.setAttribute('font-size', line.size || '11');
        if (line.bold) tspan.setAttribute('font-weight', 'bold');
        if (line.color) tspan.setAttribute('fill', line.color);
        tspan.textContent = line.text;
        text.appendChild(tspan);
    });
    
    group.appendChild(text);
    
    // Pointer triangle pointing to the marker
    const pointerY = popupY + popupHeight;
    const pointer = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    
    // Point to the marker position
    if (popupY < y) {
        // Popup is above marker - pointer points down
        pointer.setAttribute('points', `${x},${y} ${x - 10},${pointerY} ${x + 10},${pointerY}`);
    } else {
        // Popup is below marker - pointer points up
        pointer.setAttribute('points', `${x},${y} ${x - 10},${popupY} ${x + 10},${popupY}`);
    }
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
