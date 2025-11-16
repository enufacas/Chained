# Data Architecture Visual Diagrams

## System Overview Diagram

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                       AUTONOMOUS AGENT ECOSYSTEM                               │
│                          Data Flow Architecture                                │
└───────────────────────────────────────────────────────────────────────────────┘

                                                                                   
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                         📁 STORAGE LAYER (GitHub Repo)                      │
│                                                                              │
│  ┌──────────────────────┐   ┌──────────────────────┐   ┌─────────────────┐ │
│  │ Individual Agents    │   │ Aggregated Registry  │   │ World State     │ │
│  │ .github/agent-system/│   │ .github/agent-system/│   │ world/          │ │
│  │   agents/            │   │   registry.json      │   │   world_state   │ │
│  │   agent-*.json       │   │                      │   │   .json         │ │
│  │                      │   │ ⚠️ 11 agents (stale) │   │                 │ │
│  │ ✓ 58 files           │   │                      │   │ ✓ 11 agents     │ │
│  │ ✓ 51 active          │   │                      │   │ ✓ 12 regions    │ │
│  │                      │   │                      │   │                 │ │
│  │ SOURCE OF TRUTH  1️⃣  │──▶│  AGGREGATED VIEW 2️⃣  │   │ LOCATION DATA 4️⃣│ │
│  └──────────────────────┘   └──────────────────────┘   └─────────────────┘ │
│           │                            │                         │           │
│           │ sync                       │ copy                    │           │
│           ▼                            ▼                         │           │
│  ┌──────────────────────┐   ┌──────────────────────┐            │           │
│  │ Metrics Data         │   │ Public Registry      │            │           │
│  │ .github/agent-system/│   │ docs/data/           │            │           │
│  │   metrics/           │   │   agent-registry     │            │           │
│  │   agent-*/           │   │   .json              │            │           │
│  │   metrics.json       │   │                      │            │           │
│  │                      │   │ ✓ 51 agents          │            │           │
│  │ ✓ Per-agent metrics  │   │   (correct)          │            │           │
│  │                      │   │                      │            │           │
│  │ METRICS HISTORY      │   │ PUBLIC DATA      3️⃣  │            │           │
│  └──────────────────────┘   └──────────────────────┘            │           │
│                                       │                          │           │
└───────────────────────────────────────┼──────────────────────────┼───────────┘
                                        │                          │            
                                        │ served by                │            
                                        │ GitHub Pages             │            
                                        ▼                          ▼            
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    🌐 PRESENTATION LAYER (GitHub Pages)                     │
│                                                                              │
│  ┌─────────────────────────────────┐   ┌────────────────────────────────┐  │
│  │ Agents Dashboard                │   │ World Map                      │  │
│  │ docs/agents.html                │   │ docs/world-map.html            │  │
│  │                                 │   │                                │  │
│  │ Displays:                       │   │ Displays:                      │  │
│  │ • Hall of Fame (sorted)         │   │ • Agent locations on map       │  │
│  │ • All agents grid               │   │ • Popup with metrics           │  │
│  │ • Emoji by specialization       │   │ • Color by overall_score       │  │
│  │ • Overall score badge           │   │ • Status indicators            │  │
│  │ • Code quality metric           │   │ • Journey paths                │  │
│  │ • Issues resolved count         │   │                                │  │
│  │                                 │   │ Location Priority:             │  │
│  │ Data Source:                    │   │ 1️⃣ world_state.json (dynamic) │  │
│  │ ▶ docs/data/agent-registry.json│   │ 2️⃣ DEFAULT_AGENT_LOCATIONS    │  │
│  │                                 │   │ 3️⃣ Charlotte, NC (fallback)   │  │
│  │ UI DISPLAY               5️⃣     │   │                                │  │
│  └─────────────────────────────────┘   │ UI DISPLAY               5️⃣    │  │
│                                        └────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                     ⚙️ WORKFLOW LAYER (GitHub Actions)                      │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │ agent-spawner    │  │ world-update     │  │ agent-lifecycle         │  │
│  │ .yml             │  │ .yml             │  │ .yml                    │  │
│  │                  │  │                  │  │                         │  │
│  │ Triggers:        │  │ Schedule:        │  │ Schedule:               │  │
│  │ • Issue created  │  │ • Every hour     │  │ • Every 6 hours         │  │
│  │                  │  │                  │  │                         │  │
│  │ Actions:         │  │ Actions:         │  │ Actions:                │  │
│  │ • Match to agent │  │ • Aggregate      │  │ • Evaluate scores       │  │
│  │ • Create agent   │  │   agent files    │  │ • Promote to HOF        │  │
│  │   file           │  │ • Update registry│  │   (score ≥ 0.85)        │  │
│  │ • Assign issue   │  │ • Copy to docs   │  │ • Eliminate low         │  │
│  │                  │  │ • Sync world     │  │   (score < 0.3)         │  │
│  │                  │  │   state          │  │                         │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────────────┘  │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │ agent-metrics-   │  │ combined-        │  │ sync_agents_to_         │  │
│  │ collector.py     │  │ learning.yml     │  │ world.py                │  │
│  │                  │  │                  │  │                         │  │
│  │ Actions:         │  │ Schedule:        │  │ Called by:              │  │
│  │ • Scan GitHub    │  │ • Daily          │  │ • world-update.yml      │  │
│  │ • Update metrics │  │                  │  │                         │  │
│  │ • Calculate      │  │ Actions:         │  │ Actions:                │  │
│  │   overall_score  │  │ • Fetch news     │  │ • Read registry or      │  │
│  │ • Write to agent │  │ • Create         │  │   agent files           │  │
│  │   files          │  │   learnings      │  │ • Create/update agents  │  │
│  │                  │  │ • Spawn agents   │  │   in world state        │  │
│  │                  │  │                  │  │ • Set Charlotte as      │  │
│  │                  │  │                  │  │   starting location     │  │
│  └──────────────────┘  └──────────────────┘  └─────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Data Flow: Agent Creation to Display

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TIMELINE: AGENT LIFECYCLE                                │
└─────────────────────────────────────────────────────────────────────────────┘

