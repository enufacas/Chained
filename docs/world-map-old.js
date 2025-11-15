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

// Draw world map using a more realistic approach with better geographic accuracy
function drawContinents(svg) {
    // Using a simplified but more accurate world map projection
    // Based on equirectangular projection with better continent shapes
    const continents = [
        // North America - more accurate coastline
        { 
            path: 'M 50,80 L 60,65 L 75,58 L 95,55 L 115,52 L 135,50 L 155,52 L 170,55 L 185,60 L 195,68 L 205,78 L 212,90 L 218,105 L 220,120 L 220,135 L 218,150 L 214,165 L 208,178 L 200,188 L 190,196 L 178,202 L 165,206 L 150,208 L 135,207 L 120,204 L 108,199 L 98,192 L 88,183 L 80,172 L 72,158 L 66,142 L 62,125 L 58,108 L 56,92 Z M 70,70 L 80,75 L 88,82 L 92,90 L 90,98 L 85,92 L 78,85 Z',
            color: '#34495e'
        },
        // Greenland
        {
            path: 'M 230,40 L 245,38 L 258,40 L 268,45 L 273,52 L 275,62 L 273,72 L 268,80 L 260,85 L 248,88 L 238,87 L 228,82 L 222,74 L 220,64 L 222,54 Z',
            color: '#34495e'
        },
        // South America - more detailed
        { 
            path: 'M 185,205 L 195,202 L 207,203 L 218,207 L 227,214 L 234,224 L 238,236 L 240,250 L 240,265 L 238,280 L 234,293 L 228,304 L 220,312 L 210,318 L 198,320 L 186,319 L 176,315 L 168,308 L 162,298 L 158,286 L 156,272 L 156,258 L 158,244 L 162,230 L 168,218 L 176,210 Z',
            color: '#34495e'
        },
        // Europe - better detail
        { 
            path: 'M 375,70 L 388,68 L 402,68 L 415,70 L 428,73 L 440,77 L 452,82 L 463,88 L 472,96 L 478,106 L 481,117 L 481,128 L 478,138 L 472,146 L 463,152 L 452,156 L 440,158 L 428,158 L 415,156 L 402,152 L 390,146 L 380,138 L 372,128 L 368,117 L 367,106 L 369,95 L 372,84 Z M 410,72 L 420,75 L 428,80 L 432,87 L 430,94 L 424,90 L 416,84 Z',
            color: '#34495e'
        },
        // Africa - more realistic shape
        { 
            path: 'M 380,140 L 393,138 L 407,139 L 420,142 L 432,147 L 443,154 L 453,163 L 461,174 L 467,187 L 470,201 L 471,216 L 470,231 L 467,246 L 461,260 L 453,272 L 443,282 L 432,289 L 420,293 L 407,294 L 393,292 L 382,287 L 373,280 L 366,270 L 361,258 L 358,244 L 357,229 L 358,214 L 361,199 L 366,185 L 373,172 L 377,160 Z',
            color: '#34495e'
        },
        // Asia - much larger and more detailed
        { 
            path: 'M 470,55 L 490,52 L 512,51 L 535,52 L 558,55 L 580,60 L 602,66 L 623,74 L 643,84 L 661,96 L 677,110 L 690,126 L 700,143 L 707,161 L 710,180 L 710,199 L 707,217 L 700,233 L 690,247 L 677,258 L 661,266 L 643,271 L 623,274 L 602,274 L 580,271 L 558,266 L 535,258 L 512,247 L 490,233 L 473,217 L 462,199 L 456,180 L 453,161 L 453,143 L 456,126 L 462,110 L 468,96 Z M 720,90 L 735,88 L 745,92 L 748,102 L 743,110 L 732,108 Z M 485,60 L 495,65 L 502,72 L 505,82 L 502,90 L 495,85 L 488,78 Z',
            color: '#34495e'
        },
        // Australia - better proportions
        { 
            path: 'M 620,260 L 638,258 L 655,260 L 671,265 L 686,272 L 698,281 L 707,292 L 712,305 L 713,318 L 710,330 L 703,339 L 693,345 L 680,348 L 665,348 L 650,345 L 636,339 L 624,330 L 616,318 L 612,305 L 611,292 L 613,279 Z',
            color: '#34495e'
        },
        // Antarctica - bottom of map
        { 
            path: 'M 30,355 L 770,355 L 768,365 L 760,373 L 745,378 L 720,381 L 680,383 L 630,384 L 570,383 L 500,382 L 430,383 L 370,384 L 320,383 L 280,381 L 255,378 L 240,373 L 232,365 Z',
            color: '#34495e'
        },
        // Southeast Asia / Indonesia
        {
            path: 'M 630,210 L 640,209 L 650,211 L 658,215 L 663,221 L 665,228 L 663,235 L 658,240 L 650,243 L 640,243 L 632,240 L 626,235 L 624,228 L 626,221 Z M 670,215 L 678,214 L 685,217 L 688,223 L 686,229 L 680,231 L 673,229 Z',
            color: '#34495e'
        },
        // Japan
        {
            path: 'M 735,125 L 742,123 L 748,125 L 752,130 L 752,137 L 748,143 L 742,145 L 735,143 L 731,137 L 731,130 Z',
            color: '#34495e'
        },
        // New Zealand
        {
            path: 'M 755,310 L 762,309 L 768,312 L 770,318 L 768,325 L 762,328 L 755,327 L 751,323 L 750,318 Z M 758,330 L 764,329 L 768,332 L 769,338 L 766,343 L 761,344 L 756,342 L 754,337 Z',
            color: '#34495e'
        },
        // Iceland
        {
            path: 'M 335,50 L 343,49 L 349,52 L 351,58 L 349,64 L 343,66 L 335,65 L 331,61 L 330,55 Z',
            color: '#34495e'
        },
        // UK and Ireland
        {
            path: 'M 360,85 L 365,84 L 370,86 L 372,91 L 370,96 L 365,98 L 360,97 L 357,93 Z M 352,88 L 356,87 L 359,90 L 358,94 L 355,96 L 351,95 L 349,91 Z',
            color: '#34495e'
        },
        // Madagascar
        {
            path: 'M 485,265 L 490,264 L 494,267 L 495,273 L 494,280 L 490,285 L 485,286 L 481,283 L 480,277 L 481,271 Z',
            color: '#34495e'
        }
    ];
    
    // Draw ocean/water background first
    const oceanRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    oceanRect.setAttribute('x', '0');
    oceanRect.setAttribute('y', '0');
    oceanRect.setAttribute('width', '800');
    oceanRect.setAttribute('height', '400');
    oceanRect.setAttribute('fill', '#1a2838');
    svg.appendChild(oceanRect);
    
    // Draw grid lines for latitude/longitude reference
    for (let i = 50; i < 800; i += 80) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', i);
        line.setAttribute('y1', '0');
        line.setAttribute('x2', i);
        line.setAttribute('y2', '400');
        line.setAttribute('stroke', '#2d3748');
        line.setAttribute('stroke-width', '1');
        line.setAttribute('opacity', '0.3');
        svg.appendChild(line);
    }
    
    for (let i = 50; i < 400; i += 50) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', '0');
        line.setAttribute('y1', i);
        line.setAttribute('x2', '800');
        line.setAttribute('y2', i);
        line.setAttribute('stroke', '#2d3748');
        line.setAttribute('stroke-width', '1');
        line.setAttribute('opacity', '0.3');
        svg.appendChild(line);
    }
    
    // Draw continents with better styling
    continents.forEach(continent => {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', continent.path);
        path.setAttribute('fill', continent.color);
        path.setAttribute('stroke', '#4a5568');
        path.setAttribute('stroke-width', '1.5');
        path.setAttribute('opacity', '0.95');
        // Add subtle shadow effect
        path.setAttribute('filter', 'drop-shadow(2px 2px 3px rgba(0,0,0,0.4))');
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
