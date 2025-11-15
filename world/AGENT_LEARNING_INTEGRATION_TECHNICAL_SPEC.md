# 🔧 Agent-Learning Integration: Technical Specification

**Version:** 1.0  
**Coordinator:** @meta-coordinator  
**Date:** 2025-11-15

---

## Overview

This document provides the technical specification for integrating agents with historical learnings, implementing the investment system, enabling cross-agent collaboration, and presenting everything through GitHub Pages.

---

## 1. Data Schemas

### 1.1 Enhanced World State Schema

**File:** `world/world_state.json`

```json
{
  "time": "2025-11-15T07:00:00Z",
  "tick": 10,
  "agents": [
    {
      "id": "agent-123",
      "label": "🔒 Agent Name",
      "specialization": "secure-specialist",
      "location_region_id": "US:San Francisco",
      "status": "exploring",
      "home_base": "US:Charlotte",
      
      // NEW: Learning investments
      "learning_investments": [
        {
          "category": "security",
          "level": 75,
          "learnings_processed": [
            "security_analysis_20251111.md",
            "security_analysis_20251112.md"
          ],
          "ideas_generated": ["idea:42", "idea:43"],
          "last_updated": "2025-11-15T06:00:00Z"
        }
      ],
      
      // NEW: Collaboration tracking
      "collaboration_requests": [
        {
          "request_id": "collab-123",
          "requester_id": "agent-456",
          "specialist_type": "secure-specialist",
          "task_description": "Security review of API endpoints",
          "status": "in_progress",
          "created_at": "2025-11-14T12:00:00Z"
        }
      ],
      
      // NEW: Learning affinity scores
      "learning_affinities": {
        "security": 0.95,
        "performance": 0.40,
        "testing": 0.35
      }
    }
  ],
  
  "regions": [
    {
      "id": "US:San Francisco",
      "label": "San Francisco",
      "lat": 37.7749,
      "lng": -122.4194,
      "idea_count": 11,
      
      // NEW: Learning category dominance
      "primary_learning_category": "AI/ML",
      "learning_categories": {
        "AI/ML": 15,
        "security": 8,
        "infrastructure": 5
      },
      
      // NEW: Learning sources
      "learning_sources": [
        "hn_20251115_070941.json",
        "github_trending_20251114_202231.json"
      ]
    }
  ],
  
  // NEW: Learning catalog
  "learning_catalog": [
    {
      "id": "learning:security_analysis_20251111",
      "category": "security",
      "source_type": "security_analysis",
      "file_path": "learnings/security_analysis_20251111.md",
      "topics": ["CVE", "authentication", "SQL injection"],
      "relevance_score": 8.5,
      "origin_region": "US:San Francisco",
      "created_at": "2025-11-11T13:25:12Z",
      "invested_agents": ["agent-123", "agent-789"]
    }
  ]
}
```

### 1.2 Learning Index Schema

**File:** `learnings/index_by_category.json`

```json
{
  "version": "1.0",
  "generated_at": "2025-11-15T07:00:00Z",
  "categories": {
    "security": {
      "learnings": [
        {
          "id": "learning:security_analysis_20251111",
          "file": "security_analysis_20251111.md",
          "title": "Security Analysis - Nov 11",
          "topics": ["CVE", "authentication", "SQL injection"],
          "score": 8.5,
          "created_at": "2025-11-11T13:25:12Z"
        }
      ],
      "total_count": 15,
      "category_score": 245.7,
      "top_topics": ["CVE", "authentication", "encryption"],
      "last_updated": "2025-11-15T06:00:00Z",
      "related_specializations": [
        "secure-specialist",
        "secure-ninja",
        "monitor-champion"
      ]
    },
    "performance": {
      "learnings": [],
      "total_count": 8,
      "category_score": 156.3,
      "top_topics": ["optimization", "caching", "latency"],
      "related_specializations": [
        "accelerate-master",
        "accelerate-specialist"
      ]
    }
  },
  "specialization_affinity_map": {
    "secure-specialist": {
      "security": 0.95,
      "infrastructure": 0.40,
      "testing": 0.35
    },
    "accelerate-master": {
      "performance": 0.95,
      "infrastructure": 0.50,
      "testing": 0.45
    }
  }
}
```

### 1.3 Agent Investment Tracking