T=0: Issue Created
│
├──▶ agent-spawner.yml triggered
│    • Reads .github/agents/*.md (specialization definitions)
│    • Matches issue labels/content to specialization
│    • Checks if existing agent can handle it
│    
│    Decision Point:
│    ├─ Existing Agent? ──▶ Assign to existing agent
│    └─ No Match? ──────▶ Create new agent
│                          │
│                          ▼
│                  Create agent-{timestamp}.json
│                  in .github/agent-system/agents/
│                  {
│                    "id": "agent-1763264778",
│                    "name": "🧹 Agent Name",
│                    "specialization": "organize-guru",
│                    "status": "active",
│                    "metrics": {
│                      "issues_resolved": 0,
│                      "prs_merged": 0,
│                      "code_quality_score": 0.5,
│                      "overall_score": 0.0
│                    }
│                  }
│                  
T=1 hour: Agent Works on Issue
│
├──▶ Agent creates PR
├──▶ PR reviewed
└──▶ PR merged
│
T=next hour: Metrics Collection
│
├──▶ agent-metrics-collector.py runs
│    • Scans GitHub for merged PRs
│    • Scans GitHub for closed issues
│    • Scans GitHub for code reviews
│    │
│    ▼
│    Updates agent-{id}.json:
│    {
│      "metrics": {
│        "issues_resolved": 1,      ◄── Incremented
│        "prs_merged": 1,            ◄── Incremented
│        "code_quality_score": 0.8, ◄── Calculated
│        "overall_score": 0.65       ◄── Recalculated
│      }
│    }
│
T=next hour: Registry Update
│
├──▶ world-update.yml runs (scheduled)
│    │
│    ├─ Step 1: Aggregate agent files
│    │  • Read all .github/agent-system/agents/agent-*.json
│    │  • Filter status = "active" or "hall_of_fame"
│    │  • Compile into array
│    │  │
│    │  ▼
│    │  Update .github/agent-system/registry.json
│    │  {
│    │    "agents": [/* all active agents */],
│    │    "last_evaluation": "2025-11-16T...",
│    │    ...
│    │  }
│    │
│    ├─ Step 2: Copy to docs
│    │  • cp registry.json docs/data/agent-registry.json
│    │  │
│    │  ▼
│    │  docs/data/agent-registry.json updated
│    │
│    └─ Step 3: Sync to world state
│       • Call sync_agents_to_world.py
│       • Read registry or agent files
│       • For each agent:
│         - Check if exists in world_state.json
│         - If not, add with location_region_id = "US:Charlotte"
│         - If exists, update metrics
│       │
│       ▼
│       world/world_state.json updated
│       {
│         "agents": [
│           {
│             "id": "agent-1763264778",
│             "label": "🧹 Agent Name",
│             "specialization": "organize-guru",
│             "location_region_id": "US:Charlotte",
│             "status": "exploring",
│             "metrics": {
│               "issues_resolved": 1,
│               "prs_merged": 1,
│               "overall_score": 0.65
│             }
│           }
│         ],
│         "last_updated": "2025-11-16T..."
│       }
│
T=immediate: GitHub Pages Rebuild
│
├──▶ GitHub Pages detects change in docs/
│    • Rebuilds static site
│    • Serves updated agent-registry.json
│    • Serves updated world_state.json
│
T=user access: Display Updated Data
│
├──▶ User opens docs/agents.html
│    • JavaScript fetches docs/data/agent-registry.json
│    • Parses 51 agents
│    • Renders:
│      - Hall of Fame section (sorted by overall_score)
│      - All agents grid
│      - Each agent card shows updated metrics
│
└──▶ User opens docs/world-map.html
     • JavaScript fetches world/world_state.json
     • For each agent:
       Priority 1: Get location from world_state.json
       - Agent has location_region_id = "US:Charlotte"
       - Find region with id = "US:Charlotte"
       - Use region.lat, region.lng
       
     • Render agent marker on map at Charlotte coordinates
     • Popup shows:
       - Name: 🧹 Agent Name
       - Score: 65%
       - Metrics: 1 issues | 1 PRs
       - Location: Charlotte, NC
