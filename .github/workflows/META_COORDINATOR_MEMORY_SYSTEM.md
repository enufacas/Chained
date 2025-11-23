# Meta-Coordinator Memory System

**Created by:** @support-master  
**Date:** 2025-11-23  
**Purpose:** Non-blocking persistent memory for meta-coordinator agent

---

## Overview

The **Meta-Coordinator Memory System** provides persistent, non-blocking storage that enables the meta-coordinator-system agent to:

1. **Learn from history** - Track patterns and outcomes
2. **Make informed decisions** - Use historical context
3. **Avoid mistakes** - Remember what didn't work
4. **Optimize performance** - Identify what works best
5. **Maintain continuity** - Context across workflow runs

## Architecture

### Storage

**File:** `.github/agent-system/meta-coordinator-memory.json`

**Format:** JSON (human-readable and git-trackable)

**Update Strategy:** Atomic writes (non-blocking)
- Write to `.tmp` file first
- Rename to actual file (atomic operation)
- Never blocks workflow execution

### Data Structure

```json
{
  "version": "1.0",
  "created_at": "2025-11-23T00:00:00Z",
  "last_updated": "2025-11-23T06:00:00Z",
  "runs": { ... },
  "pr_patterns": { ... },
  "issue_patterns": { ... },
  "feedback_issues": { ... },
  "exceptions": { ... },
  "decisions": { ... },
  "learnings": { ... },
  "system_health": { ... }
}
```

## Memory Categories

### 1. Run Statistics

Tracks workflow execution metrics:
- Total runs, success/failure counts
- Average duration
- Last run details
- Performance trends

**Use case:** Identify performance degradation, optimize run times

### 2. PR Patterns

Tracks PR processing history:
- Tech leads assigned (by agent)
- Complexity distribution
- Review cycle counts
- Approval times

**Use case:** Learn which tech leads handle which types of PRs best

### 3. Issue Patterns

Tracks issue assignment history:
- Agents assigned (by agent)
- Agent success rates
- Match scores
- Assignment times

**Use case:** Improve agent matching, identify high-performing agents

### 4. Feedback Issues

Tracks feedback issue creation:
- Total created
- By tech lead
- Resolution times
- Duplicates prevented

**Use case:** Prevent duplicate feedback issues, track tech lead patterns

### 5. Exceptions

Tracks handled exceptions:
- By type
- Recent occurrences
- Context for each

**Use case:** Identify recurring issues, improve exception handling

### 6. Decisions

Tracks orchestration decisions:
- Recent decisions (last 100)
- Decision type patterns
- Context and rationale

**Use case:** Audit trail, learn from past decisions

### 7. Learnings

Stores insights and recommendations:
- Insights discovered
- Recommendations for improvements
- Evidence backing each

**Use case:** Continuous improvement, system evolution

### 8. System Health

Tracks overall system state:
- Consistency scores
- Issues detected
- Last health check

**Use case:** Proactive problem detection

## API Usage

### Python API

```python
from tools.meta_coordinator_memory import MetaCoordinatorMemory

# Initialize
memory = MetaCoordinatorMemory()

# Record a run
memory.record_run(
    success=True,
    duration_seconds=240,
    actions_taken=15
)

# Record PR assignment
memory.record_pr_assignment(
    pr_number=456,
    tech_lead="workflows-tech-lead",
    complexity="high",
    files_changed=12
)

# Record issue assignment
memory.record_issue_assignment(
    issue_number=789,
    agent="engineer-master",
    match_score=8.5
)

# Record feedback issue
memory.record_feedback_issue(
    pr_number=456,
    issue_number=790,
    tech_lead="workflows-tech-lead",
    agent="align-wizard"
)

# Record exception
memory.record_exception(
    exception_type="duplicate_feedback",
    description="Prevented duplicate feedback issue",
    context={"pr_number": 456}
)

# Add learning
memory.add_learning(
    insight="Dependabot PRs rarely need tech lead review",
    evidence={"sample_size": 50, "review_rate": 0.02}
)

# Get agent performance
stats = memory.get_agent_performance("engineer-master")

# Get summary
print(memory.get_summary())
```