**File:** `docs/data/agent_investments.json`

```json
{
  "version": "1.0",
  "generated_at": "2025-11-15T07:00:00Z",
  "investments": [
    {
      "agent_id": "agent-123",
      "agent_name": "🔒 Moxie Marlinspike",
      "specialization": "secure-specialist",
      "total_investments": 3,
      "categories": [
        {
          "category": "security",
          "investment_level": 75,
          "learnings_count": 12,
          "ideas_generated": 5,
          "contribution_score": 8.2
        }
      ],
      "collaborations": [
        {
          "with_agent": "agent-456",
          "with_specialization": "engineer-master",
          "task": "API security review",
          "status": "completed"
        }
      ]
    }
  ]
}
```

---

## 2. API Specifications

### 2.1 Agent-Learning Matching Engine

**Script:** `tools/agent_learning_matcher.py`

#### Core Functions

```python
def calculate_affinity(agent_specialization: str, learning_category: str) -> float:
    """
    Calculate affinity score between agent specialization and learning category.
    
    Args:
        agent_specialization: Agent's specialization (e.g., 'secure-specialist')
        learning_category: Learning category (e.g., 'security')
    
    Returns:
        Affinity score from 0.0 (no match) to 1.0 (perfect match)
    """
    # Affinity matrix
    affinity_map = {
        'secure-specialist': {
            'security': 0.95, 'infrastructure': 0.40, 'testing': 0.35
        },
        'accelerate-master': {
            'performance': 0.95, 'optimization': 0.90, 'infrastructure': 0.50
        },
        # ... all 44 specializations
    }
    
    return affinity_map.get(agent_specialization, {}).get(learning_category, 0.0)


def match_agent_to_learnings(agent_id: str, top_n: int = 5) -> List[Dict]:
    """
    Match an agent to the most relevant learnings.
    
    Args:
        agent_id: Agent ID from registry
        top_n: Number of top matches to return
    
    Returns:
        List of learning matches with scores
    """
    agent = get_agent(agent_id)
    specialization = agent['specialization']
    
    learning_index = load_learning_index()
    matches = []
    
    for category, data in learning_index['categories'].items():
        affinity = calculate_affinity(specialization, category)
        
        for learning in data['learnings']:
            score = affinity * learning['score']
            matches.append({
                'learning_id': learning['id'],
                'category': category,
                'affinity': affinity,
                'relevance_score': learning['score'],
                'combined_score': score,
                'file': learning['file']
            })
    
    matches.sort(key=lambda x: x['combined_score'], reverse=True)
    return matches[:top_n]


def assign_learning_to_agent(agent_id: str, learning_id: str) -> Dict:
    """
    Assign a learning to an agent and create an issue for them to process it.
    
    Returns:
        Assignment details including issue number
    """
    # Create GitHub issue for agent
    # Update world state with assignment
    # Track investment
    pass
```

### 2.2 World State Management Extensions

**Script:** `world/world_state_manager.py`

#### New Functions

```python
def track_investment(agent_id: str, learning_id: str, level: int) -> None:
    """
    Track agent's investment in a learning category.
    
    Args:
        agent_id: Agent ID
        learning_id: Learning identifier
        level: Investment level (0-100)
    """
    world_state = load_world_state()
    agent = find_agent(world_state, agent_id)
    
    # Find or create investment entry
    category = extract_category(learning_id)
    investment = find_investment(agent, category)
    
    if investment:
        investment['level'] = level
        investment['learnings_processed'].append(learning_id)
        investment['last_updated'] = datetime.now(timezone.utc).isoformat()
    else:
        agent['learning_investments'].append({
            'category': category,
            'level': level,
            'learnings_processed': [learning_id],
            'ideas_generated': [],
            'last_updated': datetime.now(timezone.utc).isoformat()
        })
    
    save_world_state(world_state)


def request_collaboration(requester_id: str, specialist_type: str, 
                         task_description: str) -> str:
    """
    Create a collaboration request from one agent to another specialist type.
    
    Returns:
        Collaboration request ID
    """
    # Find best specialist agent
    specialist_agent = find_best_agent_by_specialization(specialist_type)
    
    request_id = f"collab-{int(datetime.now(timezone.utc).timestamp())}"
    
    # Add to requester's record
    # Add to specialist's record
    # Create linked GitHub issues
    
    return request_id


def reconcile_agent_state(agent_id: str) -> Dict:
    """
    Reconcile agent's local understanding with world state truth.
    
    Returns:
        Reconciliation report
    """
    world_state = load_world_state()
    agent = find_agent(world_state, agent_id)
    
    # Compare agent's expected state with actual
    # Identify discrepancies
    # Generate reconciliation actions
    
    return {
        'agent_id': agent_id,
        'discrepancies': [],
        'reconciliation_actions': [],
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
```

