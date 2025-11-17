// AI Knowledge Graph Visualization using D3.js
// Enhanced by @guide-wizard to include Mission Reports

// ============================================================================
// MISSION REPORTS FUNCTIONALITY - by @guide-wizard
// ============================================================================

/**
 * Load and display mission reports from the investigation-reports directory
 * Organized by category for easy navigation and discovery
 */
async function loadMissionReports() {
    try {
        console.log('Loading mission reports data...');
        const response = await fetch('data/mission-reports.json');
        
        if (!response.ok) {
            throw new Error(`Failed to load mission reports: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Mission reports loaded:', data);
        
        // Update statistics
        document.getElementById('total-missions-count').textContent = data.total_missions;
        
        // Count completed missions
        let completedCount = 0;
        Object.values(data.categories).forEach(category => {
            category.missions.forEach(mission => {
                if (mission.status === 'complete') completedCount++;
            });
        });
        document.getElementById('completed-missions-count').textContent = completedCount;
        
        // Count categories with missions
        const categoriesWithMissions = Object.values(data.categories).filter(cat => cat.missions.length > 0).length;
        document.getElementById('categories-count').textContent = categoriesWithMissions;
        
        // Render mission categories
        renderMissionCategories(data.categories);
        
    } catch (error) {
        console.error('Error loading mission reports:', error);
        const container = document.getElementById('mission-categories-container');
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--text-muted, #666);">
                <p style="font-size: 18px; margin-bottom: 10px;">⚠️ Unable to load mission reports</p>
                <p style="font-size: 14px;">Error: ${error.message}</p>
            </div>
        `;
    }
}

/**
 * Render mission reports organized by category
 * Each category displays its missions in a grid layout
 */
function renderMissionCategories(categories) {
    const container = document.getElementById('mission-categories-container');
    container.innerHTML = '';
    
    // Sort categories by number of missions (descending)
    const sortedCategories = Object.entries(categories)
        .filter(([_, cat]) => cat.missions.length > 0)
        .sort((a, b) => b[1].missions.length - a[1].missions.length);
    
    sortedCategories.forEach(([categoryKey, category]) => {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'mission-category';
        categoryDiv.id = `category-${categoryKey}`;
        
        // Category header
        const header = document.createElement('h3');
        header.innerHTML = `
            ${category.name}
            <span class="mission-count">${category.missions.length}</span>
        `;
        categoryDiv.appendChild(header);
        
        // Mission grid
        const grid = document.createElement('div');
        grid.className = 'mission-grid';
        
        // Sort missions by date (newest first) and status (complete first)
        const sortedMissions = [...category.missions].sort((a, b) => {
            // Completed missions first
            if (a.status === 'complete' && b.status !== 'complete') return -1;
            if (a.status !== 'complete' && b.status === 'complete') return 1;
            
            // Then by date
            if (a.date && b.date) {
                return b.date.localeCompare(a.date);
            }
            return 0;
        });
        
        sortedMissions.forEach(mission => {
            const card = createMissionCard(mission);
            grid.appendChild(card);
        });
        
        categoryDiv.appendChild(grid);
        container.appendChild(categoryDiv);
    });
}

/**
 * Create a mission card element
 * Displays mission title, status, agent, date, and excerpt with link to full report
 */
function createMissionCard(mission) {
    const card = document.createElement('div');
    card.className = 'mission-card';
    
    // Card header with title and status
    const header = document.createElement('div');
    header.className = 'mission-card-header';
    
    const title = document.createElement('h4');
    title.className = 'mission-title';
    title.textContent = mission.title.replace(/^#+\s*/, ''); // Remove leading # from title
    
    const status = document.createElement('span');
    status.className = `mission-status ${mission.status}`;
    status.textContent = mission.status === 'complete' ? '✅ Complete' : '🔄 In Progress';
    
    header.appendChild(title);
    header.appendChild(status);
    card.appendChild(header);
    
    // Mission metadata
    const meta = document.createElement('div');
    meta.className = 'mission-meta';
    
    if (mission.agent && mission.agent !== 'unknown') {
        const agentSpan = document.createElement('span');
        agentSpan.innerHTML = `🤖 <strong>${mission.agent}</strong>`;
        meta.appendChild(agentSpan);
    }
    
    if (mission.date) {
        const dateSpan = document.createElement('span');
        dateSpan.innerHTML = `📅 ${mission.date}`;
        meta.appendChild(dateSpan);
    }
    
    if (mission.mission_id) {
        const idSpan = document.createElement('span');
        idSpan.innerHTML = `🎯 ${mission.mission_id}`;
        meta.appendChild(idSpan);
    }
    
    if (meta.children.length > 0) {
        card.appendChild(meta);
    }
    
    // Excerpt
    if (mission.excerpt) {
        const excerpt = document.createElement('p');
        excerpt.className = 'mission-excerpt';
        excerpt.textContent = mission.excerpt;
        card.appendChild(excerpt);
    }
    
    // Link to full report
    const link = document.createElement('a');
    link.className = 'mission-link';
    link.href = `https://github.com/enufacas/Chained/blob/main/investigation-reports/${mission.filename}`;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.innerHTML = '📄 View Full Report →';
    card.appendChild(link);
    
    return card;
}

// ============================================================================
// TAB SWITCHING
// ============================================================================

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Activate button
    event.target.classList.add('active');
    
    // Load mission reports if switching to that tab
    if (tabName === 'mission-reports' && !window.missionReportsLoaded) {
        loadMissionReports();
        window.missionReportsLoaded = true;
    }
    
    // Load codebase graph if switching to that tab
    if (tabName === 'codebase' && !window.codebaseGraphLoaded) {
        createCodebaseGraph();
        window.codebaseGraphLoaded = true;
    }
}

const width = document.getElementById('graph-container').clientWidth;
const height = 800;

let simulation;
let physicsEnabled = true;

// Create SVG
const svg = d3.select("#graph-svg")
    .attr("width", width)
    .attr("height", height);

// Add zoom behavior
const g = svg.append("g");
const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on("zoom", (event) => {
        g.attr("transform", event.transform);
    });

svg.call(zoom);

// Tooltip
const tooltip = d3.select("#tooltip");

// Color scheme for different categories
const colorScheme = {
    'AI/ML': '#ff6b6b',
    'Tools': '#4ecdc4',
    'Applications': '#45b7d1',
    'Research': '#96ceb4',
    'Industry': '#ffeaa7',
    'default': '#00d4ff'
};

// Extract keywords from title to categorize
function categorizeStory(title) {
    const titleLower = title.toLowerCase();
    
    if (titleLower.match(/\b(gpt|llm|neural|model|training|dataset|transformer)\b/)) {
        return 'AI/ML';
    } else if (titleLower.match(/\b(framework|library|tool|sdk|api)\b/)) {
        return 'Tools';
    } else if (titleLower.match(/\b(app|application|product|service)\b/)) {
        return 'Applications';
    } else if (titleLower.match(/\b(research|study|paper|academic|science)\b/)) {
        return 'Research';
    } else if (titleLower.match(/\b(company|business|market|industry|startup)\b/)) {
        return 'Industry';
    }
    return 'AI/ML';
}

// Extract key terms from title
function extractKeyTerms(title) {
    const terms = [];
    const titleLower = title.toLowerCase();
    
    // Common AI/ML terms to extract
    const aiTerms = [
        'ai', 'ml', 'gpt', 'llm', 'neural', 'model', 'training', 'dataset',
        'transformer', 'copilot', 'chatbot', 'nlp', 'vision', 'deep learning',
        'machine learning', 'reinforcement learning', 'supervised', 'unsupervised',
        'tensorflow', 'pytorch', 'hugging face', 'openai', 'anthropic', 'claude',
        'embeddings', 'fine-tuning', 'prompt', 'rag', 'vector', 'agent'
    ];
    
    for (const term of aiTerms) {
        if (titleLower.includes(term)) {
            terms.push(term);
        }
    }
    
    return terms;
}

// Build graph data from learnings
async function buildGraphData() {
    const nodes = [];
    const links = [];
    const nodeMap = new Map();
    const topicMap = new Map();
    let nodeId = 0;
    
    try {
        // Try to fetch learning files from last 7 days
        const learningFiles = [];
        const today = new Date();
        
        // Scan last 7 days for learning files
        for (let daysAgo = 0; daysAgo < 7; daysAgo++) {
            const date = new Date(today);
            date.setDate(today.getDate() - daysAgo);
            const dateStr = date.toISOString().split('T')[0].replace(/-/g, '');
            
            // Try various time patterns that might exist
            ['070000', '071000', '082000', '083000', '130000', '131000', '132000',
             '185000', '186000', '190000', '191000', '202000', '202500'].forEach(time => {
                learningFiles.push(`hn_${dateStr}_${time}.json`);
                learningFiles.push(`tldr_${dateStr}_${time}.json`);
            });
        }
        
        let lastUpdate = null;
        
        for (const filename of learningFiles) {
            try {
                const response = await fetch(`../learnings/${filename}`);
                if (!response.ok) continue;
                
                const data = await response.json();
                if (!lastUpdate || data.timestamp > lastUpdate) {
                    lastUpdate = data.timestamp;
                }
                
                // Process learnings
                for (const learning of data.learnings || []) {
                    const title = learning.title || learning.description || 'Untitled';
                    const titleLower = title.toLowerCase();
                    
                    // Only include AI-related stories
                    if (!titleLower.match(/\b(ai|ml|llm|gpt|neural|machine learning|copilot|model|training|chatbot|nlp|deep learning|transformer|agent|openai|anthropic|claude)\b/)) {
                        continue;
                    }
                    
                    const category = categorizeStory(title);
                    const terms = extractKeyTerms(title);
                    // Use popularity-based scoring if no score field exists
                    const score = learning.score || learning.points || 100;
                    
                    // Create node for the story
                    const storyNode = {
                        id: nodeId++,
                        label: title.substring(0, 30) + (title.length > 30 ? '...' : ''),
                        fullTitle: title,
                        url: learning.url || learning.link || '#',
                        score: score,
                        category: category,
                        type: 'story',
                        terms: terms,
                        source: learning.source || data.source || 'Unknown'
                    };
                    
                    nodes.push(storyNode);
                    nodeMap.set(title, storyNode);
                    
                    // Create or link to topic nodes
                    for (const term of terms) {
                        if (!topicMap.has(term)) {
                            const topicNode = {
                                id: nodeId++,
                                label: term.toUpperCase(),
                                fullTitle: term,
                                category: 'AI/ML',
                                type: 'topic',
                                count: 0
                            };
                            nodes.push(topicNode);
                            topicMap.set(term, topicNode);
                        }
                        
                        const topicNode = topicMap.get(term);
                        topicNode.count = (topicNode.count || 0) + 1;
                        
                        // Create link between story and topic
                        links.push({
                            source: storyNode.id,
                            target: topicNode.id,
                            value: 1
                        });
                    }
                }
            } catch (e) {
                // File doesn't exist or error reading
                console.log(`Could not load ${filename}`);
            }
        }
        
        // Create links between stories that share topics
        nodes.filter(n => n.type === 'story').forEach(node1 => {
            nodes.filter(n => n.type === 'story' && n.id > node1.id).forEach(node2 => {
                const sharedTerms = node1.terms.filter(t => node2.terms.includes(t));
                if (sharedTerms.length >= 2) {
                    links.push({
                        source: node1.id,
                        target: node2.id,
                        value: sharedTerms.length
                    });
                }
            });
        });
        
        // Update stats
        document.getElementById('node-count').textContent = nodes.length;
        document.getElementById('link-count').textContent = links.length;
        document.getElementById('topic-count').textContent = topicMap.size;
        
        if (lastUpdate) {
            const date = new Date(lastUpdate);
            document.getElementById('last-update').textContent = date.toLocaleString();
            document.getElementById('footer-last-updated').textContent = date.toLocaleString();
        }
        
        // Update insights
        updateInsights(nodes, topicMap);
        
    } catch (error) {
        console.error('Error building graph:', error);
    }
    
    return { nodes, links };
}

// Update insights section
function updateInsights(nodes, topicMap) {
    // Trending topics (most mentioned)
    const sortedTopics = Array.from(topicMap.entries())
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 5);
    
    const trendingList = document.getElementById('trending-topics');
    trendingList.innerHTML = sortedTopics
        .map(([term, node]) => `<li>${term.toUpperCase()} (${node.count} mentions)</li>`)
        .join('');
    
    // Emerging tech (topics with high scores)
    const storyNodes = nodes.filter(n => n.type === 'story');
    const highScoreTopics = new Map();
    
    storyNodes.forEach(node => {
        if (node.score > 200) {
            node.terms.forEach(term => {
                highScoreTopics.set(term, (highScoreTopics.get(term) || 0) + node.score);
            });
        }
    });
    
    const emergingList = document.getElementById('emerging-tech');
    const emerging = Array.from(highScoreTopics.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    if (emerging.length > 0) {
        emergingList.innerHTML = emerging
            .map(([term, score]) => `<li>${term.toUpperCase()} (avg score: ${Math.round(score / topicMap.get(term).count)})</li>`)
            .join('');
    } else {
        emergingList.innerHTML = '<li>Analyzing trends...</li>';
    }
    
    // Most connected stories
    const connectedList = document.getElementById('most-connected');
    const topStories = storyNodes
        .sort((a, b) => b.terms.length - a.terms.length)
        .slice(0, 5);
    
    connectedList.innerHTML = topStories
        .map(node => `<li>${node.fullTitle.substring(0, 50)}... (${node.terms.length} topics)</li>`)
        .join('');
}

// Create and update the graph visualization
async function createGraph() {
    const { nodes, links } = await buildGraphData();
    
    if (nodes.length === 0) {
        g.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "#00d4ff")
            .style("font-size", "20px")
            .text("No AI-related learnings found yet. Check back after learning workflows run!");
        return;
    }
    
    // Create simulation
    simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(d => d.type === 'topic' ? 40 : 30));
    
    // Create links
    const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("stroke-width", d => Math.sqrt(d.value));
    
    // Create nodes
    const node = g.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(nodes)
        .enter()
        .append("g")
        .attr("class", "node")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
    
    // Add circles
    node.append("circle")
        .attr("r", d => {
            if (d.type === 'topic') {
                return Math.min(10 + d.count * 3, 40);
            } else {
                return Math.min(5 + Math.sqrt(d.score || 100) / 2, 25);
            }
        })
        .attr("fill", d => colorScheme[d.category] || colorScheme.default)
        .attr("opacity", d => d.type === 'topic' ? 0.9 : 0.7);
    
    // Add labels
    node.append("text")
        .text(d => d.label)
        .attr("dy", d => d.type === 'topic' ? 4 : 35)
        .style("font-size", d => d.type === 'topic' ? "14px" : "10px")
        .style("font-weight", d => d.type === 'topic' ? "bold" : "normal")
        .style("fill", d => d.type === 'topic' ? colorScheme[d.category] : "#e0e0e0");
    
    // Add hover effects
    node.on("mouseover", function(event, d) {
        d3.select(this).select("circle")
            .transition()
            .duration(200)
            .attr("r", r => parseFloat(d3.select(this).select("circle").attr("r")) * 1.3);
        
        tooltip.style("opacity", 1)
            .html(`
                <h4>${d.fullTitle}</h4>
                ${d.type === 'story' ? `
                    <p><strong>Score:</strong> ${d.score}</p>
                    <p><strong>Category:</strong> ${d.category}</p>
                    <p><strong>Source:</strong> ${d.source}</p>
                    <p><strong>Topics:</strong> ${d.terms.join(', ')}</p>
                    <p><a href="${d.url}" target="_blank" style="color: #00d4ff;">Read More →</a></p>
                ` : `
                    <p><strong>Mentions:</strong> ${d.count}</p>
                    <p><strong>Type:</strong> Topic</p>
                `}
            `)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 10) + "px");
    })
    .on("mouseout", function(event, d) {
        d3.select(this).select("circle")
            .transition()
            .duration(200)
            .attr("r", r => parseFloat(d3.select(this).select("circle").attr("r")) / 1.3);
        
        tooltip.style("opacity", 0);
    })
    .on("click", function(event, d) {
        if (d.type === 'story' && d.url) {
            window.open(d.url, '_blank');
        }
    });
    
    // Update positions on tick
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        
        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });
}

