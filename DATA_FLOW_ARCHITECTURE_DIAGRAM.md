# Data Flow Architecture Diagram

**Author**: @investigate-champion  
**Purpose**: Visual representation of data flow gaps in agent evaluation system

---

## Current State Architecture

### Three-Tier Data Storage System

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              DATA STORAGE LAYERS                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: Primary Storage (Source of Truth)                                  │
│ Location: .github/agent-system/registry.json                                │
│ Updated By: agent-evaluator.yml, agent-spawner.yml                          │
│ Access: Direct file I/O via registry_manager.py                             │
│                                                                              │
│  {                                                                           │
│    "agents": [...],                                                          │
│    "hall_of_fame": [...],                                                    │
│    "metadata": {...},                                                        │
│    "config": {...}                                                           │
│  }                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ ⚠️ GAP: PR merge delay
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: Public Storage (GitHub Pages)                                      │
│ Location: docs/data/agents/agent-registry.json                              │
│ Updated By: agent-data-sync.yml (on push to main)                           │
│ Access: HTTPS (https://enufacas.github.io/Chained/data/)                    │
│                                                                              │
│  - Used by web UI visualizations                                            │
│  - Used by external tools/dashboards                                         │
│  - Can be hours behind Layer 1                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: World Model (Agent Environment)                                    │
│ Location: world/world_state.json                                            │
│ Updated By: world-update.yml, sync_agents_to_world.py                       │
│ Access: Direct file I/O by agent navigation tools                           │
│                                                                              │
│  {                                                                           │
│    "agents": [... with locations ...],                                       │
│    "regions": [...],                                                         │
│    "tick": 42,                                                               │
│    "metrics": {...}                                                          │
│  }                                                                           │
│                                                                              │
│  - Contains spatial navigation data                                          │
│  - Synced independently from evaluation                                      │
│  - May have stale agent metrics                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Temporal Flow: Agent Evaluation Lifecycle

```
TIME: T₀ (Midnight UTC - Daily Schedule)
┌─────────────────────────────────────────────────────────────────────────────┐
│ AGENT EVALUATOR WORKFLOW BEGINS                                             │
│ .github/workflows/agent-evaluator.yml                                       │
└─────────────────────────────────────────────────────────────────────────────┘
  │
  ├─ Step 1: Collect Metrics
  │    └─ Uses: tools/agent-metrics-collector.py
  │    └─ Reads: GitHub API (issues, PRs, commits, reviews)
  │    └─ Calculates: code_quality, creativity, overall_score
  │
  ├─ Step 2: Evaluate Agents
  │    └─ Loads: .github/agent-system/registry.json
  │    └─ Updates: agent['metrics']['overall_score']
  │    └─ Decisions: promote, eliminate, maintain
  │
  ├─ Step 3: Update Registry (In Memory)
  │    └─ Updates: registry['agents'], registry['hall_of_fame']
  │    └─ Saves: to temporary /tmp/evaluation_results.json
  │    └─ ⚠️ NOT YET IN MAIN BRANCH
  │
  ├─ Step 4: Sync to GitHub Pages (Premature)
  │    └─ Copies: registry.json → docs/data/agents/agent-registry.json
  │    └─ ⚠️ PROBLEM: This sync is in PR branch, not yet in main
  │
  └─ Step 5: Create Pull Request
       └─ Branch: agent-evaluation/YYYYMMDD-HHMMSS
       └─ Commits: registry.json + docs/data/ changes
       └─ ⚠️ EXITS WITHOUT WAITING FOR MERGE

TIME: T₁ (Minutes to Hours Later - Manual/Automated Review)
┌─────────────────────────────────────────────────────────────────────────────┐
│ PULL REQUEST REVIEW PERIOD                                                  │
│ ⏰ Duration: Unpredictable (could be 1 hour, could be 24 hours)             │
└─────────────────────────────────────────────────────────────────────────────┘
  │
  │ During this time:
  │  - Data exists in PR branch
  │  - Main branch has OLD data
  │  - Other workflows reading from main see STALE metrics
  │  - Agents spawning/executing use OUTDATED scores
  │
  └─ ⚠️ CRITICAL GAP: System operates with stale data

TIME: T₂ (After Review Approval)
┌─────────────────────────────────────────────────────────────────────────────┐
│ PULL REQUEST MERGED TO MAIN                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
  │
  └─ Changes now in main branch
  └─ .github/agent-system/registry.json updated ✓
  └─ docs/data/agents/agent-registry.json updated ✓
  └─ Triggers: agent-data-sync.yml workflow

TIME: T₃ (Immediately After Merge)
┌─────────────────────────────────────────────────────────────────────────────┐
│ AGENT DATA SYNC WORKFLOW                                                    │
│ .github/workflows/agent-data-sync.yml                                       │
└─────────────────────────────────────────────────────────────────────────────┘
  │
  ├─ Step 1: Read registry.json (from main)
  ├─ Step 2: Write to docs/data/
  │    └─ docs/data/agent-registry.json
  │    └─ docs/data/agents/*.json (individual files)
  │
  └─ Step 3: Create ANOTHER Pull Request
       └─ Branch: agent-data-sync/YYYYMMDD-HHMMSS
       └─ ⚠️ PROBLEM: Second PR creates more delay

TIME: T₄ (More Waiting...)
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECOND PULL REQUEST REVIEW                                                  │
│ ⏰ Duration: More unpredictable time                                         │
└─────────────────────────────────────────────────────────────────────────────┘
  │
  └─ ⚠️ COMPOUNDING DELAY: Now waiting for second PR to merge

TIME: T₅ (After Second Merge)
┌─────────────────────────────────────────────────────────────────────────────┐
│ SECOND PR MERGED                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
  │
  └─ docs/data/ now updated in main
  └─ GitHub Pages deploys new data
  └─ Web UI shows fresh metrics ✓

TIME: T₆ (Sometime Later - Manual Trigger)
┌─────────────────────────────────────────────────────────────────────────────┐
│ WORLD UPDATE WORKFLOW                                                        │
│ .github/workflows/world-update.yml (workflow_dispatch only)                 │
└─────────────────────────────────────────────────────────────────────────────┘
  │
  ├─ Step 1: Sync agents to world
  │    └─ Reads: .github/agent-system/registry.json
  │    └─ Updates: world/world_state.json
  │    └─ Syncs: Agent metrics, positions, status
  │
  ├─ Step 2: Sync learnings to ideas
  │    └─ Converts: learnings/ → world/knowledge.json
  │
  └─ Step 3: Create THIRD Pull Request
       └─ Branch: world-update/YYYYMMDD-HHMMSS
       └─ ⚠️ PROBLEM: Third PR, more delay

TOTAL TIME: T₀ → T₇ (After All Merges)
═══════════════════════════════════════════════════════════════════════════════
LATENCY: 2-48 hours (depending on review/merge speed)
═══════════════════════════════════════════════════════════════════════════════
```

## Data Dependency Graph

```
┌──────────────────────┐
│  GitHub API          │  (Issues, PRs, Commits, Reviews)
│  (External Source)   │
└──────────┬───────────┘
           │
           │ Read (via GH_TOKEN)
           ▼
┌──────────────────────┐
│ agent-metrics-       │
│ collector.py         │  Calculates performance scores
└──────────┬───────────┘
           │
           │ Metrics
           ▼
┌──────────────────────────────────────────────────┐
│ agent-evaluator.yml                              │
│ - Evaluates agents                               │
│ - Promotes/eliminates based on thresholds        │
│ - Updates registry.json                          │
└──────────┬───────────────────────────────────────┘
           │
           │ Creates PR (DELAY)
           ▼
┌──────────────────────────────────────────────────┐
│ .github/agent-system/registry.json               │ ◄── SOURCE OF TRUTH
│ (After PR merge to main)                         │
└──┬────────┬────────────────────────────────────┬─┘
   │        │                                     │
   │        │ Read                                │ Read
   │        ▼                                     ▼
   │ ┌──────────────────┐            ┌──────────────────────┐
   │ │ agent-data-sync  │            │ world-update.yml     │
   │ │ .yml             │            │ (Manual trigger)     │
   │ └────────┬─────────┘            └──────────┬───────────┘
   │          │                                  │
   │          │ Creates PR (DELAY)               │ Creates PR (DELAY)
   │          ▼                                  ▼
   │ ┌──────────────────────┐        ┌─────────────────────┐
   │ │ docs/data/           │        │ world/              │
   │ │ agent-registry.json  │        │ world_state.json    │
   │ │ agents/*.json        │        │ knowledge.json      │
   │ └──────────┬───────────┘        └─────────┬───────────┘
   │            │                               │
   │            │ Published to                  │ Read by
   │            ▼                               ▼
   │ ┌──────────────────────┐        ┌─────────────────────┐
   │ │ GitHub Pages         │        │ Agent Navigation    │
   │ │ (Web UI)             │        │ Tools               │
   │ └──────────────────────┘        └─────────────────────┘
   │
   │ Also read by (from main branch):
   │
   ├─► agent-spawner.yml (reads registry for capacity checks)
   ├─► agent-missions.yml (reads registry for agent assignment)
   ├─► Other workflows that need agent data
   │
   └─► ⚠️ ALL READ STALE DATA DURING PR PERIODS

```

## Gap Analysis: Before vs After

### Current State (With Gaps)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ EVALUATION @ T₀                                                          │
│ - Agents scored                                                          │
│ - Results in PR branch                                                   │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │ ⏰ HOURS PASS
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PR MERGED @ T₂                                                           │
│ - Registry updated                                                       │
│ - But docs/ not yet synced                                               │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │ ⏰ MORE HOURS PASS
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ SECOND PR MERGED @ T₄                                                    │
│ - Docs synced                                                            │
│ - But world not yet updated                                              │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │ ⏰ MANUAL TRIGGER NEEDED
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ WORLD UPDATED @ T₆                                                       │
│ - Finally, all systems in sync                                           │
│ - Agents can now operate with fresh data                                 │
└─────────────────────────────────────────────────────────────────────────┘

TOTAL LATENCY: 2-48 hours
```

### Desired State (Gaps Closed)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ EVALUATION @ T₀                                                          │
│ - Agents scored                                                          │
│ - Results saved                                                          │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │ Immediate (atomic update)
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ALL SYSTEMS UPDATED @ T₀+1min                                            │
│ - Registry updated                                                       │
│ - Docs synced                                                            │
│ - World updated                                                          │
│ - Single PR with all changes                                             │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │ Auto-merge (with checks)
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PR MERGED @ T₀+5min                                                      │
│ - All systems in sync                                                    │
│ - Agents immediately see fresh data                                      │
└─────────────────────────────────────────────────────────────────────────┘

TOTAL LATENCY: 5-10 minutes
```

## Consistency Problem

### Distributed System Without Transactions

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Registry       │     │   Docs/Pages     │     │   World Model    │
│   (Primary)      │     │   (Public)       │     │   (Agent Env)    │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         │ @ T₀                   │                        │
         │ Score: 0.45            │                        │
         │ Status: Active         │                        │
         │                        │                        │
         ▼                        │                        │
    Updated to:                   │                        │
    Score: 0.28                   │ @ T₂ (still old)      │ @ T₃ (still old)
    Status: Eliminated            │ Score: 0.45           │ Score: 0.45
                                  │ Status: Active        │ Status: Active
                                  ▼                        │
                             Updated to:                   │
                             Score: 0.28                   │ @ T₃ (still old)
                             Status: Eliminated            │ Score: 0.45
                                                           │ Status: Active
                                                           ▼
                                                      Updated to:
                                                      Score: 0.28
                                                      Status: Eliminated

⚠️ PROBLEM: Between T₀ and T₃, the system is in an inconsistent state
   - Agent is eliminated in registry
   - But appears active in docs and world
   - Other agents may try to collaborate with "ghost" agent
```

## Proposed Architecture: Unified Data Layer

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED DATA SERVICE                              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ Central Store (Single Source of Truth)                         │    │
│  │ - Manages all agent data                                       │    │
│  │ - Provides versioned, atomic updates                           │    │
│  │ - Guarantees consistency across views                          │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Exposed via multiple views:                                            │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │ File View    │  │ HTTP View    │  │ World View   │                 │
│  │ (registry)   │  │ (GitHub Pg)  │  │ (spatial)    │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ All views          │ synchronized       │ automatically
         ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ Registry │        │   Docs   │        │  World   │
   │  Files   │        │  Files   │        │  Files   │
   └──────────┘        └──────────┘        └──────────┘
```

## Summary: Key Insights

1. **Three-tier storage** creates consistency challenges
2. **PR-based workflow** introduces 2-48 hour delays
3. **Multiple PRs** compound latency problems
4. **No atomicity** means inconsistent states between updates
5. **Manual world sync** decouples evaluation from environment updates

**@investigate-champion** recommends:
- Consolidate syncs into single workflow
- Implement auto-merge for faster propagation
- Add version numbers for consistency checks
- Consider unified data service in future

---

*Architectural analysis by @investigate-champion*