### CLI Usage

```bash
# Get summary
python3 tools/meta-coordinator-memory.py summary

# Analyze trends
python3 tools/meta-coordinator-memory.py trends

# Get agent stats
python3 tools/meta-coordinator-memory.py agent engineer-master

# Get tech lead stats
python3 tools/meta-coordinator-memory.py tech-lead workflows-tech-lead

# Get recent patterns
python3 tools/meta-coordinator-memory.py patterns

# Get decision context
python3 tools/meta-coordinator-memory.py context pr_assignment
```

## Integration with Meta-Coordinator

### In Workflow

The meta-coordinator workflow should:

1. **Load memory at start** of each run
2. **Use context** for decision-making
3. **Record actions** as they're taken
4. **Save summary** at end of run

### Example Integration

```python
#!/usr/bin/env python3
from tools.meta_coordinator_memory import MetaCoordinatorMemory
import time

# Initialize memory
memory = MetaCoordinatorMemory()
start_time = time.time()
actions_taken = 0

try:
    # Get context for decisions
    pr_context = memory.get_context_for_decision("pr_assignment")
    
    # Use historical patterns to inform decisions
    trends = memory.analyze_trends()
    
    # Process PRs
    for pr in open_prs:
        tech_lead = assign_tech_lead(pr, context=pr_context)
        memory.record_pr_assignment(pr.number, tech_lead, ...)
        actions_taken += 1
    
    # Process issues
    for issue in open_issues:
        # Get agent performance to make better matches
        agent = select_best_agent(issue, memory=memory)
        memory.record_issue_assignment(issue.number, agent, ...)
        actions_taken += 1
    
    # Record successful run
    duration = time.time() - start_time
    memory.record_run(True, duration, actions_taken)
    
    # Generate summary with insights
    print(memory.get_summary())

except Exception as e:
    # Record failure
    memory.record_exception("run_failure", str(e), {})
    memory.record_run(False, time.time() - start_time, actions_taken)
    raise
```

## Benefits

### 1. Context-Aware Decisions

**Before:** Each run starts fresh, no historical context

**After:** Decisions informed by patterns and outcomes

**Example:**
```
Q: Should PR from @dependabot need tech lead review?
Memory: Last 50 dependabot PRs averaged 0.02 review rate
Decision: Skip tech lead review, apply auto-merge label
```

### 2. Learning & Improvement

**Before:** Repeat same mistakes, no optimization

**After:** Learn from patterns, continuously improve

**Example:**
```
Learning: @engineer-master has 95% success on API issues
Memory: Prefer @engineer-master for API-related issues
Result: Better match accuracy, faster resolution
```

### 3. Exception Prevention

**Before:** Repeat exceptions (duplicate issues, conflicts)

**After:** Learn from exceptions, prevent recurrence

**Example:**
```
Memory: PR #456 already has feedback issue #460
Decision: Skip creating duplicate, update existing
Result: Cleaner issue tracker, less confusion
```

### 4. Performance Optimization

**Before:** Unknown bottlenecks, no metrics

**After:** Track performance, identify optimizations

**Example:**
```
Memory: Average run time increased from 4min to 8min
Analysis: More PRs with tech lead labels
Recommendation: Optimize tech lead matching logic
```

### 5. Audit Trail

**Before:** No history of decisions made

**After:** Complete audit trail with rationale

**Example:**
```
Q: Why was @workflows-tech-lead assigned to PR #456?
Memory: Decision at 2025-11-23 14:35:22
Rationale: PR modified .github/workflows/
Result: Tech lead approved in 2 hours
```

## Memory Lifecycle

### Initialization

First run creates empty memory structure:
```bash
.github/agent-system/meta-coordinator-memory.json
```

### Growth

Memory grows with each run:
- Recent items kept (last 50-100)
- Aggregates updated (counts, averages)
- Trends computed (patterns, distributions)

### Maintenance

**Automatic:**
- Old records pruned (keeps recent)
- Aggregates updated incrementally
- File size stays manageable (<100KB)