// Drag functions
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Control functions
function resetZoom() {
    svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
}

function togglePhysics() {
    physicsEnabled = !physicsEnabled;
    if (physicsEnabled) {
        simulation.alphaTarget(0.3).restart();
        setTimeout(() => simulation.alphaTarget(0), 1000);
    } else {
        simulation.stop();
    }
}

function exportGraph() {
    // Export graph data as JSON
    const data = {
        nodes: simulation.nodes(),
        links: simulation.force("link").links(),
        exported: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ai-knowledge-graph-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Initialize the AI learnings graph
createGraph();

// ========== Codebase Graph Visualization ==========

let codebaseSimulation;
let codebasePhysicsEnabled = true;
let currentCodebaseFilter = 'all';

// Create codebase SVG
const codebaseSvg = d3.select("#codebase-graph-svg")
    .attr("width", width)
    .attr("height", height);

const codebaseG = codebaseSvg.append("g");
const codebaseZoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on("zoom", (event) => {
        codebaseG.attr("transform", event.transform);
    });

codebaseSvg.call(codebaseZoom);

const codebaseTooltip = d3.select("#codebase-tooltip");

// Color scheme for codebase
const codebaseColorScheme = {
    'code_file': '#4ecdc4',
    'test_file': '#ff6b6b',
    'agent': '#ffeaa7'
};

async function createCodebaseGraph() {
    try {
        const response = await fetch('data/codebase-graph.json');
        if (!response.ok) {
            throw new Error('Codebase graph not found');
        }
        
        const graphData = await response.json();
        
        // Update stats
        const stats = graphData.statistics;
        document.getElementById('codebase-node-count').textContent = graphData.nodes.length;
        document.getElementById('codebase-link-count').textContent = graphData.relationships.length;
        document.getElementById('codebase-function-count').textContent = stats.total_functions || 0;
        document.getElementById('codebase-class-count').textContent = stats.total_classes || 0;
        
        // Build graph
        const nodes = graphData.nodes.map(n => ({...n}));
        const links = graphData.relationships.map(r => ({
            source: r.source,
            target: r.target,
            type: r.type,
            weight: r.weight
        }));
        
        // Create simulation
        codebaseSimulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(25));
        
        // Create links
        const link = codebaseG.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links)
            .enter()
            .append("line")
            .attr("class", d => `link link-${d.type}`)
            .attr("stroke", d => {
                if (d.type === 'imports') return '#666';
                if (d.type === 'tests') return '#ff6b6b';
                if (d.type === 'worked_on') return '#ffeaa7';
                if (d.type === 'changes_with') return '#96ceb4';
                return '#666';
            })
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", d => Math.min(d.weight * 1.5, 4));
        
        // Create nodes
        const node = codebaseG.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes)
            .enter()
            .append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", codebaseDragstarted)
                .on("drag", codebaseDragged)
                .on("end", codebaseDragended));
        
        // Add circles
        node.append("circle")
            .attr("r", d => {
                if (d.type === 'agent') return 20;
                if (d.type === 'test_file') return 8;
                return Math.min(5 + (d.functions || 0), 15);
            })
            .attr("fill", d => codebaseColorScheme[d.type] || '#4ecdc4')
            .attr("opacity", 0.8);
        
        // Add labels
        node.append("text")
            .text(d => d.label)
            .attr("dy", 25)
            .style("font-size", d => d.type === 'agent' ? "12px" : "9px")
            .style("font-weight", d => d.type === 'agent' ? "bold" : "normal")
            .style("fill", "#e0e0e0");
        
        // Add hover effects
        node.on("mouseover", function(event, d) {
            d3.select(this).select("circle")
                .transition()
                .duration(200)
                .attr("r", r => parseFloat(d3.select(this).select("circle").attr("r")) * 1.3);
            
            let tooltipContent = `<h4>${d.label}</h4>`;
            
            if (d.type === 'agent') {
                tooltipContent += `
                    <p><strong>Type:</strong> Agent</p>
                    <p><strong>Files worked on:</strong> ${d.files_worked_on}</p>
                    <p><strong>Expertise:</strong> ${d.expertise.join(', ')}</p>
                `;
            } else {
                tooltipContent += `
                    <p><strong>Type:</strong> ${d.type.replace('_', ' ')}</p>
                    <p><strong>Functions:</strong> ${d.functions || 0}</p>
                    <p><strong>Classes:</strong> ${d.classes || 0}</p>
                    <p><strong>Lines:</strong> ${d.lines_of_code || 0}</p>
                `;
                
                // Add complexity metrics if available
                if (d.complexity_score) {
                    tooltipContent += `<p><strong>Complexity:</strong> ${d.complexity_score.toFixed(1)}</p>`;
                }
                
                // Add code quality warnings
                if (d.code_smells && d.code_smells.length > 0) {
                    tooltipContent += `<p><strong>⚠️ Issues:</strong> ${d.code_smells.join(', ')}</p>`;
                }
                
                // Add refactoring count
                if (d.refactoring_count > 0) {
                    tooltipContent += `<p><strong>🔄 Refactorings:</strong> ${d.refactoring_count}</p>`;
                }
                
                tooltipContent += `<p><strong>Path:</strong> ${d.filepath}</p>`;
            }
            
            codebaseTooltip.style("opacity", 1)
                .html(tooltipContent)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        })
        .on("mouseout", function(event, d) {
            d3.select(this).select("circle")
                .transition()
                .duration(200)
                .attr("r", r => parseFloat(d3.select(this).select("circle").attr("r")) / 1.3);
            
            codebaseTooltip.style("opacity", 0);
        });
        
        // Update positions on tick
        codebaseSimulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node.attr("transform", d => `translate(${d.x},${d.y})`);
        });
        
        // Update insights
        updateCodebaseInsights(nodes, stats, graphData.relationships);
        
        // Show quality insights in console
        showQualityInsights(graphData);
        
        // Store for filtering
        window.codebaseNodes = nodes;
        window.codebaseLinks = links;
        window.codebaseNodeElements = node;
        window.codebaseLinkElements = link;
        
    } catch (error) {
        console.error('Error loading codebase graph:', error);
        codebaseG.append("text")
            .attr("x", width / 2)
            .attr("y", height / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "#00d4ff")
            .style("font-size", "18px")
            .text("Codebase graph not generated yet. Run: python tools/knowledge_graph_builder.py");
    }
}