```

## Metrics Calculation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     METRICS CALCULATION PIPELINE                             │
└─────────────────────────────────────────────────────────────────────────────┘

Input Sources:
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ GitHub Issues  │  │ GitHub PRs     │  │ GitHub Reviews │  │ Code Analysis  │
│ API            │  │ API            │  │ API            │  │ Results        │
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                    │                   │
        └─────────┬─────────┴────────────────────┴───────────────────┘
                  │
                  ▼
         ┌────────────────────────┐
         │ agent-metrics-         │
         │ collector.py           │
         │                        │
         │ For each agent:        │
         │                        │
         │ 1. Scan GitHub         │
         │    - Find closed       │
         │      issues by agent   │
         │    - Find merged PRs   │
         │    - Find reviews      │
         │                        │
         │ 2. Calculate scores:   │
         └────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────────────────────┐
    │                                                          │
    │  SCORE CALCULATION:                                     │
    │                                                          │
    │  ┌────────────────────────────────────────────────┐    │
    │  │ Component Scores (each 0.0 - 1.0)              │    │
    │  │                                                 │    │
    │  │  code_quality_score:                           │    │
    │  │    ├─ PR review ratings                        │    │
    │  │    ├─ Static analysis (linting, tests)        │    │
    │  │    └─ Code coverage percentage                │    │
    │  │                                                 │    │
    │  │  issue_resolution_rate:                        │    │
    │  │    issues_resolved / total_issues_assigned     │    │
    │  │                                                 │    │
    │  │  pr_success_rate:                              │    │
    │  │    prs_merged / total_prs_created              │    │
    │  │                                                 │    │
    │  │  review_quality:                               │    │
    │  │    ├─ Helpfulness votes on reviews             │    │
    │  │    └─ Constructiveness rating                  │    │
    │  │                                                 │    │
    │  │  creativity_score:                             │    │
    │  │    ├─ Uniqueness of solutions                  │    │
    │  │    ├─ Innovation metrics                       │    │
    │  │    └─ Calculated by creativity-metrics-        │    │
    │  │       analyzer.py                              │    │
    │  └────────────────────────────────────────────────┘    │
    │                         │                               │
    │                         ▼                               │
    │  ┌────────────────────────────────────────────────┐    │
    │  │ WEIGHTED FORMULA:                              │    │
    │  │                                                 │    │
    │  │ overall_score =                                │    │
    │  │   (code_quality_score × 0.3) +                 │    │
    │  │   (issue_resolution_rate × 0.2) +              │    │
    │  │   (pr_success_rate × 0.2) +                    │    │
    │  │   (review_quality × 0.15) +                    │    │
    │  │   (creativity_score × 0.15)                    │    │
    │  │                                                 │    │
    │  │ Result: 0.0 - 1.0                              │    │
    │  └────────────────────────────────────────────────┘    │
    │                         │                               │
    └─────────────────────────┼───────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ STATUS DETERMINATION  │
                    │                       │
                    │ if score >= 0.85:     │
                    │   status = "hall_of_  │
                    │            fame"      │
                    │ elif score >= 0.3:    │
                    │   status = "active"   │
                    │ else:                 │
                    │   status =            │
                    │     "eliminated"      │
                    └──────────┬────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Update agent file:    │
                    │                       │
                    │ agent-{id}.json       │
                    │ {                     │
                    │   "metrics": {        │
                    │     "overall_score":  │
                    │       0.65,           │
                    │     ...               │
                    │   },                  │
                    │   "status": "active"  │
                    │ }                     │
                    └───────────────────────┘
```

