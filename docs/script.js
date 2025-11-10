// Fetch and display GitHub repository data
const REPO_OWNER = 'enufacas';
const REPO_NAME = 'Chained';
const API_BASE = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;

// Workflow schedules mapping
const WORKFLOW_SCHEDULES = {
    'Smart Idea Generator': { cron: '0 10 * * *', description: 'Daily at 10:00 AM UTC' },
    'AI Idea Generator': { cron: '0 9 * * *', description: 'Daily at 9:00 AM UTC' },
    'Daily AI Goal Generator': { cron: '0 6 * * *', description: 'Daily at 6:00 AM UTC' },
    'Goal Progress Checker': { cron: '0 */3 * * *', description: 'Every 3 hours' },
    'Learning from TLDR Tech': { cron: '0 8,20 * * *', description: 'Twice daily at 8:00 AM and 8:00 PM UTC' },
    'Learning from Hacker News': { cron: '0 7,13,19 * * *', description: 'Three times daily at 7:00 AM, 1:00 PM, and 7:00 PM UTC' },
    'Auto Review and Merge': { cron: '*/15 * * * *', description: 'Every 15 minutes' },
    'Progress Tracker': { cron: '0 */12 * * *', description: 'Every 12 hours' },
    'Timeline Updater': { cron: '0 */6 * * *', description: 'Every 6 hours' },
};

// Update last updated timestamp
document.getElementById('last-updated').textContent = new Date().toLocaleString();