function updateCodebaseInsights(nodes, stats, relationships) {
    // Most central files
    const fileCentrality = {};
    relationships.forEach(rel => {
        fileCentrality[rel.source] = (fileCentrality[rel.source] || 0) + 1;
        fileCentrality[rel.target] = (fileCentrality[rel.target] || 0) + 1;
    });
    
    const centralFiles = Object.entries(fileCentrality)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    const centralList = document.getElementById('central-files');
    centralList.innerHTML = centralFiles
        .map(([file, count]) => {
            const node = nodes.find(n => n.id === file);
            return `<li>${node ? node.label : file} (${count} connections)</li>`;
        })
        .join('');
    
    // Test coverage
    const testRels = relationships.filter(r => r.type === 'tests');
    const testCoverageList = document.getElementById('test-coverage');
    testCoverageList.innerHTML = `
        <li>Total tests: ${nodes.filter(n => n.type === 'test_file').length}</li>
        <li>Code files tested: ${new Set(testRels.map(r => r.target)).size}</li>
        <li>Test relationships: ${testRels.length}</li>
    `;
    
    // Agent expertise
    const agents = nodes.filter(n => n.type === 'agent');
    const expertiseList = document.getElementById('agent-expertise');
    if (agents.length > 0) {
        expertiseList.innerHTML = agents
            .slice(0, 5)
            .map(agent => `<li>${agent.label}: ${agent.expertise.join(', ')}</li>`)
            .join('');
    } else {
        expertiseList.innerHTML = '<li>No agent data available yet</li>';
    }
}

