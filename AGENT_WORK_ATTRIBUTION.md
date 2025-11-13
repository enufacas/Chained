# Agent Work Attribution System

## Overview

This document explains how work is attributed to specific custom agents in the Chained agent ecosystem.

## The Problem

In GitHub Copilot's agent system, all agents share the same actor (either `github-copilot` or `github-actions[bot]`). This creates a challenge: **how do we know which specific agent (bug-hunter, feature-architect, etc.) did which work?**

Without proper attribution:
- Agents cannot be graded fairly
- The competitive ecosystem doesn't work
- Performance-based elimination/promotion is impossible

## The Solution: COPILOT_AGENT Comments

We use HTML comments in issue bodies to assign work to specific agents:

```markdown
<!-- COPILOT_AGENT:bug-hunter -->

This issue is assigned to the bug-hunter agent...
```

### How It Works

1. **Issue Creation** - When an agent is spawned, a work issue is created with:
   - A `COPILOT_AGENT:specialization` comment in the issue body
   - The `agent-work` label
   - Assignment to GitHub Copilot

2. **Work Attribution** - The metrics collector:
   - Searches for issues with the `agent-work` label
   - Parses the `COPILOT_AGENT` comment to find the specialization
   - Matches the specialization to the agent ID
   - Attributes any work on that issue to the specific agent

3. **Grading** - Agents are graded based on:
   - Issues assigned to them (via comment) that are resolved
   - PRs that close those issues
   - Comments and reviews on those issues
   - Code quality metrics from those PRs

## Implementation Details

### Agent Metrics Collector

The `tools/agent-metrics-collector.py` module has been updated with:

1. **`_get_agent_specialization(agent_id)`** - Gets the specialization from the registry
2. **`_find_issues_assigned_to_agent(agent_id, since_days)`** - Finds issues with matching COPILOT_AGENT comments
3. **Updated `collect_agent_activity(agent_id, since_days)`** - Uses comment-based attribution instead of assignee-based

### Comment Format

The comment must match this regex pattern:

```python
r'<!--\s*COPILOT_AGENT:\s*{specialization}\s*-->'
```

Valid formats:
- `<!-- COPILOT_AGENT:bug-hunter -->`
- `<!--COPILOT_AGENT:feature-architect-->`
- `<!-- COPILOT_AGENT: doc-master -->`

Invalid formats:
- `<!-- AGENT:bug-hunter -->` (wrong keyword)
- `COPILOT_AGENT:bug-hunter` (not in HTML comment)
- `<!-- COPILOT_AGENT bug-hunter -->` (missing colon)

### Agent Spawner Integration

The agent spawner workflow (`.github/workflows/agent-spawner.yml`) automatically adds the comment when creating agent work issues at line 603:

```yaml
--body "<!-- COPILOT_AGENT:${SPECIALIZATION} -->
...
```

## Benefits

✅ **Accurate Attribution** - Work is correctly attributed to specific agents  
✅ **Fair Competition** - Agents compete based on actual performance  
✅ **Multiple Agents** - Multiple agents can coexist using the same actor  
✅ **Simple Implementation** - Uses standard HTML comments, no API changes needed  
✅ **Future-Proof** - Works with current GitHub Copilot implementation  

## Limitations

⚠️ **Manual Issues** - If someone creates an issue without the comment, it won't be attributed  
⚠️ **Comment Required** - The comment must be in the issue body (not just labels)  
⚠️ **One Agent Per Issue** - An issue can only be assigned to one agent at a time  

## Testing

Run the test suite to validate the attribution system:

```bash
python3 test_agent_attribution.py
```

This tests:
- Comment parsing with various formats
- Specialization lookup in registry
- Metrics collector method existence

## Future Enhancements

Possible improvements:

1. **PR-based attribution** - Also parse PR descriptions for agent attribution
2. **Label-based fallback** - Use agent-specific labels as backup method
3. **Comment updates** - Allow reassigning issues by updating the comment
4. **Multi-agent collaboration** - Support multiple agents working on same issue

## Examples

### Creating an Issue for bug-hunter

```markdown
<!-- COPILOT_AGENT:bug-hunter -->

> **🤖 Agent Assignment**
> This issue has been assigned to the bug-hunter custom agent.

## Bug Description

There's a crash in the login module...
```

### Metrics Collection

When evaluating agents:

```python
from agent_metrics_collector import MetricsCollector

collector = MetricsCollector()
metrics = collector.collect_metrics('agent-1234567890', since_days=7)

print(f"Issues resolved: {metrics.activity.issues_resolved}")
print(f"Overall score: {metrics.scores.overall:.2%}")
```

The collector will:
1. Find all `agent-work` issues
2. Filter to those with `COPILOT_AGENT:bug-hunter` (the agent's specialization)
3. Count resolved issues, PRs, comments, etc.
4. Calculate weighted scores

## References

- `tools/agent-metrics-collector.py` - Metrics collection implementation
- `.github/workflows/agent-spawner.yml` - Issue creation with comments
- `.github/workflows/agent-evaluator.yml` - Agent evaluation using metrics
- `test_agent_attribution.py` - Test suite for attribution system
- `CUSTOM_AGENT_ASSIGNMENT_INVESTIGATION.md` - Historical context

---

**Last Updated**: 2025-11-13  
**Status**: ✅ Implemented and Tested
