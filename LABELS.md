# 🏷️ Label Reference Guide

> **Complete documentation of all labels used in the Chained autonomous AI repository**

This document provides a comprehensive reference for all labels used in the Chained repository, explaining their purpose, usage, and relationships within the autonomous development cycle.

---

## 📑 Table of Contents

- [Quick Reference Table](#-quick-reference-table)
- [🚨 Critical: Understanding "copilot" vs "copilot-assigned"](#-critical-understanding-copilot-vs-copilot-assigned)
- [Core Autonomous System Labels](#-core-autonomous-system-labels)
- [Agent System Labels](#-agent-system-labels)
- [Workflow & Monitoring Labels](#️-workflow--monitoring-labels)
- [Content & Learning Labels](#-content--learning-labels)
- [Status Labels](#-status-labels)
- [Documentation Labels](#-documentation-labels)
- [Usage Examples](#-usage-examples)
- [Related Documentation](#-related-documentation)

---

## 🎯 Quick Reference Table

| Label | Color | Category | Applied By | Primary Purpose |
|-------|-------|----------|------------|-----------------|
| `copilot-assigned` | ![#0366d6](https://via.placeholder.com/15/0366d6/000000?text=+) `#0366d6` | Core | copilot-graphql-assign.yml | Issue assigned TO Copilot for work |
| `copilot` | ![#0366d6](https://via.placeholder.com/15/0366d6/000000?text=+) `#0366d6` | Core | auto-review-merge.yml | Content/PR created BY Copilot (enables auto-merge) |
| `ai-generated` | ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` | Core | idea-generator.yml | Created by AI Idea Generator |
| `automated` | ![#fbca04](https://via.placeholder.com/15/fbca04/000000?text=+) `#fbca04` | Core | Multiple workflows | Automated process or content |
| `agent-system` | ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` | Agent | agent-spawner.yml | Agent ecosystem activity |
| `agent-work` | ![#0e8a16](https://via.placeholder.com/15/0e8a16/000000?text=+) `#0e8a16` | Agent | agent-spawner.yml | Work assigned to agents |
| `spawn-pending` | ![#d4c5f9](https://via.placeholder.com/15/d4c5f9/000000?text=+) `#d4c5f9` | Agent | agent-spawner.yml | Waiting for agent spawn PR to merge |
| `in-progress` | ![#fbca04](https://via.placeholder.com/15/fbca04/000000?text=+) `#fbca04` | Status | Multiple workflows | Work in progress |
| `completed` | ![#0e8a16](https://via.placeholder.com/15/0e8a16/000000?text=+) `#0e8a16` | Status | auto-review-merge.yml | Completed task |
| `learning` | ![#d93f0b](https://via.placeholder.com/15/d93f0b/000000?text=+) `#d93f0b` | Content | learn-from-*.yml | Learning or insight captured |
| `progress-report` | ![#c5def5](https://via.placeholder.com/15/c5def5/000000?text=+) `#c5def5` | Status | progress-tracker.yml | Progress tracking report |
| `enhancement` | ![#a2eeef](https://via.placeholder.com/15/a2eeef/000000?text=+) `#a2eeef` | Content | Multiple workflows | New feature or request |
| `workflow-monitor` | ![#d73a4a](https://via.placeholder.com/15/d73a4a/000000?text=+) `#d73a4a` | Monitoring | system-monitor.yml | Workflow monitoring alert |
| `workflow-failure` | ![#d73a4a](https://via.placeholder.com/15/d73a4a/000000?text=+) `#d73a4a` | Monitoring | workflow-failure-handler.yml | Workflow failure alert |
| `announcement` | ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` | Agent | agent-spawner.yml | Agent announcements |
| `evaluation` | ![#e4e669](https://via.placeholder.com/15/e4e669/000000?text=+) `#e4e669` | Agent | agent-evaluator.yml | Agent evaluations |
| `documentation` | ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` | Content | Multiple workflows | Documentation changes |
| `code-quality` | ![#1d76db](https://via.placeholder.com/15/1d76db/000000?text=+) `#1d76db` | Content | code-analyzer.yml | Code quality improvements |
| `code-golf` | ![#fbca04](https://via.placeholder.com/15/fbca04/000000?text=+) `#fbca04` | Content | code-golf-optimizer.yml | Code golf optimization |
| `pattern-analysis` | ![#5319e7](https://via.placeholder.com/15/5319e7/000000?text=+) `#5319e7` | Content | pattern-matcher.yml | Pattern analysis results |
| `archaeology` | ![#8b4513](https://via.placeholder.com/15/8b4513/000000?text=+) `#8b4513` | Content | code-archaeologist.yml | Code archaeology findings |
| `ai-goal` | ![#ffd700](https://via.placeholder.com/15/ffd700/000000?text=+) `#ffd700` | Content | daily-goal-generator.yml | Daily AI goals |
| `ai-autonomy` | ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` | Core | Multiple workflows | AI autonomy features |
| `pages-health` | ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` | Monitoring | github-pages-review.yml | GitHub Pages health checks |
| `pages-review` | ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` | Monitoring | github-pages-review.yml | GitHub Pages review issues |
| `timeline-update` | ![#c5def5](https://via.placeholder.com/15/c5def5/000000?text=+) `#c5def5` | Content | timeline-updater.yml | Timeline update issues |
| `agent-created` | ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` | Agent | Multiple agents | Created by an agent |
| `orchestrator` | ![#5319e7](https://via.placeholder.com/15/5319e7/000000?text=+) `#5319e7` | System | dynamic-orchestrator.yml | Dynamic orchestration |
| `workflow-optimization` | ![#1d76db](https://via.placeholder.com/15/1d76db/000000?text=+) `#1d76db` | Content | Multiple workflows | Workflow optimization |

---

## 🚨 Critical: Understanding "copilot" vs "copilot-assigned"

### These Two Labels Are NOT The Same!

This is the most common source of confusion in the Chained repository. These labels serve completely different purposes:

#### `copilot-assigned` - Assignment TO Copilot
- **Color:** ![#0366d6](https://via.placeholder.com/15/0366d6/000000?text=+) `#0366d6` (blue)
- **Description:** "Assigned to Copilot"
- **Applied By:** `copilot-graphql-assign.yml` workflow
- **Purpose:** Indicates that an issue has been **assigned TO GitHub Copilot** for implementation
- **Usage:** Applied when Copilot is assigned to work on an issue
- **Lifecycle:** Added during assignment, remains until issue is closed
- **Think of it as:** "Copilot, please work on this"

```yaml
# Applied by: .github/workflows/copilot-graphql-assign.yml
# When: Issue is assigned to Copilot via GraphQL API
gh issue edit $ISSUE_NUMBER --add-label "copilot-assigned"
```

#### `copilot` - Authorship BY Copilot
- **Color:** ![#0366d6](https://via.placeholder.com/15/0366d6/000000?text=+) `#0366d6` (blue)
- **Description:** "Created by Copilot"
- **Applied By:** `auto-review-merge.yml` workflow
- **Purpose:** Indicates that content (PR, code) was **created BY GitHub Copilot**
- **Usage:** Applied to PRs created by Copilot to enable auto-merge
- **Lifecycle:** Added when PR is detected as Copilot-authored, required for auto-merge
- **Think of it as:** "Copilot made this"

```yaml
# Applied by: .github/workflows/auto-review-merge.yml
# When: PR is detected as created by Copilot (matches various copilot author formats)
gh pr edit $PR_NUMBER --add-label "copilot"
```

### Why Both Labels Matter

**Auto-Merge Criteria:**
For a PR to be automatically merged, it must:
1. Have the `copilot` label (indicates it was created BY Copilot)
2. Be from a trusted source (repository owner OR trusted bot)
3. Be in "ready for review" status (not draft)
4. Be mergeable (no conflicts)

```bash
# From auto-review-merge.yml workflow
# Only auto-merge if:
# 1. PR is from repository owner AND has copilot label, OR
# 2. PR is from trusted bot AND has copilot label
if [ "${is_repo_owner}" -eq 1 ] && [ "${has_copilot_label}" -gt 0 ]; then
  should_auto_merge=1
elif [ "${is_trusted_bot}" -eq 1 ] && [ "${has_copilot_label}" -gt 0 ]; then
  should_auto_merge=1
fi
```

### Common Scenarios

| Scenario | `copilot-assigned` | `copilot` |
|----------|-------------------|-----------|
| New issue created, needs work | ✅ Added | ❌ Not applicable (issues don't have this) |
| Copilot creates PR from assigned issue | ✅ Remains on issue | ✅ Added to PR |
| PR from Copilot ready for merge | N/A | ✅ Required for auto-merge |
| Issue closed after PR merged | ✅ Removed (issue closed) | N/A |
| Repository owner creates PR manually | ❌ No | ✅ Required for auto-merge if owned by repo owner |

### Visual Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Issue Created                                                │
│    Labels: [ai-generated, automated]                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Copilot Assignment                                           │
│    Labels: [ai-generated, automated, copilot-assigned] ◀─ Added │
│    Assignee: GitHub Copilot                                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Copilot Creates PR                                           │
│    PR Labels: [copilot, automated] ◀─ "copilot" enables merge  │
│    Issue still has: [ai-generated, automated, copilot-assigned] │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PR Auto-Merged (because has "copilot" label)                │
│    Issue closed with: [completed]                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Core Autonomous System Labels

These labels are fundamental to the autonomous development cycle.

### `ai-generated`
- **Color:** ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` (purple)
- **Description:** "Created by AI Idea Generator"
- **Applied By:** `idea-generator.yml`, `ai-idea-spawner.yml`
- **Purpose:** Marks content created by the AI Idea Generator system
- **Lifecycle:** Applied at creation, permanent marker
- **Usage Example:**
  ```bash
  gh issue create \
    --title "Implement feature X" \
    --body "..." \
    --label "ai-generated,enhancement"
  ```

### `automated`
- **Color:** ![#fbca04](https://via.placeholder.com/15/fbca04/000000?text=+) `#fbca04` (yellow)
- **Description:** "Automated process"
- **Applied By:** Multiple workflows (system-kickoff.yml, agent-spawner.yml, etc.)
- **Purpose:** Indicates content or process was fully automated without human intervention
- **Lifecycle:** Applied at creation, permanent marker
- **Common Combinations:** Often paired with other labels like `ai-generated`, `copilot`, or `agent-system`

### `ai-autonomy`
- **Color:** ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` (purple)
- **Description:** "AI autonomy features"
- **Applied By:** Various workflows for autonomy-related content
- **Purpose:** Marks issues/PRs related to improving AI autonomy capabilities
- **Usage:** Applied to enhancements that expand autonomous capabilities

---

## 🤖 Agent System Labels

Labels specific to the agent ecosystem and spawning system.

### `agent-system`
- **Color:** ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` (purple)
- **Description:** "Agent ecosystem activity"
- **Applied By:** `agent-spawner.yml`
- **Purpose:** Marks all agent-related issues, PRs, and activities
- **Lifecycle:** Applied when agent spawn PR is created
- **Special Behavior:** Issues with this label are excluded from automatic Copilot assignment in `copilot-graphql-assign.yml`
- **Usage Example:**
  ```bash
  # Agent spawner creates PR with this label
  gh pr create \
    --label "agent-system,automated" \
    --title "🤖 Agent Spawn: doc-master-agent-123"
  ```

### `agent-work`
- **Color:** ![#0e8a16](https://via.placeholder.com/15/0e8a16/000000?text=+) `#0e8a16` (green)
- **Description:** "Work assigned to agents"
- **Applied By:** `agent-spawner.yml`
- **Purpose:** Marks work issues created for agents to implement
- **Lifecycle:** Applied at issue creation, remains until completion
- **Relationship:** Paired with `spawn-pending` until agent spawn is complete

### `spawn-pending`
- **Color:** ![#d4c5f9](https://via.placeholder.com/15/d4c5f9/000000?text=+) `#d4c5f9` (light purple)
- **Description:** "Waiting for agent spawn PR to merge"
- **Applied By:** `agent-spawner.yml`
- **Purpose:** Blocks Copilot assignment until agent spawn PR is merged
- **Lifecycle:** 
  - Added when work issue is created with spawn PR
  - Removed by `auto-review-merge.yml` when spawn PR merges
  - Removal triggers Copilot assignment
- **Critical:** Must be removed before Copilot can be assigned to the work issue
- **Usage Example:**
  ```bash
  # When agent spawn PR merges:
  gh issue edit $WORK_ISSUE --remove-label "spawn-pending"
  gh workflow run copilot-graphql-assign.yml -f issue_number=$WORK_ISSUE
  ```

### `agent-created`
- **Color:** ![#7057ff](https://via.placeholder.com/15/7057ff/000000?text=+) `#7057ff` (purple)
- **Description:** "Created by an agent"
- **Applied By:** Various custom agents
- **Purpose:** Indicates content was created by a specialized agent (doc-master, bug-hunter, etc.)
- **Usage:** Applied to issues/PRs created by agent personas

### `announcement`
- **Color:** ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` (blue)
- **Description:** "Agent announcements"
- **Applied By:** `agent-spawner.yml`
- **Purpose:** Marks agent spawn announcements and agent-related announcements
- **Usage:** Applied to issues announcing new agent spawns or agent milestones

### `evaluation`
- **Color:** ![#e4e669](https://via.placeholder.com/15/e4e669/000000?text=+) `#e4e669` (yellow)
- **Description:** "Agent evaluations"
- **Applied By:** `agent-evaluator.yml`
- **Purpose:** Marks agent performance evaluation reports
- **Usage:** Applied to issues containing agent performance metrics and scores

### `agent-health`
- **Color:** ![#d73a4a](https://via.placeholder.com/15/d73a4a/000000?text=+) `#d73a4a` (red)
- **Description:** "Agent health monitoring"
- **Applied By:** Agent health monitoring workflows
- **Purpose:** Marks issues related to agent health checks and status
- **Usage:** Applied when agent health issues are detected

---

## ⚙️ Workflow & Monitoring Labels

Labels related to workflow execution, monitoring, and orchestration.

### `workflow-monitor`
- **Color:** ![#d73a4a](https://via.placeholder.com/15/d73a4a/000000?text=+) `#d73a4a` (red)
- **Description:** "Workflow monitoring alert"
- **Applied By:** `system-monitor.yml`
- **Purpose:** Alerts about workflow execution issues or anomalies
- **Lifecycle:** Created when monitoring detects issues, closed when resolved
- **Severity:** Indicates attention needed for workflow execution

### `workflow-failure`
- **Color:** ![#d73a4a](https://via.placeholder.com/15/d73a4a/000000?text=+) `#d73a4a` (red)
- **Description:** "Workflow failure alert"
- **Applied By:** `workflow-failure-handler.yml`
- **Purpose:** Specific notification of workflow run failures
- **Lifecycle:** Created on failure, updated if failure repeats, closed when resolved
- **Action Required:** Indicates a workflow needs debugging or fixing

### `orchestrator`
- **Color:** ![#5319e7](https://via.placeholder.com/15/5319e7/000000?text=+) `#5319e7` (indigo)
- **Description:** "Dynamic orchestration"
- **Applied By:** `dynamic-orchestrator.yml`
- **Purpose:** Marks issues/PRs related to dynamic workflow orchestration and scheduling
- **Usage:** Applied to orchestration adjustments based on usage patterns

### `workflow-optimization`
- **Color:** ![#1d76db](https://via.placeholder.com/15/1d76db/000000?text=+) `#1d76db` (blue)
- **Description:** "Workflow optimization"
- **Applied By:** Various optimization workflows
- **Purpose:** Marks improvements to workflow efficiency and performance
- **Usage:** Applied to PRs that optimize workflow execution

---

## 📚 Content & Learning Labels

Labels for content creation, learning, and knowledge management.

### `learning`
- **Color:** ![#d93f0b](https://via.placeholder.com/15/d93f0b/000000?text=+) `#d93f0b` (orange)
- **Description:** "Learning or insight"
- **Applied By:** `learn-from-tldr.yml`, `learn-from-hackernews.yml`
- **Purpose:** Marks captured learnings and insights from external sources
- **Usage:** Applied to issues containing learnings that inform idea generation
- **Sources:** TLDR Tech (twice daily), Hacker News (3x daily)

### `enhancement`
- **Color:** ![#a2eeef](https://via.placeholder.com/15/a2eeef/000000?text=+) `#a2eeef` (light blue)
- **Description:** "New feature or request"
- **Applied By:** Multiple workflows, idea generators
- **Purpose:** Standard GitHub label for new features or improvements
- **Usage:** Applied to feature requests and enhancement proposals

### `documentation`
- **Color:** ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` (blue)
- **Description:** "Documentation changes"
- **Applied By:** Various workflows for doc-related changes
- **Purpose:** Marks documentation updates, additions, or improvements
- **Usage:** Applied to PRs that primarily change documentation files

### `code-quality`
- **Color:** ![#1d76db](https://via.placeholder.com/15/1d76db/000000?text=+) `#1d76db` (blue)
- **Description:** "Code quality improvements"
- **Applied By:** `code-analyzer.yml`
- **Purpose:** Marks improvements to code quality, readability, or maintainability
- **Usage:** Applied to PRs focused on code quality enhancements

### `code-golf`
- **Color:** ![#fbca04](https://via.placeholder.com/15/fbca04/000000?text=+) `#fbca04` (yellow)
- **Description:** "Code golf optimization"
- **Applied By:** `code-golf-optimizer.yml`
- **Purpose:** Marks code optimization focused on reducing lines/complexity
- **Usage:** Applied to issues and PRs from the code golf optimizer

### `pattern-analysis`
- **Color:** ![#5319e7](https://via.placeholder.com/15/5319e7/000000?text=+) `#5319e7` (indigo)
- **Description:** "Pattern analysis results"
- **Applied By:** `pattern-matcher.yml`
- **Purpose:** Marks results from code pattern analysis and recognition
- **Usage:** Applied to issues containing pattern analysis insights

### `archaeology`
- **Color:** ![#8b4513](https://via.placeholder.com/15/8b4513/000000?text=+) `#8b4513` (brown)
- **Description:** "Code archaeology findings"
- **Applied By:** `code-archaeologist.yml`
- **Purpose:** Marks discoveries from historical code analysis
- **Usage:** Applied to insights about code evolution and history

### `ai-goal`
- **Color:** ![#ffd700](https://via.placeholder.com/15/ffd700/000000?text=+) `#ffd700` (gold)
- **Description:** "Daily AI goals"
- **Applied By:** `daily-goal-generator.yml`
- **Purpose:** Marks daily goals set by the AI system
- **Usage:** Applied to goal tracking issues and related work

### `timeline-update`
- **Color:** ![#c5def5](https://via.placeholder.com/15/c5def5/000000?text=+) `#c5def5` (light blue)
- **Description:** "Timeline update issues"
- **Applied By:** `timeline-updater.yml`
- **Purpose:** Marks timeline update PRs and issues
- **Usage:** Applied to automated timeline documentation updates

---

## 📊 Status Labels

Labels indicating the current state of work.

### `in-progress`
- **Color:** ![#fbca04](https://via.placeholder.com/15/fbca04/000000?text=+) `#fbca04` (yellow)
- **Description:** "Work in progress"
- **Applied By:** Various workflows when work begins
- **Purpose:** Indicates active work is being performed
- **Lifecycle:** Added when work starts, removed when completed or stalled

### `completed`
- **Color:** ![#0e8a16](https://via.placeholder.com/15/0e8a16/000000?text=+) `#0e8a16` (green)
- **Description:** "Completed task"
- **Applied By:** `auto-review-merge.yml`, `system-kickoff.yml`
- **Purpose:** Marks successfully completed tasks
- **Lifecycle:** Applied when PR merges or task completes, permanent marker
- **Usage Example:**
  ```bash
  # When PR merges and closes issue:
  gh issue close $ISSUE_NUMBER --comment "✅ Completed"
  gh issue edit $ISSUE_NUMBER --add-label "completed"
  ```

### `progress-report`
- **Color:** ![#c5def5](https://via.placeholder.com/15/c5def5/000000?text=+) `#c5def5` (light blue)
- **Description:** "Progress tracking"
- **Applied By:** `progress-tracker.yml`
- **Purpose:** Marks progress tracking reports and updates
- **Usage:** Applied to periodic progress summary issues

---

## 📄 Documentation Labels

Labels specific to GitHub Pages and documentation health.

### `pages-health`
- **Color:** ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` (blue)
- **Description:** "GitHub Pages health checks"
- **Applied By:** `github-pages-review.yml`
- **Purpose:** Marks health check results for GitHub Pages
- **Schedule:** Weekly on Mondays at 8 AM UTC
- **Usage:** Applied to issues reporting Pages health status

### `pages-review`
- **Color:** ![#0075ca](https://via.placeholder.com/15/0075ca/000000?text=+) `#0075ca` (blue)
- **Description:** "GitHub Pages review issues"
- **Applied By:** `github-pages-review.yml`
- **Purpose:** Marks issues found during GitHub Pages review
- **Usage:** Applied to issues requiring fixes for Pages content

---

## 💡 Usage Examples

### Example 1: Agent Spawn Flow

```bash
# 1. Agent spawner creates spawn PR
gh pr create \
  --title "🤖 Agent Spawn: doc-master-agent-1234" \
  --body "..." \
  --label "agent-system,automated"

# 2. Agent spawner creates work issue
gh issue create \
  --title "📚 Document the label system" \
  --body "..." \
  --label "agent-work,spawn-pending,documentation"

# 3. Auto-review merges spawn PR
gh pr merge $PR_NUMBER --squash

# 4. Auto-review removes spawn-pending and adds copilot label
gh issue edit $WORK_ISSUE --remove-label "spawn-pending"
gh issue edit $WORK_ISSUE --add-label "copilot"

# 5. Copilot assignment workflow assigns issue
gh issue edit $WORK_ISSUE --add-label "copilot-assigned"

# 6. Copilot creates PR with implementation
gh pr create \
  --title "Add LABELS.md documentation" \
  --body "Closes #$WORK_ISSUE" \
  --label "copilot,automated,documentation"

# 7. Auto-review merges PR and closes issue
gh pr merge $PR_NUMBER --squash
gh issue close $WORK_ISSUE
gh issue edit $WORK_ISSUE --add-label "completed"
```

### Example 2: AI-Generated Idea Flow

```bash
# 1. Idea generator creates issue
gh issue create \
  --title "💡 Implement dark mode for GitHub Pages" \
  --body "..." \
  --label "ai-generated,enhancement,automated"

# 2. Copilot assignment workflow picks it up
gh issue edit $ISSUE_NUMBER --add-label "copilot-assigned"

# 3. Copilot creates PR
gh pr create \
  --title "Implement dark mode" \
  --body "Closes #$ISSUE_NUMBER" \
  --label "copilot,enhancement,automated"

# 4. Auto-review approves and merges
gh pr merge $PR_NUMBER --squash

# 5. Issue closed with completed label
gh issue close $ISSUE_NUMBER
gh issue edit $ISSUE_NUMBER --add-label "completed"
```

### Example 3: Workflow Failure Handling

```bash
# 1. Workflow fails, failure handler creates issue
gh issue create \
  --title "⚠️ Workflow Failure: Daily Goal Generator" \
  --body "..." \
  --label "workflow-failure,automated"

# 2. Developer fixes the workflow
gh pr create \
  --title "Fix goal generator workflow" \
  --body "Closes #$FAILURE_ISSUE" \
  --label "workflow-optimization"

# 3. PR merged, failure issue closed
gh pr merge $PR_NUMBER --squash
gh issue close $FAILURE_ISSUE
gh issue edit $FAILURE_ISSUE --add-label "completed"
```

---

## 🔍 Label Relationships

### Common Label Combinations

| Combination | Meaning | Example Use Case |
|-------------|---------|------------------|
| `ai-generated` + `enhancement` | AI-created feature request | Daily idea generation output |
| `agent-work` + `spawn-pending` | Agent work waiting for spawn | Work issue blocked by spawn PR |
| `copilot-assigned` + `copilot` | Issue assigned to Copilot, PR created | Full autonomous cycle |
| `automated` + `copilot` | Fully automated Copilot work | Auto-merge eligible PR |
| `workflow-failure` + `automated` | Automated failure detection | System self-monitoring |
| `agent-system` + `announcement` | Agent spawn announcement | New agent introduction |
| `learning` + `automated` | Auto-captured learning | TLDR/HN learning ingestion |
| `documentation` + `agent-created` | Doc written by agent | Doc-master agent output |

### Mutually Exclusive Labels

These labels should not appear together:

- `copilot-assigned` and `copilot` (one is for issues, one is for PRs)
- `in-progress` and `completed` (different lifecycle stages)
- `spawn-pending` and `completed` (spawn must complete before closure)

---

## 🔗 Related Documentation

- **[AGENT_QUICKSTART.md](AGENT_QUICKSTART.md)** - Agent system overview
- **[COPILOT_SETUP.md](COPILOT_SETUP.md)** - Copilot integration setup
- **[AUTONOMOUS_CYCLE.md](AUTONOMOUS_CYCLE.md)** - Full autonomous development cycle
- **[WORKFLOW_TRIGGERS.md](WORKFLOW_TRIGGERS.md)** - Workflow scheduling and triggers
- **[FAQ.md](FAQ.md)** - Frequently asked questions

---

## 📝 Label Management

### Creating Labels

Labels are automatically created by the `system-kickoff.yml` workflow during initial setup. To manually create a label:

```bash
gh label create "label-name" \
  --color "HEXCOLOR" \
  --description "Description of the label"
```

### Modifying Labels

To update a label's color or description:

```bash
gh label edit "label-name" \
  --color "HEXCOLOR" \
  --description "New description"
```

### Deleting Labels

⚠️ **Caution:** Deleting labels used by workflows will break automation.

```bash
gh label delete "label-name"
```

---

## 🎨 Color Scheme

The Chained label system uses a consistent color scheme:

- **Purple** (`#7057ff`, `#7057ff`, `#5319e7`) - AI/Agent system
- **Blue** (`#0366d6`, `#0075ca`, `#1d76db`) - Copilot, documentation, quality
- **Green** (`#0e8a16`) - Success, completion, agent work
- **Yellow** (`#fbca04`, `#e4e669`) - In-progress, automated, warnings
- **Red** (`#d73a4a`) - Failures, alerts, critical issues
- **Light Blue** (`#a2eeef`, `#c5def5`) - Enhancements, progress reports
- **Orange** (`#d93f0b`) - Learning, insights
- **Gold** (`#ffd700`) - Goals, achievements
- **Brown** (`#8b4513`) - Archaeology, historical analysis
- **Light Purple** (`#d4c5f9`) - Pending states

---

## 🤝 Contributing

When contributing to workflows, please:

1. **Use existing labels** whenever possible
2. **Follow naming conventions**: lowercase with hyphens
3. **Update this documentation** when adding new labels
4. **Test label behavior** in workflows before deploying
5. **Consider label relationships** and lifecycle

---

## ❓ FAQ

### Q: Why do we need both "copilot" and "copilot-assigned"?
**A:** They serve different purposes in the autonomous cycle:
- `copilot-assigned` = Copilot should work on this issue
- `copilot` = Copilot created this PR (enables auto-merge)

### Q: What happens if I remove the "spawn-pending" label manually?
**A:** The Copilot assignment workflow will immediately pick up the work issue and assign it to Copilot, even if the agent spawn isn't complete. This could cause issues if the agent doesn't exist yet.

### Q: Can I add custom labels to my issues?
**A:** Yes! Custom labels won't interfere with automation, but they won't trigger any automated workflows either.

### Q: Why are some labels required for auto-merge?
**A:** The `copilot` label is a security measure to ensure only Copilot-created content is automatically merged without human review.

### Q: How do I find all issues with a specific label?
**A:**
```bash
gh issue list --label "label-name"
gh issue list --label "label1,label2"  # Multiple labels (AND)
```

---

*Last updated: 2025-11-12*  
*Part of the Chained autonomous AI motion machine*  
*For questions or updates, create an issue with the `documentation` label*
