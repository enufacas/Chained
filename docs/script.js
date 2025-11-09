// Fetch and display GitHub repository data
const REPO_OWNER = 'enufacas';
const REPO_NAME = 'Chained';
const API_BASE = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;

// Update last updated timestamp
document.getElementById('last-updated').textContent = new Date().toLocaleString();

// Fetch repository statistics
async function fetchStats() {
    try {
        // Try to fetch stats.json first (created by timeline updater)
        try {
            const statsResponse = await fetch('data/stats.json');
            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                document.getElementById('total-ideas').textContent = stats.ai_generated || 0;
                document.getElementById('total-prs').textContent = stats.merged_prs || 0;
                document.getElementById('total-completed').textContent = stats.completed || 0;
                document.getElementById('completion-rate').textContent = (stats.completion_rate || 0) + '%';
                
                // Load timeline from cached data if available
                const issuesResponse = await fetch('data/issues.json');
                if (issuesResponse.ok) {
                    const issues = await issuesResponse.json();
                    loadTimeline(issues);
                }
                
                return; // Successfully loaded from cache
            }
        } catch (e) {
            console.log('Cache not available, fetching from API');
        }
        
        // Fallback to API if cache not available
        const issuesResponse = await fetch(`${API_BASE}/issues?state=all&per_page=100`);
        const issues = await issuesResponse.json();
        
        const aiGenerated = issues.filter(issue => 
            issue.labels.some(label => label.name === 'ai-generated')
        ).length;
        
        const completed = issues.filter(issue => 
            issue.labels.some(label => label.name === 'completed')
        ).length;
        
        // Fetch PRs for merge count
        const prsResponse = await fetch(`${API_BASE}/pulls?state=closed&per_page=100`);
        const prs = await prsResponse.json();
        const mergedPrs = prs.filter(pr => pr.merged_at).length;
        
        const completionRate = aiGenerated > 0 ? ((completed / aiGenerated) * 100).toFixed(1) : 0;
        
        // Update stats
        document.getElementById('total-ideas').textContent = aiGenerated;
        document.getElementById('total-prs').textContent = mergedPrs;
        document.getElementById('total-completed').textContent = completed;
        document.getElementById('completion-rate').textContent = completionRate + '%';
        
        // Load timeline from issues
        loadTimeline(issues);
    } catch (error) {
        console.error('Error fetching stats:', error);
        // Keep default values on error
    }
}

// Load timeline from issues and events
function loadTimeline(issues) {
    const timelineContainer = document.getElementById('timeline-container');
    
    // Sort issues by creation date (newest first)
    const sortedIssues = issues.sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
    );
    
    // Add issues to timeline
    sortedIssues.slice(0, 10).forEach(issue => {
        const timelineItem = createTimelineItem(issue);
        timelineContainer.appendChild(timelineItem);
    });
}

// Create a timeline item from an issue
function createTimelineItem(issue) {
    const item = document.createElement('div');
    item.className = 'timeline-item';
    
    const date = new Date(issue.created_at || issue.createdAt);
    const dateStr = date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const statusEmoji = issue.state === 'closed' ? '✅' : '🔄';
    const isAutomated = issue.labels?.some(l => 
        ['ai-generated', 'copilot', 'automated', 'copilot-assigned'].includes(l.name)
    );
    const automatedBadge = isAutomated ? ' 🤖' : '';
    
    const labels = (issue.labels || []).map(label => 
        `<span class="label" style="background-color: #${label.color}">${escapeHtml(label.name)}</span>`
    ).join(' ');
    
    const body = issue.body || 'No description';
    const truncatedBody = body.length > 200 ? body.substring(0, 200) + '...' : body;
    
    item.innerHTML = `
        <div class="timeline-date">${dateStr}</div>
        <div class="timeline-content">
            <h3>${statusEmoji}${automatedBadge} ${escapeHtml(issue.title)}</h3>
            <p>${escapeHtml(truncatedBody)}</p>
            ${labels ? `<div class="labels">${labels}</div>` : ''}
            <a href="${issue.html_url || issue.url}" target="_blank">View Issue #${issue.number}</a>
        </div>
    `;
    
    return item;
}

// Load learnings from a special issue or file
async function loadLearnings() {
    try {
        // Try to fetch a LEARNINGS.md file or special issues tagged with 'learning'
        const issuesResponse = await fetch(`${API_BASE}/issues?labels=learning&state=all`);
        const learningIssues = await issuesResponse.json();
        
        if (learningIssues.length > 0) {
            const learningsContainer = document.getElementById('learnings-container');
            learningsContainer.innerHTML = ''; // Clear default content
            
            learningIssues.forEach(issue => {
                const learningItem = document.createElement('div');
                learningItem.className = 'learning-item';
                learningItem.innerHTML = `
                    <h3>🧠 ${escapeHtml(issue.title)}</h3>
                    <p>${escapeHtml(issue.body ? issue.body.substring(0, 150) : 'No description')}${issue.body && issue.body.length > 150 ? '...' : ''}</p>
                `;
                learningsContainer.appendChild(learningItem);
            });
        }
    } catch (error) {
        console.error('Error fetching learnings:', error);
        // Keep default learnings on error
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS for labels dynamically
const style = document.createElement('style');
style.textContent = `
    .labels {
        margin-top: 0.5rem;
    }
    .label {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
        margin-right: 0.5rem;
        color: white;
        font-weight: 500;
    }
    .timeline-content a {
        display: inline-block;
        margin-top: 0.5rem;
        color: var(--accent-color);
        text-decoration: none;
        font-weight: 500;
    }
    .timeline-content a:hover {
        text-decoration: underline;
    }
`;
document.head.appendChild(style);

// Initialize
fetchStats();
loadLearnings();

// Refresh data every 5 minutes
setInterval(() => {
    fetchStats();
    loadLearnings();
}, 5 * 60 * 1000);
