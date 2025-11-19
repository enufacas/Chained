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
4. **`_extract_agent_mentions_from_text(text)`** - NEW: Extracts @agent-name mentions from text
5. **`_check_pr_agent_attribution(pr_number, specialization)`** - NEW: Verifies PR was done by expected agent
6. **`_filter_prs_by_agent_attribution(prs, specialization, strict_mode)`** - NEW: Filters PRs by attribution
7. **`_is_strict_pr_attribution_enabled()`** - NEW: Checks if strict mode is enabled in config

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

1. ~~**PR-based attribution** - Also parse PR descriptions for agent attribution~~ ✅ **IMPLEMENTED**
2. **Label-based fallback** - Use agent-specific labels as backup method
3. **Comment updates** - Allow reassigning issues by updating the comment
4. **Multi-agent collaboration** - Support multiple agents working on same issue

## PR-Based Attribution (Implemented)

As of the latest update, the agent evaluation system now examines PR descriptions and comments to verify agent work attribution:

### How It Works

1. **Issue Assignment** - Issues are assigned to agents via `COPILOT_AGENT` comments (existing behavior)
2. **PR Discovery** - PRs linked to those issues are discovered via GitHub timeline API (existing behavior)
3. **PR Attribution Check** - NEW: The system now examines PR descriptions and comments for `@agent-name` mentions
4. **Strict Validation** - NEW: PRs are only counted if they clearly mention the assigned agent

### Agent Mention Format

PRs are attributed to an agent if they contain mentions in the format `@agent-name` where agent-name matches the agent's specialization:

- `@engineer-master` in PR title
- `@bug-hunter` in PR description
- `@secure-specialist` in PR comments
- `**@create-guru**` (bolded mentions also work)
- `(@accelerate-master)` (in commit-style format)

### Configuration

Strict PR attribution checking can be configured in the registry:

```json
{
  "config": {
    "strict_pr_attribution": true
  }
}
```

- `true` (default): Only count PRs with clear agent mentions
- `false`: Accept all PRs linked to agent's issues (backward compatible)

### Benefits

✅ **Accurate Work Attribution** - Ensures agents are only credited for work they actually did  
✅ **Prevents False Positives** - A PR linked to an agent's issue but done by someone else won't be counted  
✅ **Encourages Proper Documentation** - Agents must clearly identify themselves in PRs  
✅ **Configurable** - Can be disabled for backward compatibility

### Testing

The test suite has been extended to cover PR attribution:

```bash
python3 test_agent_attribution.py
```

New tests include:
- Agent mention extraction from various text formats
- Configuration loading and validation
- Method existence verification for new functionality

## Examples

### Creating an Issue for bug-hunter

```markdown
<!-- COPILOT_AGENT:bug-hunter -->

> **🤖 Agent Assignment**
> This issue has been assigned to the bug-hunter custom agent.

## Bug Description

There's a crash in the login module...
```

### Creating a PR that will be attributed to bug-hunter

```markdown
## 👤 Agent

Created by: **@bug-hunter**

### Work Completed

**@bug-hunter** has implemented the following changes:
- Fixed the crash in the login module
- Added error handling for null inputs
- Added tests for edge cases

### Testing

All tests pass. The bug is now resolved.

Fixes #123
```

This PR will be properly attributed to bug-hunter because:
1. It mentions `@bug-hunter` in the description
2. It references the issue (#123) that was assigned to bug-hunter
3. The system will validate both the issue assignment and the PR mention

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