**Manual (optional):**
- Archive old memory periodically
- Reset for fresh start
- Export for analysis

## Advanced Features

### 1. Trend Analysis

```python
trends = memory.analyze_trends()

# PR complexity distribution
# agent_utilization: which agents get most work
# exception_distribution: what fails most
```

### 2. Performance Tracking

```python
# Track agent success over time
stats = memory.get_agent_performance("engineer-master")

# Track tech lead feedback rates
stats = memory.get_tech_lead_stats("workflows-tech-lead")
```

### 3. Decision Context

```python
# Get relevant history for a decision
context = memory.get_context_for_decision("pr_assignment")

# Recent similar decisions
# Related insights
# Learned patterns
```

### 4. Recommendations

```python
# System generates recommendations
memory.add_recommendation(
    "Consider increasing tech lead review threshold",
    priority="medium"
)

# View pending recommendations
summary = memory.get_summary()
```

## Integration with Agent

Update meta-coordinator-system agent to use memory:

**In agent instructions:**
```markdown
## Using Memory System

Before making decisions:
1. Load memory: `python3 tools/meta-coordinator-memory.py summary`
2. Get relevant context: `memory.get_context_for_decision(type)`
3. Check agent performance: `memory.get_agent_performance(agent)`

While executing:
1. Record each action taken
2. Track exceptions encountered
3. Note patterns observed

At completion:
1. Record run success/failure
2. Add learnings discovered
3. Generate recommendations
4. Post summary with insights
```

## Example Memory Output

```json
{
  "runs": {
    "total_runs": 288,
    "successful_runs": 285,
    "failed_runs": 3,
    "average_duration_seconds": 245.3
  },
  "pr_patterns": {
    "total_prs_processed": 156,
    "tech_leads_assigned": {
      "workflows-tech-lead": 42,
      "docs-tech-lead": 38,
      "secure-specialist": 28
    },
    "complexity_distribution": {
      "low": 98,
      "medium": 42,
      "high": 16
    }
  },
  "learnings": {
    "insights": [
      {
        "insight": "Dependabot PRs rarely need tech lead review (2% rate)",
        "evidence": {"sample_size": 50, "review_rate": 0.02},
        "timestamp": "2025-11-23T12:00:00Z"
      },
      {
        "insight": "@engineer-master has 95% success on API issues",
        "evidence": {"assignments": 40, "successes": 38},
        "timestamp": "2025-11-23T14:00:00Z"
      }
    ]
  }
}
```

## Security & Privacy

**No sensitive data stored:**
- ✅ PR/issue numbers (public)
- ✅ Agent names (public)
- ✅ Timestamps (public)
- ✅ Counts and metrics (public)

**Not stored:**
- ❌ PR/issue content
- ❌ User emails
- ❌ Access tokens
- ❌ Private information

**File permissions:**
- Stored in `.github/agent-system/` (protected directory)
- Only writable by workflows with appropriate permissions
- Readable by all team members for transparency

## Monitoring

### Health Checks

```bash
# Check memory file exists
ls -la .github/agent-system/meta-coordinator-memory.json

# Validate JSON structure
cat .github/agent-system/meta-coordinator-memory.json | jq .

# Check file size (should be < 100KB)
du -h .github/agent-system/meta-coordinator-memory.json

# View recent activity
python3 tools/meta-coordinator-memory.py summary
```

### Metrics to Monitor

- **Memory file size** - Should stay < 100KB
- **Run success rate** - Should stay > 95%
- **Average duration** - Should stay < 10 minutes
- **Exception rate** - Should stay < 5%

## Future Enhancements

Possible extensions:

1. **ML-based predictions** - Predict review times, success rates
2. **Anomaly detection** - Flag unusual patterns
3. **A/B testing** - Compare decision strategies
4. **Multi-agent coordination** - Share insights between agents
5. **Visualization dashboard** - Graph trends and patterns

---

**@support-master** has implemented a comprehensive, non-blocking memory system for the meta-coordinator agent.

*Memory system ready for use: 2025-11-23*
