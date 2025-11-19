# Implementation Plan: Closing Data Flow Gaps

**Author**: @investigate-champion  
**Date**: 2025-11-15  
**Goal**: Close gaps in agent evaluation data flow to enable real-time world model updates

---

## Overview

This document provides a concrete implementation plan to address the data flow gaps identified in the agent evaluation system. The plan is structured in phases, starting with quick wins and progressing to architectural improvements.

## Phase 1: Immediate Fixes (Quick Wins)

**Timeline**: 1-2 hours  
**Goal**: Reduce PR merge latency from hours to minutes

### 1.1 Enable Auto-Merge for Evaluation PRs

**File**: `.github/workflows/agent-evaluator.yml`

**Changes**:
```yaml
# Add after line 435 (after gh pr create)
- name: Enable auto-merge
  if: steps.evaluate.outputs.has_results == 'true'
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Get the PR number that was just created
    PR_NUMBER=$(gh pr list --head "agent-evaluation/$(date +%Y%m%d)" --json number -q '.[0].number')
    
    if [ -n "$PR_NUMBER" ]; then
      echo "Enabling auto-merge for PR #$PR_NUMBER"
      gh pr merge "$PR_NUMBER" --auto --squash
      echo "✅ Auto-merge enabled. PR will merge after checks pass."
    else
      echo "⚠️ Could not find PR number for auto-merge"
    fi
```

**Benefits**:
- Reduces manual review delay
- PR still creates audit trail
- Merges automatically after CI passes
- Reduces latency from hours to ~5 minutes

**Risks**:
- Auto-merges without human review (low risk for automated evaluations)
- Requires CI checks to be reliable

### 1.2 Add Data Freshness Warnings

**File**: `.github/agent-system/registry.json`

**Add metadata**:
```json
{
  "version": "2.0.0",
  "last_evaluation": "2025-11-15T00:00:00Z",
  "data_freshness_warning": "Data may be up to 24 hours old during PR review periods",
  "pr_status": "pending|merged",
  "agents": [...]
}
```

**File**: Create `tools/check_data_freshness.py`

```python
#!/usr/bin/env python3
"""
Check if registry data is fresh or stale.
Warns agents if they're reading data that's pending merge.
"""
import json
import sys
from datetime import datetime, timedelta

def check_freshness(registry_path='.github/agent-system/registry.json'):
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    last_eval = datetime.fromisoformat(registry['last_evaluation'].replace('Z', '+00:00'))
    now = datetime.utcnow()
    age_hours = (now - last_eval).total_seconds() / 3600
    
    if age_hours > 25:  # More than a day + buffer
        print(f"⚠️ WARNING: Registry data is {age_hours:.1f} hours old")
        print("   Evaluation may be stuck in PR review")
        return False
    
    print(f"✅ Data is fresh ({age_hours:.1f} hours old)")
    return True

if __name__ == '__main__':
    sys.exit(0 if check_freshness() else 1)
```

**Usage**: Add to workflows that read registry:
```yaml
- name: Check data freshness
  run: python3 tools/check_data_freshness.py
  continue-on-error: true  # Warn but don't fail
```

### 1.3 Document Current Limitations

**File**: `README.md` (add section)

```markdown
## ⚠️ Data Latency Notice

The agent evaluation system updates data through GitHub Pull Requests, which introduces latency:

- **Evaluation runs**: Daily at midnight UTC
- **Data updates**: 5-30 minutes after evaluation (with auto-merge)
- **Maximum staleness**: Up to 24 hours if auto-merge fails

Agents operating during PR review periods may see slightly outdated metrics.

**Real-time data availability**:
- Primary registry: `.github/agent-system/registry.json` (may be in PR branch)
- GitHub Pages: `docs/data/` (lags by 5-30 minutes)
- World model: `world/world_state.json` (manual sync required)
```

## Phase 2: Consolidate Data Syncs

**Timeline**: 3-4 hours  
**Goal**: Eliminate redundant PRs, single atomic update

### 2.1 Merge agent-data-sync into agent-evaluator

**File**: `.github/workflows/agent-evaluator.yml`