### 2.3 Learning Indexer

**Script:** `tools/learning_indexer.py`

```python
def index_all_learnings() -> Dict:
    """
    Index all learnings by category, extract topics, calculate scores.
    
    Returns:
        Complete learning index
    """
    learnings_dir = Path('learnings')
    index = {
        'version': '1.0',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'categories': {}
    }
    
    # Process all JSON learning files
    for file in learnings_dir.glob('*.json'):
        category = detect_category(file)
        learning_data = extract_learning_data(file)
        
        if category not in index['categories']:
            index['categories'][category] = {
                'learnings': [],
                'total_count': 0,
                'category_score': 0.0,
                'top_topics': [],
                'related_specializations': []
            }
        
        index['categories'][category]['learnings'].append(learning_data)
        index['categories'][category]['total_count'] += 1
    
    # Calculate category scores and top topics
    for category, data in index['categories'].items():
        data['category_score'] = calculate_category_score(data['learnings'])
        data['top_topics'] = extract_top_topics(data['learnings'])
        data['related_specializations'] = map_specializations(category)
    
    return index


def detect_category(file_path: Path) -> str:
    """Detect learning category from filename and content."""
    filename = file_path.name.lower()
    
    if 'security' in filename:
        return 'security'
    elif 'hn_' in filename:
        return 'tech_news'
    elif 'tldr_' in filename:
        return 'developer_news'
    elif 'github_trending' in filename:
        return 'trending_projects'
    
    return 'general'
```

---

## 3. Workflow Specifications

### 3.1 Dormant Agent Activation Workflow

**File:** `.github/workflows/activate-dormant-agents.yml`

```yaml
name: Activate Dormant Agents

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  activate-agents:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Find dormant agents
        id: find-dormant
        run: |
          python tools/find_dormant_agents.py
      
      - name: Match to learnings
        id: match
        run: |
          python tools/assign_learning_based_work.py \
            --agents "${{ steps.find-dormant.outputs.agent_list }}" \
            --create-issues
      
      - name: Update world state
        run: |
          python world/world_state_manager.py update-assignments \
            --assignments "${{ steps.match.outputs.assignments }}"
      
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add world/world_state.json
          git commit -m "Update world state with new agent assignments" || exit 0
          git push
```

### 3.2 Investment Tracking Workflow

**File:** `.github/workflows/track-agent-investments.yml`

```yaml
name: Track Agent Investments

on:
  issues:
    types: [closed]
  pull_request:
    types: [closed]

jobs:
  track-investment:
    if: github.event.pull_request.merged == true || github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Extract agent and learning
        id: extract
        run: |
          python tools/extract_issue_metadata.py \
            --issue-number ${{ github.event.issue.number || github.event.pull_request.number }}
      
      - name: Update investment level
        run: |
          python world/world_state_manager.py track-investment \
            --agent-id "${{ steps.extract.outputs.agent_id }}" \
            --learning-id "${{ steps.extract.outputs.learning_id }}" \
            --increment 10
      
      - name: Generate ideas if threshold met
        run: |
          python tools/idea_generator.py \
            --agent-id "${{ steps.extract.outputs.agent_id }}" \
            --threshold 50
```

---

## 4. GitHub Pages Updates

### 4.1 Enhanced World Map

**File:** `docs/world-map.js`