// Enhanced insights with quality metrics
function showQualityInsights(graphData) {
    // Show complexity insights
    const complexFiles = graphData.nodes
        .filter(n => n.type === 'code_file' && n.complexity_score > 5)
        .sort((a, b) => b.complexity_score - a.complexity_score)
        .slice(0, 5);
    
    if (complexFiles.length > 0) {
        console.log('🔍 Most Complex Files:');
        complexFiles.forEach(f => {
            console.log(`  ${f.label}: ${f.complexity_score} (${f.functions} functions)`);
        });
    }
    
    // Show files with code smells
    const filesWithSmells = graphData.nodes
        .filter(n => n.code_smells && n.code_smells.length > 0);
    
    if (filesWithSmells.length > 0) {
        console.log('\n⚠️ Files with Code Smells:');
        filesWithSmells.slice(0, 5).forEach(f => {
            console.log(`  ${f.label}: ${f.code_smells.join(', ')}`);
        });
    }
    
    // Show refactoring history
    const refactoredFiles = graphData.nodes
        .filter(n => n.refactoring_count > 0)
        .sort((a, b) => b.refactoring_count - a.refactoring_count)
        .slice(0, 5);
    
    if (refactoredFiles.length > 0) {
        console.log('\n🔄 Frequently Refactored:');
        refactoredFiles.forEach(f => {
            console.log(`  ${f.label}: ${f.refactoring_count} refactorings`);
        });
    }
    
    // Summary statistics
    const avgComplexity = graphData.nodes
        .filter(n => n.complexity_score)
        .reduce((sum, n) => sum + n.complexity_score, 0) / 
        graphData.nodes.filter(n => n.complexity_score).length;
    
    console.log(`\n📊 Average Complexity: ${avgComplexity.toFixed(2)}`);
    console.log(`📊 Files with Issues: ${filesWithSmells.length}`);
}