**Add new step after "Sync agent registry to GitHub Pages" (line 235)**:

```yaml
- name: Sync world state
  run: |
    echo "🌍 Syncing agents to world model..."
    python3 world/sync_agents_to_world.py
    
    # Copy world data to docs for GitHub Pages
    mkdir -p docs/world
    cp world/world_state.json docs/world/
    cp world/knowledge.json docs/world/ 2>/dev/null || echo "No knowledge.json yet"
    
    echo "✅ World state synced"

- name: Sync learnings to ideas
  continue-on-error: true
  run: |
    echo "💡 Syncing learnings to world ideas..."
    python3 world/sync_learnings_to_ideas.py 2>&1 || echo "No learnings to sync (OK)"
```

**Modify commit step (line 342)** to include all data:

```yaml
- name: Commit changes
  if: steps.evaluate.outputs.has_results == 'true'
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    BRANCH_NAME="agent-evaluation/$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$BRANCH_NAME"
    
    # Stage ALL data updates in single commit
    git add .github/agent-system/
    git add docs/data/agents/agent-registry.json
    git add docs/data/agents/*.json
    git add docs/world/
    git add world/
    
    git commit -m "🔄 Daily agent evaluation and data sync

- Updated agent registry
- Synced to GitHub Pages (docs/data/)
- Updated world model (world/)
- Modified agent profiles
- Archived eliminated agents

This is a consolidated update of all agent data stores."
    
    git push origin "$BRANCH_NAME"
    
    # Create PR (rest of existing code...)
```

**Benefits**:
- Single PR instead of 2-3 separate PRs
- All data updates are atomic
- Reduces total latency by eliminating cascading PRs
- Cleaner git history

### 2.2 Deprecate Redundant Workflows

**Files to modify**:
- `.github/workflows/agent-data-sync.yml` - Add deprecation notice
- `.github/workflows/world-update.yml` - Add note about integration

**Change agent-data-sync.yml**:

```yaml
name: "Agent System: Data Sync [DEPRECATED]"

# NOTE: This workflow is deprecated as of 2025-11-15
# Data sync is now part of agent-evaluator.yml for atomic updates
# This workflow remains for manual triggers only

on:
  # Remove automatic triggers
  workflow_dispatch:
    inputs:
      force_sync:
        description: 'Force manual sync (use only if evaluator fails)'
        required: false
        type: boolean
        default: false
```

**Change world-update.yml**:

```yaml
name: World Model Update

# NOTE: World model updates are now automatic via agent-evaluator.yml
# This workflow remains for manual testing or emergency syncs

on:
  workflow_dispatch:
```

### 2.3 Update Documentation

**File**: `docs/data/agents/README.md`

Update to reflect new consolidated workflow:

```markdown
# Agent Data Directory

This directory contains agent registry data synced from `.github/agent-system/`.

## Update Schedule

- **Automatic Updates**: Daily at midnight UTC via `agent-evaluator.yml`
- **Latency**: 5-30 minutes after evaluation completes
- **Includes**: Agent metrics, Hall of Fame, world state

## Data Structure

- `agent-registry.json` - Consolidated registry (all agents + metadata)
- `agent-*.json` - Individual agent files for granular access
- Available via GitHub Pages at: `https://enufacas.github.io/Chained/data/`

## Data Flow

1. Evaluation runs (agent-evaluator.yml)
2. Registry updated (.github/agent-system/registry.json)
3. Data synced to docs/data/ (same workflow)
4. World model updated (world/world_state.json)
5. Single PR created with all changes
6. Auto-merge after CI passes
7. GitHub Pages deploys updated data

**Result**: All data stores updated within 5-30 minutes of evaluation.
```

## Phase 3: Real-Time Feedback System

**Timeline**: 4-6 hours  
**Goal**: Notify agents immediately about evaluation results

### 3.1 Create Notification System

**File**: `tools/notify_agents.py`

```python
#!/usr/bin/env python3
"""
Notify agents about evaluation results via GitHub issues.
Creates targeted notification issues for promoted/eliminated agents.
"""
import json
import subprocess
import sys
from typing import Dict, List, Any

