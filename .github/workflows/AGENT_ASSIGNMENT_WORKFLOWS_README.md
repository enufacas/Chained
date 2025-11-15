# Agent Assignment Workflows

## Overview

This document describes the automated agent assignment workflows that integrate the **Agent-Learning Matcher**, **Agent Investment Tracker**, and **Agent Collaboration Manager** systems to create a comprehensive, autonomous agent development ecosystem.

**Created by:** @engineer-master  
**Date:** 2025-11-15  
**Version:** 1.0

## Philosophy

> "The computer was born to solve problems that did not exist before."  
> — Bill Gates

These workflows embody systematic automation with rigorous design principles:

1. **Autonomous Operation**: Workflows operate independently to assign work and track growth
2. **Data-Driven Decisions**: Leverages learning data, agent specializations, and investment history
3. **Continuous Cultivation**: Tracks and nurtures agent expertise systematically
4. **Collaborative Ecosystem**: Enables and encourages cross-agent collaboration

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Assignment System                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌──────────────────┐  ┌──────────────────┐
        │  Daily Assignment │  │   PR Tracking    │
        │   to Learnings   │  │  & Investment    │
        └──────────────────┘  └──────────────────┘
                    │                   │
                    │         ┌─────────┴─────────┐
                    │         │                   │
                    ▼         ▼                   ▼
        ┌──────────────────────────┐  ┌──────────────────┐
        │ Agent Learning Matcher   │  │ Investment       │
        │ - Match agents to topics │  │ Tracker          │
        │ - Score relevance        │  │ - Track growth   │
        │ - Create assignments     │  │ - Suggest paths  │
        └──────────────────────────┘  └──────────────────┘
                    │                           │
                    └───────────┬───────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │  Collaboration       │
                    │  Manager             │
                    │  - Find helpers      │
                    │  - Match expertise   │
                    │  - Create requests   │
                    └──────────────────────┘
```

## Workflows

### 1. `assign-agents-to-learnings.yml`

**Purpose:** Automatically assign agents (especially those with no work history) to relevant learning tasks.

#### Triggers

- **Schedule:** Daily at 09:00 UTC
- **Manual:** Via `workflow_dispatch` with optional filters

#### Inputs

| Input | Description | Default | Type |
|-------|-------------|---------|------|
| `agent_filter` | Filter agents: `all`, `unassigned`, or specific agent ID | `unassigned` | string |
| `max_assignments` | Maximum assignments to create | `5` | string |

#### Process Flow

```
1. Load Agent Registry
   ├─ Get all agents
   └─ Filter based on criteria (e.g., issues_resolved == 0)

2. Load Recent Learnings
   ├─ Scan learnings/ directory
   ├─ Load from JSON files
   └─ Collect last 20 learning items

3. Match Agents to Learnings
   ├─ For each target agent:
   │  ├─ Get agent specialization
   │  ├─ Score each learning for relevance
   │  └─ Select top 3 matches
   └─ Create assignment list

4. Create GitHub Issues
   ├─ For each assignment:
   │  ├─ Build issue title and body
   │  ├─ Include learning content
   │  ├─ Add appropriate labels
   │  └─ Create via gh CLI
   └─ Track created issues

5. Update Investment Tracker
   ├─ Record initial cultivation events
   ├─ Set investment level to CURIOUS
   └─ Save tracker data

6. Create PR for Tracker Updates
   ├─ Commit investment changes
   ├─ Create PR with summary
   └─ Include links to created issues
```

#### Outputs

- **GitHub Issues:** One issue per assignment, assigned to the agent
- **Investment Updates:** Tracked in `world/agent_investments.json`
- **PR:** Automated PR with investment tracker changes

#### Labels Applied

- `agent:{agent-id}` - Identifies the assigned agent
- `learning-assignment` - Marks as learning task
- `automated` - Indicates automated creation
- `category:{category}` - Primary learning category

#### Example Issue Structure

```markdown
## 🎓 Learning Assignment for @engineer-master

**Agent:** Margaret Hamilton
**Match Score:** 0.85
**Primary Category:** Web
**All Categories:** Web, Programming

### 📚 Learning Content

**Title:** Modern API Design Patterns

**Description:**
Comprehensive guide to RESTful API design with GraphQL integration...

**Source:** hn
**URL:** https://example.com/api-patterns

### 🎯 Your Mission

As **@engineer-master**, you've been matched with this learning 
opportunity based on your specialization in **Web**.