function filterCodebase(filterType) {
    if (!window.codebaseLinks || !window.codebaseLinkElements) return;
    
    currentCodebaseFilter = filterType;
    
    if (filterType === 'all') {
        window.codebaseLinkElements.style("display", "block");
        window.codebaseNodeElements.style("display", "block");
    } else {
        // Filter links by type
        window.codebaseLinkElements.style("display", d => {
            if (filterType === 'imports' && d.type === 'imports') return "block";
            if (filterType === 'tests' && d.type === 'tests') return "block";
            if (filterType === 'agents' && d.type === 'worked_on') return "block";
            return "none";
        });
        
        // Show only connected nodes
        const visibleLinks = window.codebaseLinks.filter(d => {
            if (filterType === 'imports' && d.type === 'imports') return true;
            if (filterType === 'tests' && d.type === 'tests') return true;
            if (filterType === 'agents' && d.type === 'worked_on') return true;
            return false;
        });
        
        const visibleNodeIds = new Set();
        visibleLinks.forEach(link => {
            visibleNodeIds.add(link.source.id || link.source);
            visibleNodeIds.add(link.target.id || link.target);
        });
        
        window.codebaseNodeElements.style("display", d => {
            return visibleNodeIds.has(d.id) ? "block" : "none";
        });
    }
}

// Drag functions for codebase
function codebaseDragstarted(event, d) {
    if (!event.active) codebaseSimulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function codebaseDragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function codebaseDragended(event, d) {
    if (!event.active) codebaseSimulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Control functions for codebase
function resetCodebaseZoom() {
    codebaseSvg.transition().duration(750).call(codebaseZoom.transform, d3.zoomIdentity);
}

function toggleCodebasePhysics() {
    codebasePhysicsEnabled = !codebasePhysicsEnabled;
    if (codebasePhysicsEnabled) {
        codebaseSimulation.alphaTarget(0.3).restart();
        setTimeout(() => codebaseSimulation.alphaTarget(0), 1000);
    } else {
        codebaseSimulation.stop();
    }
}


// ============================================================================
// INITIALIZATION - by @guide-wizard
// ============================================================================

/**
 * Initialize the page on load
 * Mission Reports tab is active by default, so load it immediately
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Knowledge Graph page initialized by @guide-wizard');
    
    // Load mission reports immediately since it's the active tab
    loadMissionReports();
    window.missionReportsLoaded = true;
});