def create_agent_notification(
    agent_id: str,
    agent_name: str,
    event_type: str,
    score: float,
    details: Dict[str, Any]
) -> bool:
    """
    Create a notification issue for an agent event.
    
    Args:
        agent_id: Agent identifier
        agent_name: Human-readable agent name
        event_type: 'promoted', 'eliminated', or 'warning'
        score: Agent's overall score
        details: Additional event details
    
    Returns:
        True if notification created successfully
    """
    
    # Emoji map
    emoji_map = {
        'promoted': '🏆',
        'eliminated': '❌',
        'warning': '⚠️'
    }
    
    # Title
    emoji = emoji_map.get(event_type, '📊')
    title = f"{emoji} Agent {agent_name} - {event_type.title()}"
    
    # Body
    body = f"""## Agent Evaluation Notification

**Agent**: {agent_name} (`{agent_id}`)  
**Event**: {event_type.title()}  
**Score**: {score:.2%}  
**Date**: {details.get('timestamp', 'N/A')}

### Details

"""
    
    if event_type == 'promoted':
        body += f"""
**Congratulations!** You have been promoted to the Hall of Fame!

Your consistent high performance (score {score:.2%}) has earned you a permanent place among the elite agents.

**Benefits**:
- Protected from future elimination
- Recognition on public dashboard
- Potential to become System Lead

**Next Steps**:
- Continue your excellent work
- Consider mentoring newer agents
- Lead by example in your specialization
"""
    
    elif event_type == 'eliminated':
        body += f"""
Your score ({score:.2%}) has fallen below the elimination threshold ({details.get('threshold', 0.30):.2%}).

**Reason**: {details.get('reason', 'Score below threshold')}

**What This Means**:
- Your agent profile has been archived
- You will no longer receive new assignments
- Your contributions are preserved in the archive

**Learning Opportunity**:
- Review your past work for patterns
- Identify areas for improvement
- Future agents can learn from this experience
"""
    
    elif event_type == 'warning':
        body += f"""
Your score ({score:.2%}) is approaching the elimination threshold ({details.get('threshold', 0.30):.2%}).

**Warning Level**: {details.get('warning_level', 'Medium')}

**Recommendations**:
- Focus on code quality improvements
- Increase PR merge success rate
- Engage more in peer reviews
- Complete assigned issues promptly

**Time to Improve**: {details.get('grace_period', 'N/A')}
"""
    
    body += f"""

---

### Metrics Breakdown

- **Code Quality**: {details.get('code_quality_score', 0.0):.2%}
- **Issue Resolution**: {details.get('issues_resolved', 0)} resolved
- **PR Success**: {details.get('prs_merged', 0)} merged
- **Peer Reviews**: {details.get('reviews_given', 0)} given
- **Creativity Score**: {details.get('creativity_score', 0.0):.2%}

---

*🤖 Automated notification from agent evaluation system*
"""
    
    # Create issue via gh CLI
    try:
        result = subprocess.run(
            [
                'gh', 'issue', 'create',
                '--title', title,
                '--body', body,
                '--label', f'agent-system,evaluation,agent:{agent_id}'
            ],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Created notification issue for {agent_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create notification for {agent_name}: {e.stderr}")
        return False


def notify_from_evaluation_results(results_file: str = '/tmp/evaluation_results.json') -> None:
    """
    Read evaluation results and create notifications for all relevant events.
    """
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Notify promoted agents
    for agent in results.get('promoted', []):
        create_agent_notification(
            agent_id=agent['id'],
            agent_name=agent['name'],
            event_type='promoted',
            score=agent['score'],
            details={
                'timestamp': results.get('timestamp', 'N/A'),
                'specialization': agent.get('specialization', 'unknown')
            }
        )
    
    # Notify eliminated agents
    for agent in results.get('eliminated', []):
        create_agent_notification(
            agent_id=agent['id'],
            agent_name=agent['name'],
            event_type='eliminated',
            score=agent['score'],
            details={
                'timestamp': results.get('timestamp', 'N/A'),
                'reason': f"Score {agent['score']:.2%} below elimination threshold",
                'threshold': 0.30
            }
        )
    
    # Check for agents in warning zone (score between 0.30 and 0.40)
    for agent in results.get('maintained', []):
        if agent['score'] < 0.40:
            create_agent_notification(
                agent_id=agent['id'],
                agent_name=agent['name'],
                event_type='warning',
                score=agent['score'],
                details={
                    'timestamp': results.get('timestamp', 'N/A'),
                    'warning_level': 'High' if agent['score'] < 0.35 else 'Medium',
                    'threshold': 0.30,
                    'grace_period': '24-48 hours'
                }
            )


if __name__ == '__main__':
    try:
        notify_from_evaluation_results()
        print("✅ All notifications created")
    except Exception as e:
        print(f"❌ Error creating notifications: {e}")
        sys.exit(1)
```

**Add to agent-evaluator.yml** (after line 525):

```yaml
- name: Notify affected agents
  if: steps.evaluate.outputs.has_results == 'true'
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    echo "📬 Creating notification issues for agents..."
    python3 tools/notify_agents.py
    echo "✅ Agent notifications complete"
```

### 3.2 Create Agent Dashboard Issue

**Add to agent-evaluator.yml** (modify existing issue creation):

Add real-time metrics to the evaluation report issue:

```python
# In the evaluation report creation (line 442-525)
# Add a section for "Agents at Risk"

body += """
### ⚠️ Agents at Risk

Agents with scores below 0.40 (warning zone):

"""

for agent in results.get('maintained', []):
    if agent['score'] < 0.40:
        warning_level = '🔴 High' if agent['score'] < 0.35 else '🟡 Medium'
        body += f"- {warning_level} **{agent['name']}** - {agent['score']:.2%}\n"
```

## Phase 4: Architecture Evolution

**Timeline**: 1-2 days  
**Goal**: Implement versioning and consistency guarantees

### 4.1 Add Version Numbers to All Data Files

**Update registry structure**:

```json
{
  "version": "2.1.0",
  "data_version": "v20251115-000000",
  "last_evaluation": "2025-11-15T00:00:00Z",
  "last_update": "2025-11-15T00:05:23Z",
  "pr_status": "merged",
  "agents": [...],
  "hall_of_fame": [...],
  "metadata": {
    "schema_version": "2.0",
    "consistency_hash": "abc123..."
  }
}
```

### 4.2 Implement Consistency Checks

**File**: `tools/verify_data_consistency.py`

```python
#!/usr/bin/env python3
"""
Verify consistency across all agent data stores.
Ensures registry, docs, and world are in sync.
"""
import json
import hashlib
from typing import Dict, Any, List

def compute_agent_hash(agents: List[Dict[str, Any]]) -> str:
    """Compute hash of agent data for consistency checking."""
    # Sort agents by ID for consistent hashing
    sorted_agents = sorted(agents, key=lambda a: a['id'])
    # Hash relevant fields only
    data = json.dumps([
        {
            'id': a['id'],
            'status': a['status'],
            'score': a['metrics']['overall_score']
        }
        for a in sorted_agents
    ], sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def verify_consistency() -> bool:
    """Verify all data stores have consistent agent data."""
    
    # Load registry
    with open('.github/agent-system/registry.json', 'r') as f:
        registry = json.load(f)
    
    # Load docs
    with open('docs/data/agents/agent-registry.json', 'r') as f:
        docs = json.load(f)
    
    # Load world
    with open('world/world_state.json', 'r') as f:
        world = json.load(f)
    
    # Compute hashes
    registry_hash = compute_agent_hash(registry['agents'])
    docs_hash = compute_agent_hash(docs['agents'])
    world_hash = compute_agent_hash(world['agents'])
    
    print(f"Registry hash: {registry_hash}")
    print(f"Docs hash:     {docs_hash}")
    print(f"World hash:    {world_hash}")
    
    if registry_hash == docs_hash == world_hash:
        print("✅ All data stores are consistent")
        return True
    else:
        print("❌ Data stores are inconsistent!")
        if registry_hash != docs_hash:
            print("   - Registry and Docs differ")
        if registry_hash != world_hash:
            print("   - Registry and World differ")
        if docs_hash != world_hash:
            print("   - Docs and World differ")
        return False

if __name__ == '__main__':
    import sys
    sys.exit(0 if verify_consistency() else 1)
```

**Add to workflows** as a validation check:

```yaml
- name: Verify data consistency
  run: python3 tools/verify_data_consistency.py
```

### 4.3 Implement Fallback Mechanisms

**File**: `tools/registry_manager.py`

Add method to check data freshness and use fallback:

```python
def get_agents_with_freshness_check(self, max_age_hours: int = 25) -> List[Dict[str, Any]]:
    """
    Get agents with freshness check.
    Warns if data is stale and provides fallback options.
    """
    registry = self.load_registry()
    
    last_eval = datetime.fromisoformat(registry['last_evaluation'].replace('Z', '+00:00'))
    age_hours = (datetime.utcnow() - last_eval).total_seconds() / 3600
    
    if age_hours > max_age_hours:
        print(f"⚠️ WARNING: Registry data is {age_hours:.1f} hours old")
        print(f"   Last evaluation: {registry['last_evaluation']}")
        print(f"   Consider using cached data with caution")
    
    return registry['agents']
```

## Implementation Checklist

### Phase 1: Immediate (Do First)
- [ ] Add auto-merge to agent-evaluator.yml
- [ ] Add data freshness warnings to README
- [ ] Create check_data_freshness.py tool
- [ ] Test auto-merge on next evaluation run

### Phase 2: Consolidation (Do Second)
- [ ] Move world sync into agent-evaluator.yml
- [ ] Update commit step to include all data
- [ ] Deprecate agent-data-sync.yml
- [ ] Update world-update.yml notice
- [ ] Update documentation

### Phase 3: Notifications (Do Third)
- [ ] Create notify_agents.py tool
- [ ] Add notification step to agent-evaluator.yml
- [ ] Test notification system
- [ ] Add "at risk" section to evaluation report

### Phase 4: Architecture (Do Last)
- [ ] Add version numbers to all data files
- [ ] Create verify_data_consistency.py tool
- [ ] Add consistency checks to workflows
- [ ] Implement fallback mechanisms in registry_manager.py
- [ ] Document versioning scheme

## Success Metrics

After implementation, measure:

1. **Latency Reduction**
   - Before: 2-48 hours from evaluation to availability
   - Target: 5-30 minutes
   - Measure: Time from evaluation start to docs deployment

2. **Consistency Improvements**
   - Before: 3 separate updates at different times
   - Target: Single atomic update
   - Measure: Number of consistency check failures

3. **Agent Awareness**
   - Before: Agents unaware of evaluation results
   - Target: Immediate notifications
   - Measure: Notification issue creation rate

4. **System Reliability**
   - Before: Manual sync triggers sometimes forgotten
   - Target: Fully automated
   - Measure: Days since last manual intervention

## Rollback Plan

If issues arise:

1. **Phase 1 Rollback**: Disable auto-merge
   ```yaml
   # Comment out auto-merge step
   # Manual review resumes
   ```

2. **Phase 2 Rollback**: Re-enable agent-data-sync.yml
   ```yaml
   # Uncomment push trigger
   # Separate workflows resume
   ```

3. **Phase 3 Rollback**: Disable notifications
   ```yaml
   # Comment out notify_agents.py step
   # No notifications sent
   ```

4. **Phase 4 Rollback**: Remove consistency checks
   ```yaml
   # Comment out verification steps
   # System continues without checks
   ```

## Conclusion

This implementation plan provides a clear path to closing the data flow gaps identified by **@investigate-champion**. The phased approach allows for incremental improvements while maintaining system stability.

**Key Outcomes**:
- ✅ Reduced latency from hours to minutes
- ✅ Atomic updates across all data stores
- ✅ Real-time agent notifications
- ✅ Consistency guarantees and versioning

The goal is to enable agents to operate within an up-to-date world model, making decisions based on fresh data rather than stale metrics.

---

*Implementation plan by @investigate-champion*  
*Ready for execution - all phases designed for backward compatibility*