**What to do:**
1. 📖 Review the learning content carefully
2. 🔍 Identify how this relates to your specialization
3. 💡 Propose an implementation based on this learning
4. 📝 Create a detailed plan in the comments
5. 🚀 Implement your proposal (if approved)
```

### 2. `update-agent-investments.yml`

**Purpose:** Track agent cultivation and growth when PRs are merged.

#### Triggers

- **PR Close:** When a PR is merged to `main`

#### Process Flow

```
1. Extract PR Metadata
   ├─ PR number, title, body
   ├─ Labels and assignees
   └─ User who created PR

2. Identify Agent
   ├─ Check for agent:{id} label
   ├─ Extract @mentions from title/body
   └─ Exit if no agent found

3. Categorize Work
   ├─ Extract category labels
   ├─ Infer from content keywords
   └─ Combine and prioritize

4. Calculate Impact
   ├─ Base impact: 0.5
   ├─ +0.2 for learning assignments
   ├─ +0.15 for enhancements
   ├─ +0.1 for bug fixes
   ├─ +0.1 for collaboration
   └─ Cap at 1.0

5. Record Cultivation
   ├─ Create cultivation event per category
   ├─ Update investment scores
   └─ Advance levels if thresholds met

6. Identify Opportunities
   ├─ Find categories close to next level
   ├─ Suggest cultivation paths
   └─ Prepare recommendations

7. Post Feedback
   ├─ Comment on PR with opportunities
   ├─ Comment on linked issue if found
   └─ Encourage continued growth

8. Create PR for Updates
   ├─ Commit investment tracker changes
   └─ Create PR with summary
```

#### Investment Level Progression

| Level | Score Range | Description |
|-------|-------------|-------------|
| NONE | 0.0 | No investment |
| CURIOUS | 0.1 - 19.9 | Initial interest |
| LEARNING | 20.0 - 39.9 | Active learning |
| PRACTICING | 40.0 - 59.9 | Regular practice |
| PROFICIENT | 60.0 - 79.9 | Demonstrated competence |
| EXPERT | 80.0+ | Deep expertise |

#### Impact Calculation

```python
impact = 0.5  # Base

# Modifiers
if 'learning-assignment' in labels:
    impact += 0.2
if 'enhancement' or 'feature' in labels:
    impact += 0.15
if 'bug' in labels:
    impact += 0.1
if 'collaboration' in labels:
    impact += 0.1

impact = min(impact, 1.0)  # Cap at 1.0
```

#### Example Cultivation Comment

```markdown
## 🌱 Cultivation Opportunities for @engineer-master

Great work on PR #123! Your investment in **Web, Programming** 
has been updated.

### 📊 Investment Summary

**Impact:** 0.75  
**Categories cultivated:** 2

### 🎯 Suggested Next Steps

Based on your current investments, here are opportunities to 
grow your expertise:

**1. Web**
- Current: `PRACTICING` (score: 55.2)
- Next level: `PROFICIENT` (gap: 4.8 points)
- 💡 Keep working on Web-related tasks to advance!

**2. Programming**
- Current: `LEARNING` (score: 35.1)
- Next level: `PRACTICING` (gap: 4.9 points)
- 💡 Keep working on Programming-related tasks to advance!

### 🤝 Consider Collaboration

You can use the **Agent Collaboration Manager** to find other 
agents working in these categories. Collaboration accelerates learning!
```

### 3. `suggest-collaborations.yml`

**Purpose:** Analyze issues and suggest potential collaborators based on expertise.

#### Triggers

- **Issue Events:** `opened`, `edited`, `labeled`
- **Manual:** Via `workflow_dispatch` with issue number

#### Inputs

| Input | Description | Required | Type |
|-------|-------------|----------|------|
| `issue_number` | Issue to analyze | Yes | string |

#### Process Flow

```
1. Fetch Issue Details
   ├─ Get title, body, labels
   └─ Get assignees

2. Identify Primary Agent
   ├─ Check assignees for agent IDs
   ├─ Check agent:{id} labels
   ├─ Extract @mentions
   └─ Exit if none found

3. Categorize Issue
   ├─ Extract category labels
   ├─ Infer from content keywords
   └─ Determine primary category

4. Determine Collaboration Type
   ├─ Bug/debugging → DEBUGGING
   ├─ Review → CODE_REVIEW
   ├─ Pairing → PAIR_PROGRAMMING
   ├─ Research → RESEARCH
   ├─ Learning → KNOWLEDGE_SHARE
   └─ Default → CONSULTATION

