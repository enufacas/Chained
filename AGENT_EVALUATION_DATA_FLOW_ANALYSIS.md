# Agent Evaluation Data Flow Analysis

**Investigator**: @investigate-champion  
**Date**: 2025-11-15  
**Issue**: Data storage, PR workflow, and world model integration gaps

---

## Executive Summary

**@investigate-champion** has completed a comprehensive investigation of the agent evaluation system's data flow and identified critical gaps in how evaluation data propagates through the autonomous ecosystem. The current system creates a **temporal disconnect** between evaluation execution and data availability, potentially causing agents to operate with stale information.

## Current Architecture

### 1. Data Storage Locations

The system maintains agent data in **three separate locations**:

#### Primary Storage: `.github/agent-system/`
- **Location**: `.github/agent-system/registry.json`
- **Purpose**: Source of truth for agent registry
- **Updated by**: `agent-evaluator.yml`, agent spawning workflows
- **Structure**: Distributed system with individual agent files
- **Access**: Direct file access via registry_manager.py

#### Secondary Storage: `docs/data/`
- **Location**: `docs/data/agents/agent-registry.json` and `docs/data/agents/*.json`
- **Purpose**: GitHub Pages publication for web visualization
- **Updated by**: `agent-data-sync.yml` workflow (on push to main)
- **Access**: HTTP requests from GitHub Pages (https://enufacas.github.io/Chained/)
- **Lag**: Only updates AFTER PR merge to main branch

#### Tertiary Storage: `world/`
- **Location**: `world/world_state.json`
- **Purpose**: World model state for agent spatial navigation
- **Updated by**: `world-update.yml` and `sync_agents_to_world.py`
- **Access**: Python scripts in world/ directory
- **Sync**: Separate workflow, may be out of sync with registry

### 2. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT EVALUATION CYCLE                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  agent-evaluator.yml (Daily at midnight UTC)                    │
│  - Collects metrics via agent-metrics-collector.py             │
│  - Updates .github/agent-system/registry.json                   │
│  - Creates evaluation PR                                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  PR Created   │  ⚠️ GAP: Data not yet in main
                        │  (Branch)     │
                        └───────────────┘
                                │
                                │ ⏰ Time passes (hours? days?)
                                │
                                ▼
                        ┌───────────────┐
                        │  PR Merged    │
                        │  to main      │
                        └───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  agent-data-sync.yml (Triggered by push to main)               │
│  - Syncs registry.json → docs/data/agent-registry.json         │
│  - Creates individual agent JSON files                          │
│  - Creates another PR for docs sync                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  Second PR    │  ⚠️ GAP: More delay
                        │  Created      │
                        └───────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │  Second PR    │
                        │  Merged       │
                        └───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  GitHub Pages (Public Data)                                     │
│  - docs/data/ now available via HTTPS                           │
│  - Web UI shows updated agent data                              │
└─────────────────────────────────────────────────────────────────┘

                        ┌───────────────┐
                        │  world-update │  ⚠️ GAP: Runs independently
                        │  .yml         │
                        └───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  World State Update                                             │
│  - sync_agents_to_world.py reads registry.json                 │
│  - Updates world/world_state.json                               │
│  - Creates third PR for world updates                           │
└─────────────────────────────────────────────────────────────────┘
```

## Identified Gaps

### Gap 1: Temporal Disconnect (Critical)

**Problem**: Evaluation results exist in a PR branch but are not yet part of main branch.

**Impact**:
- During the PR review period (could be hours or days), agents spawning or executing tasks may read stale data
- Registry shows old scores until PR merges
- Agents making decisions based on outdated performance metrics

**Current State**:
```python
# agent-evaluator.yml line 338-349
- name: Commit changes
  run: |
    BRANCH_NAME="agent-evaluation/$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$BRANCH_NAME"
    git add .github/agent-system/
    git add docs/data/agents/agent-registry.json  # ⚠️ This is premature!
    git commit -m "🔄 Daily agent evaluation and governance"
    git push origin "$BRANCH_NAME"
    # ... creates PR but doesn't wait for merge
```

**Evidence**: The workflow creates the PR and exits. No mechanism ensures the PR is merged before other workflows run.

### Gap 2: Multi-Stage PR Process (Performance)

**Problem**: Two separate PRs required for full data propagation.

**Impact**:
- First PR: evaluation results → registry
- Second PR: registry → docs/data (GitHub Pages)
- Total delay: 2x PR review/merge cycles
- Compounding latency in data availability

**Current State**:
```yaml
# agent-evaluator.yml updates registry → PR 1
# agent-data-sync.yml (triggered after PR 1 merges) → PR 2
```

### Gap 3: World Model Desynchronization (Architecture)

**Problem**: World state updates run on a different schedule/trigger than evaluation.

**Impact**:
- `world/world_state.json` may have outdated agent scores
- Agents' world model representation doesn't match registry truth
- Spatial/strategic decisions based on stale metrics

**Current State**:
```yaml
# world-update.yml: workflow_dispatch only (manual trigger)
# No automatic sync after agent evaluations
```

**Code Evidence**:
```python
# world/sync_agents_to_world.py line 136-141
world_agents = []
for reg_agent in registry_agents:
    world_agent = create_world_agent_from_registry(reg_agent)
    # Copies metrics from registry at sync time
    # If registry is old, world gets old data
```

### Gap 4: No Atomic Updates (Consistency)

**Problem**: Updates across three storage locations are not atomic.

**Impact**:
- Registry updated at T0
- Docs synced at T1 (after PR merge)
- World synced at T2 (separate workflow)
- Inconsistent system state during intervals

**Database analogy**: Like updating a distributed database without transactions.

### Gap 5: Missing Feedback Loops (Integration)

**Problem**: Agents don't receive immediate feedback about evaluation results.

**Impact**:
- No notification when promoted/eliminated
- Can't adjust behavior based on metrics in real-time
- Learning loop is delayed

**Example**: An agent eliminated at midnight won't "know" until PR merges (possibly 8+ hours later).

## Value Chain Analysis

### Current Value Chain
```
Evaluation → PR → Human Review → Merge → Docs Sync → PR → Merge → Pages Update
                                                                          ↓
                                                               Agents See New Data
```

**Latency**: 2-24 hours (depending on PR review speed)

### Desired Value Chain
```
Evaluation → Update Registry → Update Docs → Update World → Notify Agents
           └─────────────────┬──────────────────┬─────────────────┘
                             │                  │
                          (Atomic)          (Real-time)
```

**Latency**: Minutes (near real-time)

## Root Cause Analysis

### Why PRs Instead of Direct Commits?

**Answer**: Branch protection rules require PRs for main branch.

**Justification** (from `.github/instructions/branch-protection.instructions.md`):
- Code review for all changes
- CI/CD validation
- Audit trail
- Rollback capability

**Trade-off**: Safety vs. Latency

### Why Separate Syncs?

**Answer**: Different workflows triggered by different events.

**Consequences**:
- agent-evaluator.yml: Scheduled (daily)
- agent-data-sync.yml: Push-triggered (after merge)
- world-update.yml: Manual only

**Problem**: No orchestration between these workflows.

## Recommendations

### High Priority: Reduce PR Latency

**Option A: Auto-merge for automated PRs**
```yaml
# Add to agent-evaluator.yml
- name: Auto-merge evaluation PR
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Wait for CI checks to pass
    gh pr merge "$PR_NUMBER" --auto --squash
```

**Pros**: Maintains PR audit trail, reduces delay to minutes  
**Cons**: Still have delay for CI checks

**Option B: Direct commit on evaluation branch**
```yaml
# Instead of creating PR, push directly to a dedicated evaluation branch
# that agents read from
```

**Pros**: Zero PR delay  
**Cons**: Loses review/validation step

### Medium Priority: Consolidate Syncs

**Recommendation**: Combine agent-data-sync and world-update into agent-evaluator.yml

```yaml
# Add to agent-evaluator.yml after evaluation
- name: Sync all data stores
  run: |
    # Update docs/data
    python3 tools/sync_registry_to_docs.py
    
    # Update world state
    python3 world/sync_agents_to_world.py
    
    # Single commit, single PR for all updates
    git add docs/data/ world/
    git commit -m "Sync evaluation data across all stores"
```

**Benefit**: One PR instead of multiple, atomic updates

### Medium Priority: Real-time Agent Notifications

**Recommendation**: Create notification system for evaluation results

```yaml
# Add to agent-evaluator.yml
- name: Notify affected agents
  run: |
    python3 << 'PYTHON_SCRIPT'
    import json
    
    with open('/tmp/evaluation_results.json', 'r') as f:
        results = json.load(f)
    
    # Create issues for eliminated agents
    for agent in results['eliminated']:
        create_notification_issue(
            agent_id=agent['id'],
            title=f"🚨 Agent {agent['name']} Eliminated",
            body=f"Score: {agent['score']:.2%} - below threshold"
        )
    
    # Create issues for promoted agents
    for agent in results['promoted']:
        create_notification_issue(
            agent_id=agent['id'],
            title=f"🏆 Agent {agent['name']} Promoted to Hall of Fame",
            body=f"Score: {agent['score']:.2%}"
        )
    PYTHON_SCRIPT
```

### Low Priority: World Model as Source of Truth

**Recommendation**: Consider making world state the primary store

**Rationale**: If agents operate in the world model, they should read world data primarily.

**Implementation**: 
```python
# Invert the sync: registry → world (immediate) → docs (async)
# Agents read from world/world_state.json
# GitHub Pages reads from docs/data/ (can lag slightly)
```

### Critical: Data Consistency Guarantees

**Recommendation**: Implement versioning and consistency checks

```python
# Add version numbers to data files
{
  "version": "v123",
  "timestamp": "2025-11-15T00:00:00Z",
  "agents": [...]
}

# Agents check version before making decisions
if world_version < registry_version:
    # Refuse to operate or use fallback
    raise StaleDataError("World model is behind registry")
```

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 hours)
1. Add auto-merge to agent-evaluator.yml for faster propagation
2. Document current latencies in README
3. Add warning to agents: "Data may be up to 24h old"

### Phase 2: Consolidation (3-4 hours)
1. Merge agent-data-sync logic into agent-evaluator.yml
2. Merge world-update logic into agent-evaluator.yml
3. Single PR per evaluation with all data updates

### Phase 3: Real-time Feedback (4-6 hours)
1. Implement notification system for evaluation results
2. Create agent dashboard showing current metrics
3. Add webhook/events for immediate propagation

### Phase 4: Architecture Evolution (1-2 days)
1. Implement versioned data stores
2. Add consistency checks across stores
3. Consider unified data layer (single source of truth)

## Conclusion

**@investigate-champion** has identified that the current agent evaluation system suffers from:

1. **Temporal gaps**: PRs create delays before data becomes "official"
2. **Multi-stage propagation**: Multiple PRs compound latency
3. **Desynchronization**: Three separate data stores update at different times
4. **No atomicity**: Updates are not transactional across stores
5. **Limited feedback**: Agents don't receive immediate evaluation results

The root cause is the **tension between safety (branch protection) and performance (real-time data)**. The system optimizes for safety but at the cost of data freshness.

**Recommendation**: Implement Phase 1 (auto-merge) immediately to reduce latency from hours to minutes while maintaining audit trail. Follow with Phase 2 (consolidation) to eliminate redundant PRs.

The goal is to enable agents to operate with fresh data as part of their environment, which requires closing the gaps in the value chain between evaluation and data availability.

---

**End of Analysis**  
*Conducted by @investigate-champion - Visionary and analytical investigation*
