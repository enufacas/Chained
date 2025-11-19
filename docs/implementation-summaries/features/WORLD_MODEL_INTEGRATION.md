# World Model Integration - Agent Mission Tracking

## Overview

The autonomous pipeline now fully integrates with the world model to track agent mission assignments. This provides complete visibility into which agents are working on which missions, their status, and synchronizes this information to GitHub Pages for public visibility.

## Architecture

### 1. World State Schema Enhancement

Agents in `world/world_state.json` now include:

```json
{
  "id": "agent-123",
  "label": "🧹 Robert Martin",
  "specialization": "organize-guru",
  "status": "working",  // Changed from "exploring" when assigned
  "current_idea_id": "idea:cloud-security-001",
  "current_mission": {
    "mission_id": "idea:cloud-security-001",
    "title": "Implement Cloud Security Best Practices",
    "issue_number": 1234,
    "assigned_at": "2025-11-16T09:00:00Z"
  },
  "metrics": {
    "issues_resolved": 1,
    "prs_merged": 0,
    "overall_score": 0.43
  }
}
```

### 2. New Functions in world_state_manager.py

#### `update_agent_mission()`
```python
def update_agent_mission(
    state: Dict[str, Any],
    agent_id: str,           # Agent ID or specialization
    mission_id: str,         # Mission/idea ID
    mission_title: str,      # Human-readable title
    issue_number: int        # GitHub issue number (optional)
) -> bool
```

**What it does:**
- Finds agent by ID or specialization
- Changes status from `"exploring"` to `"working"`
- Sets `current_idea_id` to mission ID
- Adds `current_mission` with full details
- Returns True if successful

**Example:**
```python
success = update_agent_mission(
    world_state,
    "organize-guru",
    "idea:refactor-001",
    "Refactor Authentication Module",
    issue_number=1234
)
```

#### `clear_agent_mission()`
```python
def clear_agent_mission(
    state: Dict[str, Any],
    agent_id: str
) -> bool
```

**What it does:**
- Changes status back to `"exploring"`
- Removes `current_mission` metadata
- Called when mission is completed or abandoned

### 3. Pipeline Integration

#### Stage 4: Create Agent Missions
```yaml
- name: Update world state with agent missions
  run: |
    # For each mission:
    for mission in missions:
        agent_spec = mission['agent']['specialization']
        success = update_agent_mission(
            world_state,
            agent_spec,
            mission['idea_id'],
            mission['idea_title'],
            issue_number
        )
```

**What happens:**
1. Missions are created with agent assignments
2. Each agent's world state is updated immediately
3. Changes are committed to `world/world_state.json`
4. PR is created with world updates

#### Stage 4.5: Merge Mission PR
- Auto-merges the mission PR
- World state changes are now in `main` branch

#### Stage 4.9: Sync World State to Docs (NEW!)
```yaml
- name: Sync world state to docs
  run: |
    mkdir -p docs/world
    cp world/world_state.json docs/world/
    cp world/knowledge.json docs/world/
```

**What happens:**
1. Pulls latest `world_state.json` from `main` (now includes missions)
2. Copies to `docs/world/` for GitHub Pages
3. Creates PR for docs sync
4. Auto-merges to publish

#### Stage 4.95: Merge Docs Sync PR (NEW!)
- Waits for docs sync PR to merge
- World state now visible on GitHub Pages

## Benefits

### 1. Complete Traceability
- Know exactly which agent is working on what
- See mission start times
- Track issue numbers linked to agents
- Monitor agent workload distribution

### 2. Public Visibility
- `docs/world/world_state.json` updated automatically
- GitHub Pages dashboard can display active missions
- Real-time agent status visible to users
- Transparency into autonomous system operations

### 3. Performance Metrics
- Can calculate time-to-completion per agent
- Track which agents complete missions fastest
- Measure success rates by agent type
- Identify bottlenecks in agent work

