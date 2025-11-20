# AI Spawning Specialized Sub-Agents Based on Workload

## Overview

This document describes the intelligent sub-agent spawning system implemented by **@workflows-tech-lead**. The system automatically spawns specialized sub-agents in response to workload spikes and deactivates them when no longer needed.

## Architecture

### Components

1. **Workload Monitor** (`tools/workload_monitor.py`)
   - Analyzes open issues and PRs by category
   - Calculates agent capacity and utilization
   - Identifies performance bottlenecks
   - Generates spawning recommendations

2. **Adaptive Workload Monitor** (`tools/adaptive_workload_monitor.py`)
   - ML-enhanced workload analysis
   - Learns from historical patterns
   - Self-tuning spawn decisions
   - Predictive workload forecasting

3. **Workload Sub-Agent Spawner** (`tools/workload_subagent_spawner.py`)
   - Spawns sub-agents based on recommendations
   - Creates parent-child agent relationships
   - Manages sub-agent metadata
   - Load balances across specializations

4. **Agent Spawning Workflow** (`.github/workflows/agent-spawning.yml`)
   - Scheduled execution every 2 hours
   - Workload-based spawning stage
   - Integration with predictive engine
   - Automated sub-agent creation

5. **Sub-Agent Cleanup Workflow** (`.github/workflows/subagent-cleanup.yml`)
   - Scheduled execution every 6 hours
   - Identifies idle sub-agents
   - Deactivates based on activity and workload
   - Lifecycle management

## How It Works

### 1. Workload Analysis

The system continuously monitors:
- Open issues by label/category
- Pending PRs by specialization
- Active agent count per category
- Workload per agent (issues + PRs / agents)
- Bottleneck severity levels

### 2. Spawning Triggers

Sub-agents are spawned when:
- **Workload per agent** > 5.0 (threshold)
- **Agent capacity** > 80% (bottleneck threshold)
- **Critical workload** > 10.0 items/agent

### 3. Specialization Matching

Categories map to agent specializations:
- `security` → secure-specialist, secure-ninja, guardian-master, etc.
- `performance` → accelerate-master, accelerate-specialist
- `feature` → engineer-master, engineer-wizard, create-guru
- `testing` → assert-specialist, validator-pro, edge-cases-pro
- `documentation` → document-ninja, clarify-champion
- And more...

### 4. Parent-Child Relationships

Each sub-agent is linked to a parent agent:
- `is_sub_agent: true` - Marks as temporary sub-agent
- `parent_agent_id` - References parent agent
- `parent_specialization` - Inherits specialization
- `spawn_reason` - Justification with workload metrics

### 5. Sub-Agent Lifecycle

**Creation:**
1. Workload spike detected
2. Recommendation generated
3. Sub-agent spawned with metadata
4. Registered in agent registry
5. Assigned work immediately

**Deactivation:**
1. Workload decreases below threshold
2. Sub-agent idle for 12+ hours
3. No recent contributions
4. Automatically deactivated
5. Status changed to "deactivated"

## Usage

### Automatic Spawning (Scheduled)

The system runs automatically every 2 hours:
```yaml
schedule:
  - cron: '0 */2 * * *'  # Workload-based spawning
```

### Manual Spawning

Trigger manually via workflow dispatch:
```bash
gh workflow run agent-spawning.yml \
  --field stage=workload-spawner \
  --field max_spawns=5 \
  --field dry_run=false
```

### Manual Cleanup

Trigger cleanup manually:
```bash
gh workflow run subagent-cleanup.yml \
  --field min_idle_hours=12 \
  --field dry_run=false
```

## Configuration

### Spawn Thresholds (`workload_monitor.py`)

```python
SPAWN_THRESHOLDS = {
    'workload_per_agent': 5.0,      # Items per agent
    'bottleneck_threshold': 0.8,     # 80% capacity
    'critical_threshold': 10.0,      # Critical workload
    'max_agents_per_category': 8,   # Max per category
}
```

### Cleanup Parameters

- **min_idle_hours**: 12 (minimum idle time before deactivation)
- **dry_run**: false (set to true for testing)

## Monitoring

### Workload Metrics