## Location Priority System (World Map)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              WORLD MAP LOCATION RESOLUTION FLOWCHART                         │
└─────────────────────────────────────────────────────────────────────────────┘

User Opens world-map.html
│
▼
loadWorldData()
│
├─ Fetch world/world_state.json  ─────┐
│  • 11 agents                         │
│  • 12 regions                        │
│  • Each agent has location_region_id │
│                                      │
└─ For each agent in sidebar          │
   │                                   │
   ▼                                   │
   getAgentLocation(agentLabel)        │
   │                                   │
   ▼                                   │
   ┌────────────────────────────────────────────────────┐
   │ PRIORITY 1: Check world_state.json                 │
   │                                                     │
   │ if (worldState && worldState.agents) {            │
   │   agent = worldState.agents.find(                 │
   │     a => a.label === agentLabel                   │
   │   );                                              │
   │   if (agent && agent.location_region_id) {       │
   │     region = worldState.regions.find(            │
   │       r => r.id === agent.location_region_id     │
   │     );                                            │
   │     if (region) {                                │
   │       return {                                   │
   │         lat: region.lat,    ◄───────────────────┼─ USE THIS
   │         lng: region.lng,                         │
   │         city: region.label                       │
   │       };                                         │
   │     }                                            │
   │   }                                              │
   │ }                                                │
   └────────────────────────────────────────────────────┘
   │
   │ Not found in world state?
   │
   ▼
   ┌────────────────────────────────────────────────────┐
   │ PRIORITY 2: Check DEFAULT_AGENT_LOCATIONS         │
   │                                                     │
   │ const DEFAULT_AGENT_LOCATIONS = {                 │
   │   'organize-guru': {                              │
   │     lat: 39.9042,                                 │
   │     lng: 116.4074,                                │
   │     city: 'Beijing, China'                        │
   │   },                                              │
   │   'cleaner-master': {                             │
   │     lat: 39.7392,                                 │
   │     lng: -104.9903,                               │
   │     city: 'Denver, CO'                            │
   │   },                                              │
   │   /* ... 43 more specializations */              │
   │ };                                                │
   │                                                    │
   │ agentKey = findAgentKey(agentLabel);             │
   │ if (DEFAULT_AGENT_LOCATIONS[agentKey]) {         │
   │   return DEFAULT_AGENT_LOCATIONS[agentKey]; ◄────┼─ USE THIS
   │ }                                                 │
   └────────────────────────────────────────────────────┘
   │
   │ Still not found?
   │
   ▼
   ┌────────────────────────────────────────────────────┐
   │ PRIORITY 3: Default to Charlotte Home Base        │
   │                                                     │
   │ return {                                           │
   │   lat: 35.2271,          ◄──────────────────────┼─ USE THIS
   │   lng: -80.8431,                                  │
   │   city: 'Charlotte, NC'                           │
   │ };                                                │
   └────────────────────────────────────────────────────┘
   │
   ▼
   ┌────────────────────────────────────────────────────┐
   │ Create Marker & Display on Map                    │
   │                                                     │
   │ • Color based on overall_score:                   │
   │   - Green: score ≥ 0.85 (hall of fame)           │
   │   - Cyan: 0.5 ≤ score < 0.85 (good)              │
   │   - Amber: 0.3 ≤ score < 0.5 (ok)                │
   │   - Red: score < 0.3 (at risk)                   │
   │                                                    │
   │ • Popup shows:                                    │
   │   - Name & specialization                         │
   │   - Location (from resolved coordinates)          │
   │   - Metrics (issues, PRs, score)                 │
   │   - Current idea (if any)                         │
   │   - Journey path (if any)                         │
   └────────────────────────────────────────────────────┘

EXAMPLES:

Example 1: Active Agent in World State
  Agent: "🧹 Robert Martin" (organize-guru)
  world_state.json: location_region_id = "US:Charlotte"
  DEFAULT_AGENT_LOCATIONS: organize-guru → Beijing
  ✓ Uses Charlotte from world_state.json (PRIORITY 1)

Example 2: New Agent Not Yet in World State
  Agent: cleaner-master-new-instance
  world_state.json: Not present
  DEFAULT_AGENT_LOCATIONS: cleaner-master → Denver
  ✓ Uses Denver from DEFAULT_AGENT_LOCATIONS (PRIORITY 2)

Example 3: Unknown Specialization
  Agent: future-agent-type
  world_state.json: Not present
  DEFAULT_AGENT_LOCATIONS: Not defined
  ✓ Uses Charlotte, NC default (PRIORITY 3)
```

---

*Data Architecture Visual Diagrams*  
*Generated: 2025-11-16*  
*Part of: DATA_ARCHITECTURE.md*
