# Workflow Coordination Quick Reference

**For:** Developers using workflow-driven multi-agent coordination  
**By:** @coordinate-wizard

## 🚀 One-Liner Usage

```bash
gh issue edit ISSUE_NUM --add-label "coordination-needed"
```

That's it! The workflow does everything else.

## 📋 Workflow Commands

### Trigger Coordination

```bash
# Method 1: Add label to existing issue
gh issue edit 123 --add-label "coordination-needed"

# Method 2: Create issue with label
gh issue create \
  --title "Complex task description" \
  --body "Detailed requirements..." \
  --label "coordination-needed"

# Method 3: Manual workflow dispatch
gh workflow run auto-coordinate-agents.yml -f issue_number=123
```

### Monitor Progress

```bash
# List coordination workflow runs
gh run list --workflow=auto-coordinate-agents.yml --limit 5

# View specific run
gh run view RUN_ID

# List sub-task issues
gh issue list --label "coordination-subtask"

# Check parent issue status
gh issue view 123
```

### Update Progress Manually

```bash
# Trigger progress update
gh workflow run track-coordination-progress.yml -f parent_issue=123
```

## 🎯 Task Complexity Guide

| Keywords in Issue | Likely Complexity | Coordination? |
|-------------------|-------------------|---------------|
| "and", "also", "plus" (1-2 times) | Moderate | ❌ |
| Multiple specializations mentioned | Complex | ✅ |
| "system", "complete", "end-to-end" | Complex | ✅ |
| Architecture + implementation + testing | Highly Complex | ✅ |
| >5 different aspects to handle | Highly Complex | ✅ |

## 🔧 Agent Assignment Patterns

| Sub-Task Type | Typical Agent |
|---------------|---------------|
| API design, architecture | @engineer-master, @APIs-architect |
| Security review, audit | @secure-specialist, @guardian-master |
| Testing, QA | @assert-specialist, @validator-pro |
| Performance optimization | @accelerate-master, @optimizer-architect |
| Documentation | @document-ninja, @support-master |
| Refactoring, cleanup | @organize-guru, @refactor-champion |
| Infrastructure, deployment | @create-botter, @infrastructure-specialist |
| UI/UX design | @designer-chief, @prototype-interfaces-maven |

## 📊 Progress Bar Legend

```
██████████████████░░ 90%  - Almost done!
█████████░░░░░░░░░░░ 45%  - About halfway
███░░░░░░░░░░░░░░░░░ 15%  - Just started
████████████████████ 100% - Complete! 🎉
```

## 🎨 Sub-Issue Format

Every coordination sub-task follows this format:

```markdown
## 🎯 Coordination Sub-Task

**Parent Issue:** #123
**Coordination ID:** coord-20241224-...
**Sub-Task ID:** task-1

### Task Description
[Specific task description]

### Requirements
**Specializations Required:**
- api-design
- security

**Dependencies:**
- task-0 must complete first

**Estimated Effort:** medium
**Priority:** 8/10

### Completion Criteria
- [ ] Criterion 1
- [ ] Criterion 2

---

**Assigned Agent:** @agent-name

When complete:
1. Close this issue
2. Link your PR
3. Progress tracked automatically
```

## 🎯 Workflow States

| Label | Meaning |
|-------|---------|
| `coordination-needed` | User requests coordination |
| `coordination-active` | Plan created, agents working |
| `coordination-subtask` | This is a sub-task |
| `coordination-complete` | All sub-tasks done |

## 🔍 Finding Your Way Around

### Find All Coordinations

```bash
# Active coordinations
gh issue list --label "coordination-active"

# Complete coordinations
gh issue list --label "coordination-complete" --state closed

# All coordination sub-tasks
gh issue list --label "coordination-subtask"
```

### Find Specific Coordination

```bash
# By coordination ID (in comments)
gh issue list --search "coord-20241224"

# By parent issue
gh issue list --search "Parent Issue: #123"
```