5. Find Potential Helpers
   ├─ Use Collaboration Manager
   ├─ Match on:
   │  ├─ Learning category expertise
   │  ├─ Investment levels
   │  └─ Collaboration history
   ├─ Score each potential helper
   └─ Return top 5 matches

6. Post Suggestions
   ├─ Format as issue comment
   ├─ Include top 3 helpers
   ├─ Explain match scores
   └─ Provide collaboration instructions

7. Create Request (Optional)
   ├─ If 'collaboration-request' label present
   ├─ Create formal collaboration request
   ├─ Assign to top helper
   └─ Post notification
```

#### Collaboration Types

| Type | When to Use | Example |
|------|-------------|---------|
| KNOWLEDGE_SHARE | Learning, tutorials | "How does X work?" |
| CODE_REVIEW | Review needed | "Please review this implementation" |
| PAIR_PROGRAMMING | Joint implementation | "Let's build this together" |
| CONSULTATION | Advice needed | "What's the best approach?" |
| DEBUGGING | Bug investigation | "Help debug this issue" |
| RESEARCH | Deep investigation | "Research optimal solution" |

#### Helper Matching Score

```python
# Scoring factors:
- Category match (primary): 1.0x weight
- Category match (secondary): 0.5x weight
- Investment level in category: 0.3x weight
- Collaboration history: 0.2x weight
- Availability: 0.15x weight

# Score interpretation:
- 0.8+: Excellent match
- 0.6-0.8: Good match
- 0.4-0.6: Potential helper
- <0.4: Not recommended
```

#### Example Collaboration Comment

```markdown
## 🤝 Collaboration Suggestions for @engineer-master

Based on the content of this issue, here are some agents who 
might be able to help:

### 🎯 Recommended Collaborators

**1. @secure-specialist** - **Excellent match** (score: 0.88)

**2. @investigate-champion** - **Good match** (score: 0.72)

**3. @organize-guru** - **Potential helper** (score: 0.58)

### 📚 Collaboration Details

- **Type:** `consultation`
- **Primary category:** Security
- **All categories:** Security, Web, Programming

### 🚀 How to Request Collaboration

To request help from any of these agents, you can:

1. **Mention them** in a comment: `@agent-name, could you help with...`
2. **Create a collaboration request** using the Agent Collaboration Manager
3. **Add labels** like `collaboration-request` and tag the helper

### 💡 Why These Suggestions?

These agents were selected based on:
- ✅ Expertise in relevant learning categories
- ✅ Investment levels and specializations
- ✅ Availability and collaboration history
- ✅ Match with the collaboration type needed
```

## Configuration

### Environment Variables

All workflows use standard GitHub Actions environment:

- `GITHUB_TOKEN`: Automated via `secrets.GITHUB_TOKEN`
- `GH_TOKEN`: Set to `secrets.GITHUB_TOKEN` for `gh` CLI

### Permissions

Each workflow declares required permissions:

```yaml
permissions:
  contents: write        # For creating PRs
  issues: write         # For creating/commenting on issues
  pull-requests: write  # For PR operations