// Fetch and display AI Goal of the Day
async function fetchAIGoal() {
    try {
        const response = await fetch('AI_GOALS.md');
        if (!response.ok) {
            throw new Error('Could not fetch AI goals');
        }
        
        const markdown = await response.text();
        
        // Parse the current goal from markdown
        const categoryMatch = markdown.match(/\*\*Category\*\*:\s*(.+)/);
        const goalMatch = markdown.match(/\*\*Goal\*\*:\s*(.+)/);
        const dateMatch = markdown.match(/\*\*Date\*\*:\s*(.+)/);
        const statusMatch = markdown.match(/\*\*Status\*\*:\s*(.+)/);
        
        if (categoryMatch && goalMatch && dateMatch) {
            document.getElementById('goal-category').textContent = categoryMatch[1].trim();
            document.getElementById('goal-description').textContent = goalMatch[1].trim();
            document.getElementById('goal-date').textContent = dateMatch[1].trim();
            
            if (statusMatch) {
                document.getElementById('goal-status').textContent = statusMatch[1].trim();
            }
            
            // Parse progress from the markdown (look for progress updates)
            const progressMatches = markdown.match(/\((\d+)%\s*complete\)/);
            if (progressMatches) {
                const progress = parseInt(progressMatches[1]);
                document.getElementById('goal-progress').style.width = progress + '%';
                document.getElementById('goal-progress-text').textContent = progress + '%';
            }
        } else {
            // No current goal
            document.getElementById('goal-category').textContent = 'No Active Goal';
            document.getElementById('goal-description').textContent = 'The next goal will be generated at 6 AM UTC. You can also trigger it manually via GitHub Actions.';
            document.getElementById('goal-date').textContent = 'Pending';
            document.getElementById('goal-status').textContent = '⏳ Pending';
        }
    } catch (error) {
        console.error('Error fetching AI goal:', error);
        document.getElementById('goal-category').textContent = 'Loading Error';
        document.getElementById('goal-description').textContent = 'Could not load the current goal. Please check back later.';
        document.getElementById('goal-date').textContent = '-';
        document.getElementById('goal-status').textContent = '❌ Error';
    }
}

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
                
                // Try to load learning stats
                try {
                    const learningResponse = await fetch('../learnings/index.json');
                    if (learningResponse.ok) {
                        const learningStats = await learningResponse.json();
                        console.log('Learning stats:', learningStats);
                    }
                } catch (e) {
                    console.log('Learning stats not yet available');
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

// Load workflow schedules and display them
async function loadWorkflowSchedules() {
    try {
        // Try to fetch workflows from cached data
        const workflowsResponse = await fetch('data/workflows.json');
        if (workflowsResponse.ok) {
            const workflows = await workflowsResponse.json();
            displayWorkflowSchedules(workflows);
        } else {
            console.log('Workflows data not available');
        }
    } catch (error) {
        console.error('Error fetching workflow schedules:', error);
    }
}

// Display workflow schedules with last run and next run info
function displayWorkflowSchedules(workflows) {
    const container = document.getElementById('workflow-schedules-container');
    container.innerHTML = '';
    
    // Group workflows by name and find the most recent run
    const workflowMap = new Map();
    workflows.forEach(workflow => {
        const name = workflow.name;
        if (!workflowMap.has(name) || new Date(workflow.createdAt) > new Date(workflowMap.get(name).createdAt)) {
            workflowMap.set(name, workflow);
        }
    });
    
    // Display scheduled workflows
    Object.entries(WORKFLOW_SCHEDULES).forEach(([workflowName, schedule]) => {
        const latestRun = workflowMap.get(workflowName);
        const scheduleItem = createWorkflowScheduleItem(workflowName, schedule, latestRun);
        container.appendChild(scheduleItem);
    });
}

// Create a workflow schedule item
function createWorkflowScheduleItem(workflowName, schedule, latestRun) {
    const item = document.createElement('div');
    item.className = 'workflow-schedule-item';
    
    let statusEmoji = '⏰';
    let statusClass = '';
    let lastRunText = 'No recent runs';
    
    if (latestRun) {
        const lastRunDate = new Date(latestRun.createdAt);
        const timeAgo = getTimeAgo(lastRunDate);
        
        if (latestRun.status === 'completed') {
            if (latestRun.conclusion === 'success') {
                statusEmoji = '✅';
                statusClass = 'success';
                lastRunText = `Last run: ${timeAgo} - Success`;
            } else if (latestRun.conclusion === 'failure') {
                statusEmoji = '❌';
                statusClass = 'failure';
                lastRunText = `Last run: ${timeAgo} - Failed`;
            } else {
                statusEmoji = '⚠️';
                statusClass = 'success';
                lastRunText = `Last run: ${timeAgo} - ${latestRun.conclusion}`;
            }
        } else if (latestRun.status === 'in_progress') {
            statusEmoji = '🔄';
            statusClass = 'in-progress';
            lastRunText = `Running now (started ${timeAgo})`;
        }
    }
    
    const nextRun = calculateNextRun(schedule.cron);
    
    item.innerHTML = `
        <h3>${statusEmoji} ${escapeHtml(workflowName)}</h3>
        <p class="schedule-info"><strong>Schedule:</strong> ${escapeHtml(schedule.description)}</p>
        <p class="schedule-info"><strong>Next run:</strong> ${nextRun}</p>
        <p class="last-run ${statusClass}">${lastRunText}</p>
    `;
    
    return item;
}

// Calculate next run time from cron expression (simplified)
function calculateNextRun(cronExpression) {
    const now = new Date();
    const parts = cronExpression.split(' ');
    
    // Simple cron parser for common patterns
    if (cronExpression.startsWith('*/15')) {
        // Every 15 minutes
        const minutes = now.getMinutes();
        const nextMinute = Math.ceil(minutes / 15) * 15;
        const nextRun = new Date(now);
        if (nextMinute >= 60) {
            nextRun.setHours(now.getHours() + 1);
            nextRun.setMinutes(0);
        } else {
            nextRun.setMinutes(nextMinute);
        }
        return getTimeUntil(nextRun);
    } else if (cronExpression.includes('*/12')) {
        // Every 12 hours
        const hours = now.getUTCHours();
        const nextHour = Math.ceil(hours / 12) * 12;
        const nextRun = new Date(now);
        if (nextHour >= 24) {
            nextRun.setUTCDate(now.getUTCDate() + 1);
            nextRun.setUTCHours(0);
        } else {
            nextRun.setUTCHours(nextHour);
        }
        nextRun.setUTCMinutes(0);
        return getTimeUntil(nextRun);
    } else if (cronExpression.includes('*/6')) {
        // Every 6 hours
        const hours = now.getUTCHours();
        const nextHour = Math.ceil(hours / 6) * 6;
        const nextRun = new Date(now);
        if (nextHour >= 24) {
            nextRun.setUTCDate(now.getUTCDate() + 1);
            nextRun.setUTCHours(0);
        } else {
            nextRun.setUTCHours(nextHour);
        }
        nextRun.setUTCMinutes(0);
        return getTimeUntil(nextRun);
    } else {
        // Daily or multiple times daily
        const hours = parts[1].split(',').map(h => parseInt(h));
        const currentHour = now.getUTCHours();
        
        let nextHour = hours.find(h => h > currentHour);
        const nextRun = new Date(now);
        
        if (nextHour !== undefined) {
            nextRun.setUTCHours(nextHour);
            nextRun.setUTCMinutes(0);
        } else {
            // Next day
            nextRun.setUTCDate(now.getUTCDate() + 1);
            nextRun.setUTCHours(hours[0]);
            nextRun.setUTCMinutes(0);
        }
        
        return getTimeUntil(nextRun);
    }
}

// Get time ago string
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [name, secondsInInterval] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInInterval);
        if (interval >= 1) {
            return `${interval} ${name}${interval !== 1 ? 's' : ''} ago`;
        }
    }
    
    return 'just now';
}