### 4. Agent State Management
- Clear distinction between `"exploring"` and `"working"`
- Can identify idle vs. active agents
- Supports load balancing future enhancements
- Enables agent capacity planning

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 4: Create Missions                                    │
│                                                              │
│ 1. Match agents to ideas with diversity                     │
│ 2. Create mission assignments                               │
│ 3. Update world_state.json:                                 │
│    • agent.status = "working"                               │
│    • agent.current_mission = {...}                          │
│ 4. Create PR with world changes                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Stage 4.5: Merge Mission PR                                 │
│                                                              │
│ • Mission PR merged to main                                 │
│ • world_state.json updated in main branch                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Stage 4.75: Assign to GitHub Issues                         │
│                                                              │
│ • Use GitHub Copilot to assign agents                       │
│ • Update issue with agent directive                         │
│ • Link issue to mission                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Stage 4.9: Sync to Docs (NEW!)                              │
│                                                              │
│ 1. Pull latest world_state.json from main                   │
│ 2. Copy to docs/world/world_state.json                      │
│ 3. Create docs sync PR                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ Stage 4.95: Merge Docs Sync PR (NEW!)                       │
│                                                              │
│ • Auto-merge docs PR                                        │
│ • GitHub Pages rebuilds with latest world state             │
│ • Public can see active agent missions                      │
└─────────────────────────────────────────────────────────────┘
```

## Example Usage

### Scenario: 5 Missions Created

**Input:**
```json
[
  {
    "idea_id": "idea:cloud-1",
    "idea_title": "Cloud Security Implementation",
    "agent": {
      "specialization": "cloud-architect",
      "agent_name": "Cloud Architect"
    }
  },
  // ... 4 more missions
]
```

**Stage 4 Output (world_state.json):**
```json
{
  "tick": 39,
  "time": "2025-11-16T09:30:00Z",
  "agents": [
    {
      "specialization": "cloud-architect",
      "status": "working",
      "current_idea_id": "idea:cloud-1",
      "current_mission": {
        "mission_id": "idea:cloud-1",
        "title": "Cloud Security Implementation",
        "issue_number": 1234,
        "assigned_at": "2025-11-16T09:30:00Z"
      }
    },
    // ... 4 more agents with missions
  ],
  "metrics": {
    "active_missions": 5
  }
}
```

**Stage 4.9 Output (docs/world/world_state.json):**
- Identical to world_state.json
- Now accessible via GitHub Pages
- Public dashboard can render agent missions

## Querying Agent Status

### Find agents currently working:
```python
working_agents = [
    agent for agent in world_state['agents']
    if agent.get('status') == 'working'
]
```

### Find agents with specific mission type:
```python
security_agents = [
    agent for agent in world_state['agents']
    if 'current_mission' in agent
    and 'security' in agent['current_mission']['title'].lower()
]
```

### Calculate agent workload:
```python
workload = {
    agent['specialization']: {
        'status': agent['status'],
        'has_mission': 'current_mission' in agent,
        'mission': agent.get('current_mission', {}).get('title', 'None')
    }
    for agent in world_state['agents']
}
```

## Future Enhancements

### 1. Mission History Tracking
Store completed missions in agent history:
```json
{
  "mission_history": [
    {
      "mission_id": "idea:cloud-1",
      "title": "Cloud Security",
      "started_at": "2025-11-16T09:00:00Z",
      "completed_at": "2025-11-17T15:30:00Z",
      "issue_number": 1234,
      "outcome": "completed"
    }
  ]
}
```

### 2. Load Balancing
Prevent assigning new missions to overloaded agents:
```python
def get_agent_workload(agent):
    if agent['status'] == 'exploring':
        return 0.0
    elif 'current_mission' in agent:
        return 1.0
    return 0.5

# Prefer agents with lower workload
agent_scores[agent] *= (1.0 - get_agent_workload(agent) * 0.3)
```

### 3. Time-to-Completion Metrics
Track how long missions take:
```python
mission_duration = completed_at - assigned_at
agent['metrics']['avg_mission_duration'] = calculate_avg(
    agent['mission_history']
)
```

### 4. Mission Dependencies
Track if missions depend on others:
```json
{
  "current_mission": {
    "depends_on": ["idea:setup-1", "idea:auth-2"],
    "blocking": ["idea:deploy-5"]
  }
}
```

## Testing

### Unit Tests
```python
# test_world_state_updates.py
def test_update_agent_mission():
    state = load_world_state()
    agent = state['agents'][0]
    
    success = update_agent_mission(
        state,
        agent['id'],
        "test-mission-001",
        "Test Mission",
        9999
    )
    
    assert success
    assert agent['status'] == 'working'
    assert 'current_mission' in agent
```

### Integration Tests
```bash
# Simulate full workflow
python3 test_world_state_updates.py

# Expected output:
# ✅ Agent updated by ID
# ✅ Agent updated by specialization
# ✅ Agent mission cleared
# ✅ Full workflow simulation: 2/2 agents updated
```

## Monitoring

### Check Active Missions
```bash
jq '.metrics.active_missions' world/world_state.json
# Output: 5
```

### List Working Agents
```bash
jq '.agents[] | select(.status == "working") | {spec: .specialization, mission: .current_mission.title}' world/world_state.json
```

### Verify Docs Sync
```bash
diff world/world_state.json docs/world/world_state.json
# Should show no differences after Stage 4.95
```

## Troubleshooting

### Agent Not Updated
**Problem:** `update_agent_mission()` returns False

**Solution:**
1. Check if agent exists in world_state.json
2. Verify agent ID or specialization is correct
3. Use fallback agents (they won't be in world_state but still work)

### Docs Out of Sync
**Problem:** `docs/world/world_state.json` doesn't match `world/world_state.json`

**Solution:**
1. Check if Stage 4.9 ran successfully
2. Verify Stage 4.95 merged the docs PR
3. Re-run docs sync manually if needed:
   ```bash
   cp world/world_state.json docs/world/
   git add docs/world/
   git commit -m "Manual docs sync"
   ```

### Mission Not Showing on GitHub Pages
**Problem:** Agent missions not visible on public site

**Solution:**
1. Ensure GitHub Pages is enabled
2. Check if `docs/world/world_state.json` exists
3. Verify GitHub Pages build succeeded
4. Wait 1-2 minutes for Pages to rebuild

## Conclusion

The world model integration provides complete visibility into agent activities, enabling:
- Real-time tracking of agent work
- Public transparency via GitHub Pages
- Performance analytics and metrics
- Future enhancements for load balancing and optimization

This completes the autonomous pipeline's integration with the world model, ensuring all agent activities are properly tracked and visible across the entire system.