## 🧪 Test Scenarios

### Basic Test

```bash
# Create simple test
gh issue create \
  --title "Test: Simple task" \
  --body "This should NOT trigger coordination" \
  --label "coordination-needed"

# Expected: Comment saying task is too simple
```

### Complex Test

```bash
# Create complex test
gh issue create \
  --title "Test: Build authentication system" \
  --body "Build complete auth with OAuth, JWT, testing, and docs" \
  --label "coordination-needed"

# Expected: 4-5 sub-issues created
```

### Manual Coordination

```bash
# Force coordination on simple task
gh workflow run auto-coordinate-agents.yml \
  -f issue_number=123 \
  -f force_coordinate=true
```

## 🐛 Troubleshooting Quick Fixes

### Coordination Didn't Start

```bash
# Check workflow ran
gh run list --workflow=auto-coordinate-agents.yml --limit 1

# Check label is correct
gh issue view ISSUE_NUM --json labels

# Trigger manually
gh workflow run auto-coordinate-agents.yml -f issue_number=ISSUE_NUM
```

### Progress Not Updating

```bash
# Check sub-issue has parent reference
gh issue view SUB_ISSUE_NUM --json body

# Trigger update manually
gh workflow run track-coordination-progress.yml -f parent_issue=PARENT_NUM
```

### Wrong Agent Assigned

```bash
# Check agent specializations
cat .github/agents/AGENT_NAME.md

# Reassign by updating issue assignee
gh issue edit SUB_ISSUE_NUM --add-assignee @CORRECT_AGENT
```

## 📈 Metrics to Track

```bash
# Coordination success rate
active=$(gh issue list --label "coordination-active" --json number --jq 'length')
complete=$(gh issue list --label "coordination-complete" --state closed --json number --jq 'length')
echo "Success rate: $complete / ($active + $complete)"

# Average sub-tasks per coordination
subtasks=$(gh issue list --label "coordination-subtask" --json number --jq 'length')
coordinations=$(gh issue list --label "coordination-active,coordination-complete" --json number --jq 'length')
echo "Avg sub-tasks: $subtasks / $coordinations"
```

## 🎹 Pro Tips

1. **Write Detailed Issue Bodies** - More context = better coordination plans
2. **Use Clear Task Names** - Helps with sub-task titles
3. **Mention Required Skills** - Guides agent selection
4. **List Dependencies** - Workflow respects execution order
5. **Check Progress Often** - Use progress tracking workflow

## 🔗 Quick Links

- **Full Documentation**: `docs/WORKFLOW_COORDINATION.md`
- **Workflow File**: `.github/workflows/auto-coordinate-agents.yml`
- **Progress Tracking**: `.github/workflows/track-coordination-progress.yml`
- **Coordinator Logic**: `tools/meta_agent_coordinator.py`
- **Agent Profiles**: `.github/agents/`

## 🎯 Examples by Type

### Example: Feature Development

```bash
gh issue create \
  --title "Implement user dashboard" \
  --body "Create user dashboard with analytics, charts, and export functionality" \
  --label "coordination-needed,feature"
```

### Example: Bug Fix Coordination

```bash
gh issue create \
  --title "Fix authentication flow issues" \
  --body "Multiple auth issues: OAuth callback, JWT refresh, session expiry" \
  --label "coordination-needed,bug"
```

### Example: Refactoring

```bash
gh issue create \
  --title "Refactor API layer" \
  --body "Refactor API layer for better maintainability and performance" \
  --label "coordination-needed,refactor"
```

## 🎵 The Quincy Jones Approach

> "The whole is greater than the sum of its parts"

Coordination is about bringing together diverse talents to create something greater. Each agent contributes their expertise, and the workflow orchestrates them into a unified solution.

That's the @coordinate-wizard way! 🎹

---

**Need help?** Check the full documentation in `docs/WORKFLOW_COORDINATION.md`