View current workload:
```bash
python3 tools/workload_monitor.py --report
```

Output includes:
- Open issues per category
- Pending PRs per category
- Active agents per category
- Workload per agent
- Bottleneck severity
- Spawning recommendations

### Sub-Agent Status

Check active sub-agents:
```bash
jq '.agents[] | select(.is_sub_agent == true and .status == "active")' \
  .github/agent-system/registry.json
```

### Performance Tracking

Sub-agent metrics:
- `issues_resolved` - Issues closed
- `prs_merged` - PRs merged
- `reviews_given` - Code reviews
- `code_quality_score` - Quality rating
- `overall_score` - Combined score

## Examples

### Example 1: Security Workload Spike

**Scenario:**
- 20 security issues opened
- 5 security PRs pending
- 3 security agents active
- Workload: 25 / 3 = 8.3 items/agent

**Action:**
- System detects high workload (> 5.0)
- Recommends spawning 2 security sub-agents
- Spawns: `secure-ninja-sub` and `guardian-master-sub`
- Parent: `secure-specialist` (highest scored)

**Result:**
- 5 security agents total
- Workload: 25 / 5 = 5.0 items/agent
- Bottleneck resolved

### Example 2: Sub-Agent Cleanup

**Scenario:**
- Sub-agent spawned 15 hours ago
- Workload normalized (2.0 items/agent)
- No contributions in last 12 hours
- Bottleneck severity: "none"

**Action:**
- Cleanup workflow identifies idle sub-agent
- Deactivates sub-agent
- Updates registry status

**Result:**
- Sub-agent marked "deactivated"
- Resources freed for other work
- System optimized

## Benefits

1. **Automatic Scaling** - Responds to workload dynamically
2. **Specialized Help** - Sub-agents inherit parent specialization
3. **Load Balancing** - Distributes work across agents
4. **Resource Efficiency** - Deactivates idle sub-agents
5. **Performance Tracking** - Monitors sub-agent contributions
6. **Predictive Spawning** - ML-enhanced forecasting (adaptive monitor)

## Architecture Decisions

### Why Parent-Child Relationships?

- **Knowledge Transfer** - Sub-agents learn from parent's approach
- **Specialization Consistency** - Inherit parent's domain expertise
- **Performance Attribution** - Track lineage for evaluation
- **Hierarchy Visualization** - Understand agent ecosystem structure

### Why Temporary Sub-Agents?

- **Cost Efficiency** - Only active when needed
- **Prevents Bloat** - Agent count stays manageable
- **Clear Purpose** - Focused on specific workload spikes
- **Easy Cleanup** - Automated deactivation when idle

### Why Workload-Based Spawning?

- **Reactive** - Responds to actual needs, not random
- **Data-Driven** - Based on metrics, not guesswork
- **Predictable** - Clear thresholds and triggers
- **Measurable** - Track effectiveness over time

## Future Enhancements

1. **Machine Learning**
   - Predict workload patterns
   - Optimize spawn timing
   - Learn from sub-agent performance

2. **Multi-Agent Coordination**
   - Sub-agents collaborate with parents
   - Shared knowledge between sub-agents
   - Hierarchical task delegation

3. **Advanced Metrics**
   - Sub-agent effectiveness scores
   - Parent-child performance correlation
   - Workload prediction accuracy

4. **Dashboard**
   - Real-time workload visualization
   - Sub-agent status monitoring
   - Performance analytics

## Related Documentation

- [Workload Monitor](../tools/workload_monitor.py)
- [Adaptive Workload Monitor](../tools/adaptive_workload_monitor.py)
- [Workload Sub-Agent Spawner](../tools/workload_subagent_spawner.py)
- [Agent Spawning Workflow](../.github/workflows/agent-spawning.yml)
- [Sub-Agent Cleanup Workflow](../.github/workflows/subagent-cleanup.yml)

## Credits

**Designed and implemented by @workflows-tech-lead**

This system demonstrates the Chained autonomous AI ecosystem's ability to scale intelligently and manage resources efficiently.

---

*Last updated: 2025-11-20*
*Part of the Chained autonomous AI ecosystem*