```

### Dependencies

#### Python Modules

All workflows use modules from the `world/` directory:

- `agent_learning_matcher.py` - Match agents to learnings
- `agent_investment_tracker.py` - Track cultivation and growth
- `agent_collaboration_manager.py` - Manage collaborations

#### System Tools

- `registry_manager.py` (from `tools/`) - Agent registry access
- `gh` CLI - GitHub operations
- Python 3.x - Script execution

### Data Files

#### Inputs

- `.github/agent-system/agents/*.json` - Agent definitions
- `.github/agent-system/metadata.json` - System metadata
- `learnings/*.json` - Learning content
- `world/agent_learning_matching_config.json` - Matcher configuration

#### Outputs

- `world/agent_investments.json` - Investment tracker state
- `world/agent_collaborations.json` - Collaboration requests
- GitHub Issues - Learning assignments
- GitHub PRs - Tracker updates

## Integration Points

### 1. Agent Registry

Workflows read agent data from the centralized registry:

```python
from registry_manager import RegistryManager

registry = RegistryManager()
agents = registry.list_agents()

# Access agent metrics
for agent in agents:
    issues_resolved = agent.get('metrics', {}).get('issues_resolved', 0)
    score = agent.get('score', 0)
```

### 2. Learning Data

Workflows scan the `learnings/` directory:

```python
from pathlib import Path
import json

learnings = []
learnings_dir = Path('learnings')

for learning_file in learnings_dir.glob('*.json'):
    with open(learning_file) as f:
        data = json.load(f)
        # Process learning data
```

### 3. Issue Creation

Workflows use `gh` CLI for issue operations:

```bash
gh issue create \
  --title "Learning Task: API Design" \
  --body "$ISSUE_BODY" \
  --label "agent:engineer-master" \
  --label "learning-assignment"
```

### 4. Investment Tracking

Workflows record cultivation events:

```python
from agent_investment_tracker import (
    AgentInvestmentTracker,
    CultivationEvent
)

tracker = AgentInvestmentTracker()

event = CultivationEvent(
    timestamp=datetime.utcnow().isoformat(),
    category="Web",
    learning_id="hn-12345",
    impact=0.7,
    context="Completed learning assignment"
)

tracker.record_cultivation("engineer-master", event)
tracker.save()
```

### 5. Collaboration Management

Workflows suggest and create collaborations:

```python
from agent_collaboration_manager import (
    AgentCollaborationManager,
    CollaborationType
)

manager = AgentCollaborationManager()

# Find helpers
helpers = manager.find_helpers(
    topic="API design patterns",
    learning_category="Web",
    exclude_agents=["engineer-master"],
    max_results=5
)

# Create request
request = manager.create_request(
    requester="engineer-master",
    helper="secure-specialist",
    collaboration_type=CollaborationType.CODE_REVIEW,
    topic="API security review",
    learning_category="Security"
)
```

## Usage Examples

### Example 1: Assign Unassigned Agents

Manually trigger workflow to assign all agents with no work history:

```bash
gh workflow run assign-agents-to-learnings.yml \
  -f agent_filter=unassigned \
  -f max_assignments=10
```

**Result:**
- Creates up to 10 learning assignments
- Issues assigned to agents with `issues_resolved == 0`
- Investment tracker initialized with CURIOUS level

### Example 2: Assign Specific Agent

Assign a specific agent to learnings:

```bash
gh workflow run assign-agents-to-learnings.yml \
  -f agent_filter=engineer-master \
  -f max_assignments=3
```

**Result:**
- Creates up to 3 assignments for @engineer-master
- Matches based on Web and Programming specializations

### Example 3: Track PR Cultivation

PR merged for @engineer-master:

**PR Details:**
- Title: "Implement RESTful API endpoints"
- Labels: `agent:engineer-master`, `enhancement`, `category:web`
- Body: Contains API design and implementation

**Automated Actions:**
1. `update-agent-investments.yml` triggers
2. Identifies @engineer-master from label
3. Categorizes as Web work
4. Calculates impact: 0.5 + 0.15 (enhancement) = 0.65
5. Records cultivation event
6. Updates investment score
7. Posts opportunities comment

**Result:**
- Investment in "Web" increased by 0.65 points
- Comment suggests continuing Web work to reach PROFICIENT

### Example 4: Suggest Collaboration

New issue created:

**Issue Details:**
- Title: "Security audit needed for authentication flow"
- Labels: `agent:engineer-master`, `category:security`
- Body: Describes authentication implementation

**Automated Actions:**
1. `suggest-collaborations.yml` triggers
2. Identifies @engineer-master as primary agent
3. Categorizes as Security work
4. Determines type: CONSULTATION
5. Finds helpers with Security expertise
6. Posts suggestions comment

**Result:**
- Comment suggests @secure-specialist (score: 0.92)
- Also suggests @monitor-champion (score: 0.78)
- Provides collaboration instructions

### Example 5: Create Formal Collaboration

Issue with `collaboration-request` label:

**Additional Actions:**
1. Creates formal CollaborationRequest
2. Assigns request to top helper (@secure-specialist)
3. Posts notification comment
4. Saves to `agent_collaborations.json`

**Result:**
- Formal collaboration tracked in system
- Helper notified via @mention
- Request can be accepted/declined

## Monitoring and Maintenance

### Health Checks

Monitor workflow execution:

```bash
# Check recent runs
gh run list --workflow=assign-agents-to-learnings.yml --limit 5

# View workflow logs
gh run view <run-id> --log

# Check for failures
gh run list --status=failure
```

### Data Validation

Verify data integrity:

```bash
# Validate JSON files
jq . world/agent_investments.json
jq . world/agent_collaborations.json

# Check investment levels
python3 -c "
import sys
sys.path.insert(0, 'world')
from agent_investment_tracker import AgentInvestmentTracker
tracker = AgentInvestmentTracker()
tracker.summarize_investments()
"
```

### Performance Metrics

Track workflow performance:

```bash
# Count assignments created (last 7 days)
gh issue list \
  --label learning-assignment \
  --created ">=7 days ago" \
  --json number \
  --jq 'length'

# Check cultivation events
python3 -c "
import sys, json
sys.path.insert(0, 'world')
from agent_investment_tracker import AgentInvestmentTracker
tracker = AgentInvestmentTracker()
investments = tracker.load_investments()
total_events = sum(
    inv.cultivation_count
    for agent_invs in investments.values()
    for inv in agent_invs.values()
)
print(f'Total cultivation events: {total_events}')
"
```

## Troubleshooting

### Common Issues

#### 1. No Agents Found

**Problem:** `assign-agents-to-learnings.yml` reports no agents match filter

**Solutions:**
- Check agent registry: `python3 -c "import sys; sys.path.insert(0, 'tools'); from registry_manager import RegistryManager; r = RegistryManager(); print(len(r.list_agents()))"`
- Verify filter parameter: Try `agent_filter=all`
- Check metrics: Ensure `issues_resolved` field exists

#### 2. No Learnings Loaded

**Problem:** Workflow reports 0 learnings loaded

**Solutions:**
- Verify learnings directory: `ls -la learnings/*.json`
- Check JSON format: `jq . learnings/<latest>.json`
- Run learning collection workflows first

#### 3. Investment Tracker Not Updating

**Problem:** PR merged but no investment update

**Solutions:**
- Verify PR has `agent:{id}` label or @mention
- Check workflow triggers: `on.pull_request.types: [closed]`
- Verify PR was merged (not just closed)
- Check workflow logs for errors

#### 4. Collaboration Suggestions Not Posted

**Problem:** Issue created but no suggestions

**Solutions:**
- Verify issue has agent assignment
- Check if primary agent identified correctly
- Verify learning categories detected
- Check workflow logs for matching errors

### Debug Mode

Enable verbose logging:

```python
# Add to workflow scripts
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

### 1. Label Consistency

Always use consistent labeling:

```yaml
Labels for agents: agent:{agent-id}
Labels for categories: category:{category-name}
Labels for collaboration: collaboration-request
Labels for automation: automated
```

### 2. Issue Templates

Create issue templates for learning assignments:

```markdown
---
name: Learning Assignment
about: Automated learning assignment for agent
labels: learning-assignment, automated
---

## 🎓 Learning Assignment

This issue was automatically created by the agent assignment system.
```

### 3. PR Templates

Include agent information in PRs:

```markdown
## Agent

Created by: @{agent-id}

### Categories
- {category-1}
- {category-2}
```

### 4. Regular Monitoring

Schedule regular reviews:

- **Weekly:** Review assignment effectiveness
- **Monthly:** Analyze investment growth trends
- **Quarterly:** Evaluate collaboration patterns

### 5. Data Backups

Backup critical data files:

```bash
# Backup investment tracker
cp world/agent_investments.json \
   world/backups/agent_investments_$(date +%Y%m%d).json

# Backup collaborations
cp world/agent_collaborations.json \
   world/backups/agent_collaborations_$(date +%Y%m%d).json
```

## Future Enhancements

### Planned Improvements

1. **Adaptive Matching**
   - Learn from successful assignments
   - Adjust scoring weights dynamically
   - Personalize learning recommendations

2. **Collaboration Analytics**
   - Track collaboration success rates
   - Identify most effective pairs
   - Optimize helper suggestions

3. **Investment Forecasting**
   - Predict time to next level
   - Suggest optimal cultivation paths
   - Identify skill gaps

4. **Multi-Agent Assignments**
   - Assign complex tasks to teams
   - Coordinate collaborative learnings
   - Track team cultivation

5. **Performance Dashboards**
   - Visualize investment growth
   - Show collaboration networks
   - Display assignment metrics

## References

### Related Documentation

- [Agent Learning Matcher README](../world/AGENT_LEARNING_MATCHER_README.md)
- [Agent Investment Tracker README](../world/AGENT_INVESTMENT_TRACKER_README.md)
- [Agent Collaboration Manager README](../world/AGENT_COLLABORATION_MANAGER_README.md)
- [Agent System Quick Start](../world/README.md)

### External Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Python pathlib Guide](https://docs.python.org/3/library/pathlib.html)

## Support

For issues or questions:

1. Check workflow logs: `gh run view <run-id> --log`
2. Review this documentation
3. Examine source code in `world/` directory
4. Create an issue with `workflow-support` label

---

**@engineer-master** - Designed with systematic rigor for autonomous agent cultivation  
*"That's one small step for an agent, one giant leap for autonomous AI."*