// Get time until string
function getTimeUntil(date) {
    const seconds = Math.floor((date - new Date()) / 1000);
    
    if (seconds < 60) {
        return `in ${seconds} second${seconds !== 1 ? 's' : ''}`;
    }
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) {
        return `in ${minutes} minute${minutes !== 1 ? 's' : ''}`;
    }
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
        return `in ${hours} hour${hours !== 1 ? 's' : ''}`;
    }
    
    const days = Math.floor(hours / 24);
    return `in ${days} day${days !== 1 ? 's' : ''}`;
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

// Load auto learnings from the learnings directory
async function loadAutoLearnings() {
    try {
        // Fetch learning index
        const indexResponse = await fetch('../learnings/index.json');
        if (!indexResponse.ok) {
            console.log('Learning index not available');
            return;
        }
        
        const indexData = await indexResponse.json();
        
        // Update stats
        document.getElementById('total-learnings').textContent = indexData.total_learnings || 0;
        document.getElementById('tldr-learnings').textContent = indexData.sources?.tldr || 0;
        document.getElementById('hn-learnings').textContent = indexData.sources?.hacker_news || 0;
        
        // Try to fetch recent files by looking at the current date pattern
        const container = document.getElementById('learning-files-container');
        container.innerHTML = '';
        
        // Fetch learning files - try common patterns for today
        const learningFiles = [];
        const today = new Date();
        const dateStr = today.toISOString().split('T')[0].replace(/-/g, '');
        
        // Add known patterns for today
        ['082735', '083000', '202403', '202500'].forEach(time => {
            learningFiles.push({ name: `tldr_${dateStr}_${time}.json`, type: 'tldr' });
        });
        
        ['070959', '071000', '131719', '131800', '190715', '191000'].forEach(time => {
            learningFiles.push({ name: `hn_${dateStr}_${time}.json`, type: 'hn' });
        });
        
        // Try yesterday too
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);
        const yesterdayStr = yesterday.toISOString().split('T')[0].replace(/-/g, '');
        ['082000', '083000', '202000', '202500'].forEach(time => {
            learningFiles.push({ name: `tldr_${yesterdayStr}_${time}.json`, type: 'tldr' });
        });
        ['070000', '071000', '130000', '131000', '190000', '191000'].forEach(time => {
            learningFiles.push({ name: `hn_${yesterdayStr}_${time}.json`, type: 'hn' });
        });
        
        let filesFound = 0;
        for (const file of learningFiles) {
            try {
                const response = await fetch(`../learnings/${file.name}`, { method: 'HEAD' });
                if (response.ok) {
                    const dataResponse = await fetch(`../learnings/${file.name}`);
                    const data = await dataResponse.json();
                    
                    if (data.learnings && data.learnings.length > 0) {
                        filesFound++;
                        const fileItem = createLearningFileItem(file.name, data);
                        container.appendChild(fileItem);
                        
                        if (filesFound >= 10) break;
                    }
                }
            } catch (e) {
                // File doesn't exist, continue silently
            }
        }
        
        if (filesFound === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">No learning sessions found yet. Check back after the scheduled learning workflows run.</p>';
        }
        
    } catch (error) {
        console.error('Error loading auto learnings:', error);
    }
}

// Create a learning file item
function createLearningFileItem(filename, data) {
    const item = document.createElement('div');
    item.className = 'learning-file-item';
    
    // Extract date and time from filename
    const match = filename.match(/([a-z]+)_(\d{8})_(\d{6})\.json/);
    if (!match) return item;
    
    const [, source, dateStr, timeStr] = match;
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);
    const hour = timeStr.substring(0, 2);
    const minute = timeStr.substring(2, 4);
    
    const date = new Date(`${year}-${month}-${day}T${hour}:${minute}:00Z`);
    const dateFormatted = date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const sourceLabel = source === 'tldr' ? 'TLDR Tech' : 'Hacker News';
    const sourceEmoji = source === 'tldr' ? '📰' : '💬';
    const learningCount = data.learnings?.length || 0;
    
    item.innerHTML = `
        <div class="file-name">${sourceEmoji} ${escapeHtml(sourceLabel)}</div>
        <div class="file-meta">${dateFormatted}</div>
        <div class="file-count">${learningCount} stories collected</div>
    `;
    
    // Make it clickable to expand in news feed
    item.onclick = () => {
        // Scroll to news feed and filter by source
        const newsSection = document.querySelector('.news-feed');
        newsSection.scrollIntoView({ behavior: 'smooth' });
        
        // Set filter
        const filterBtn = document.querySelector(`.filter-btn[data-filter="${source === 'tldr' ? 'tldr' : 'hn'}"]`);
        if (filterBtn) {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            filterBtn.classList.add('active');
            filterNewsFeed(source === 'tldr' ? 'tldr' : 'hn');
        }
    };
    
    return item;
}