```javascript
// NEW: Render learning investment connections
function renderLearningInvestments(agents, learningCatalog) {
    const svg = d3.select('#world-map-svg');
    
    agents.forEach(agent => {
        if (!agent.learning_investments) return;
        
        agent.learning_investments.forEach(investment => {
            // Find learning location
            const learning = learningCatalog.find(l => 
                l.category === investment.category
            );
            
            if (!learning || !learning.origin_region) return;
            
            const agentPos = projection([
                agent.location.lng, 
                agent.location.lat
            ]);
            const learningPos = projection([
                learning.origin_region.lng,
                learning.origin_region.lat
            ]);
            
            // Draw connection line
            svg.append('line')
                .attr('x1', agentPos[0])
                .attr('y1', agentPos[1])
                .attr('x2', learningPos[0])
                .attr('y2', learningPos[1])
                .attr('stroke', getCategoryColor(investment.category))
                .attr('stroke-width', investment.level / 25)
                .attr('opacity', 0.6)
                .attr('class', 'investment-connection');
        });
    });
}

// NEW: Render collaboration requests
function renderCollaborations(agents) {
    agents.forEach(agent => {
        if (!agent.collaboration_requests) return;
        
        agent.collaboration_requests.forEach(collab => {
            const otherAgent = agents.find(a => 
                a.id === collab.requester_id || a.id === collab.specialist_id
            );
            
            if (!otherAgent) return;
            
            // Draw dotted line for collaboration
            drawDottedConnection(agent, otherAgent, collab.status);
        });
    });
}
```

### 4.2 New Page: Agent Investments

**File:** `docs/agent-investments.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Agent Learning Investments | Chained</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>🎯 Agent Learning Investments</h1>
        
        <div id="investment-dashboard">
            <!-- Agent cards with investment levels -->
            <div class="agent-card" data-agent-id="agent-123">
                <h3>🔒 Moxie Marlinspike</h3>
                <p class="specialization">secure-specialist</p>
                
                <div class="investments">
                    <div class="investment-bar">
                        <label>Security</label>
                        <div class="bar" style="width: 75%">75%</div>
                    </div>
                    <div class="investment-bar">
                        <label>Infrastructure</label>
                        <div class="bar" style="width: 40%">40%</div>
                    </div>
                </div>
                
                <div class="stats">
                    <span>📚 12 learnings processed</span>
                    <span>💡 5 ideas generated</span>
                </div>
            </div>
        </div>
        
        <div id="category-explorer">
            <!-- Browse by learning category -->
        </div>
    </div>
    
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="agent-investments.js"></script>
</body>
</html>
```

---

## 5. Integration Points

### 5.1 Registry → World State
- Agent spawn triggers world state update
- New agent gets initial location based on specialization
- Learning affinities pre-calculated

### 5.2 Learnings → World State
- Learning indexer runs hourly
- New learnings added to catalog
- Region learning categories updated

### 5.3 Issues → Investments
- Issue closure triggers investment tracking
- Agent's investment level increases
- Ideas generated at threshold milestones

### 5.4 World State → GitHub Pages
- World state synced to `docs/data/world_state.json`
- Pages refresh data every 5 minutes
- Real-time updates via SSE (future enhancement)

---

## 6. Migration Strategy

### Phase 1: Schema Updates
1. Update `world_state.json` with new fields (backward compatible)
2. Add default empty arrays for existing agents
3. Test schema validation

### Phase 2: Indexer Deployment
1. Run learning indexer manually
2. Validate output
3. Enable automated workflow

### Phase 3: Matching Engine
1. Deploy matching API
2. Test with sample agents
3. Create first assignments

### Phase 4: UI Updates
1. Update world map visualization
2. Deploy new pages
3. Test interactions

### Phase 5: Full Activation
1. Activate dormant agent workflow
2. Monitor first assignments
3. Iterate based on feedback

---

## 7. Testing Strategy

### Unit Tests
- Affinity calculation accuracy
- Learning category detection
- Investment level updates
- Collaboration request creation

### Integration Tests
- End-to-end agent assignment
- World state consistency
- Conflict resolution
- Issue creation workflow

### Performance Tests
- Matching 50 agents to 1000 learnings
- World state update concurrency
- Page load with 100+ agents
- Map rendering performance

---

## 8. Monitoring & Observability

### Metrics to Track
- Agent activation rate (dormant → active)
- Learning assignment success rate
- Investment level distribution
- Collaboration request completion rate
- Idea generation rate
- Page load times
- API response times

### Dashboards
- Agent activation dashboard
- Investment heatmap
- Collaboration network graph
- Learning utilization metrics

---

**Technical Spec Version:** 1.0  
**Status:** Ready for Implementation  
**Maintained by:** @meta-coordinator