// Load news feed from recent learning files
let allNewsItems = [];

async function loadNewsFeed() {
    try {
        // Fetch recent learning files by trying today and yesterday
        const learningFiles = [];
        const today = new Date();
        const dateStr = today.toISOString().split('T')[0].replace(/-/g, '');
        
        // Add today's patterns
        ['082735', '083000', '202403', '202500'].forEach(time => {
            learningFiles.push({ name: `tldr_${dateStr}_${time}.json`, type: 'tldr' });
        });
        
        ['070959', '071000', '131719', '131800', '190715', '191000'].forEach(time => {
            learningFiles.push({ name: `hn_${dateStr}_${time}.json`, type: 'hn' });
        });
        
        // Add yesterday's patterns
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);
        const yesterdayStr = yesterday.toISOString().split('T')[0].replace(/-/g, '');
        ['082000', '083000', '202000', '202500'].forEach(time => {
            learningFiles.push({ name: `tldr_${yesterdayStr}_${time}.json`, type: 'tldr' });
        });
        ['070000', '071000', '130000', '131000', '190000', '191000'].forEach(time => {
            learningFiles.push({ name: `hn_${yesterdayStr}_${time}.json`, type: 'hn' });
        });
        
        allNewsItems = [];
        
        for (const file of learningFiles) {
            try {
                const response = await fetch(`../learnings/${file.name}`, { method: 'HEAD' });
                if (response.ok) {
                    const dataResponse = await fetch(`../learnings/${file.name}`);
                    const data = await dataResponse.json();
                    
                    if (data.learnings && data.learnings.length > 0) {
                        data.learnings.forEach(learning => {
                            allNewsItems.push({
                                ...learning,
                                source: file.type,
                                timestamp: data.timestamp
                            });
                        });
                    }
                }
            } catch (e) {
                // File doesn't exist, continue
            }
        }
        
        // Sort by score (for HN) or by order (for TLDR)
        allNewsItems.sort((a, b) => {
            const scoreA = a.score || 0;
            const scoreB = b.score || 0;
            return scoreB - scoreA;
        });
        
        // Limit to 50 most relevant items
        allNewsItems = allNewsItems.slice(0, 50);
        
        // Display news feed
        displayNewsFeed(allNewsItems);
        
        // Setup filter buttons
        setupNewsFilters();
        
    } catch (error) {
        console.error('Error loading news feed:', error);
    }
}

// Display news feed
function displayNewsFeed(items) {
    const container = document.getElementById('news-feed-container');
    container.innerHTML = '';
    
    if (items.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1; text-align: center;">No news items found yet. Check back after the scheduled learning workflows run.</p>';
        return;
    }
    
    items.forEach(item => {
        const newsItem = createNewsItem(item);
        container.appendChild(newsItem);
    });
}

// Create a news item
function createNewsItem(item) {
    const div = document.createElement('div');
    div.className = `news-item ${item.source}`;
    div.dataset.source = item.source;
    
    const sourceLabel = item.source === 'tldr' ? 'TLDR Tech' : 'Hacker News';
    const hasUrl = item.url && item.url.trim() !== '';
    
    let scoreInfo = '';
    if (item.score) {
        scoreInfo = `<span class="news-score">▲ ${item.score} points</span>`;
    }
    
    div.innerHTML = `
        <span class="news-source ${item.source}">${escapeHtml(sourceLabel)}</span>
        <h3>${escapeHtml(item.title)}</h3>
        ${item.description ? `<p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.5rem;">${escapeHtml(item.description)}</p>` : ''}
        <div class="news-meta">
            ${scoreInfo}
            ${hasUrl ? `<a href="${item.url}" target="_blank" rel="noopener noreferrer">Read more →</a>` : ''}
        </div>
    `;
    
    return div;
}

// Setup news filters
function setupNewsFilters() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Filter news
            const filter = btn.dataset.filter;
            filterNewsFeed(filter);
        });
    });
}

// Filter news feed
function filterNewsFeed(filter) {
    let filteredItems = allNewsItems;
    
    if (filter === 'tldr') {
        filteredItems = allNewsItems.filter(item => item.source === 'tldr');
    } else if (filter === 'hn') {
        filteredItems = allNewsItems.filter(item => item.source === 'hn');
    }
    
    displayNewsFeed(filteredItems);
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
fetchAIGoal();
fetchStats();
loadLearnings();
loadWorkflowSchedules();
loadAutoLearnings();
loadNewsFeed();
loadLearningsIndex();

// Refresh data every 5 minutes
setInterval(() => {
    fetchAIGoal();
    fetchStats();
    loadLearnings();
    loadWorkflowSchedules();
    loadAutoLearnings();
    loadNewsFeed();
    loadLearningsIndex();
}, 5 * 60 * 1000);

// Load learnings index
async function loadLearningsIndex() {
    try {
        // Load index.json for stats
        const indexResponse = await fetch('../learnings/index.json');
        if (indexResponse.ok) {
            const indexData = await indexResponse.json();
            document.getElementById('index-total-learnings').textContent = indexData.total_learnings || 0;
            document.getElementById('index-tldr-count').textContent = indexData.sources?.tldr || 0;
            document.getElementById('index-hn-count').textContent = indexData.sources?.hacker_news || 0;
        }

        // Load all learning files
        const learningFiles = await fetchLearningFiles();
        displayLearningsIndex(learningFiles);
        displayTopics(learningFiles);
    } catch (error) {
        console.error('Error loading learnings index:', error);
        document.getElementById('learnings-index-container').innerHTML = '<p style="color: var(--text-muted);">Unable to load learnings index.</p>';
    }
}

// Fetch learning files from the repository
async function fetchLearningFiles() {
    try {
        const response = await fetch('https://api.github.com/repos/enufacas/Chained/contents/learnings');
        if (!response.ok) return [];
        
        const files = await response.json();
        const learningFiles = files.filter(file => 
            (file.name.startsWith('tldr_') || file.name.startsWith('hn_')) && 
            file.name.endsWith('.json')
        );

        // Fetch content for each file
        const filesWithContent = await Promise.all(
            learningFiles.map(async (file) => {
                try {
                    const contentResponse = await fetch(file.download_url);
                    const content = await contentResponse.json();
                    return {
                        name: file.name,
                        url: file.html_url,
                        size: file.size,
                        content: content
                    };
                } catch (e) {
                    return {
                        name: file.name,
                        url: file.html_url,
                        size: file.size,
                        content: null
                    };
                }
            })
        );

        return filesWithContent.sort((a, b) => b.name.localeCompare(a.name));
    } catch (error) {
        console.error('Error fetching learning files:', error);
        return [];
    }
}

// Display learnings index
function displayLearningsIndex(files) {
    const container = document.getElementById('learnings-index-container');
    
    if (files.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">No learning files found yet.</p>';
        return;
    }

    container.innerHTML = '';
    files.forEach(file => {
        const div = document.createElement('div');
        div.className = 'learning-index-item';
        
        const source = file.name.startsWith('tldr_') ? 'TLDR Tech' : 'Hacker News';
        const dateMatch = file.name.match(/(\d{8})_(\d{6})/);
        let dateStr = 'Unknown date';
        if (dateMatch) {
            const date = dateMatch[1];
            const time = dateMatch[2];
            dateStr = `${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)} ${time.slice(0, 2)}:${time.slice(2, 4)}`;
        }
        
        const itemCount = file.content?.learnings?.length || 0;
        
        div.innerHTML = `
            <div class="index-file-name">${escapeHtml(source)}</div>
            <div class="index-file-meta">📅 ${dateStr}</div>
            <div class="index-file-count">📄 ${itemCount} items</div>
        `;
        
        div.addEventListener('click', () => {
            window.open(file.url, '_blank');
        });
        
        container.appendChild(div);
    });
}

// Display topics from learnings
function displayTopics(files) {
    const container = document.getElementById('topics-container');
    const topicsSet = new Set();

    files.forEach(file => {
        if (file.content && file.content.topics) {
            Object.keys(file.content.topics).forEach(topic => {
                topicsSet.add(topic);
            });
        }
    });

    if (topicsSet.size === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">No topics categorized yet.</p>';
        return;
    }

    container.innerHTML = '';
    Array.from(topicsSet).sort().forEach(topic => {
        const tag = document.createElement('span');
        tag.className = 'topic-tag';
        tag.textContent = topic;
        container.appendChild(tag);
    });
}
