# Workflow-Driven Multi-Agent Coordination

**Implemented by:** @coordinate-wizard (Quincy Jones style 🎹)  
**Supported by:** @meta-coordinator  
**Status:** ✅ Complete and Ready for Use

## Overview

This system enables **automated multi-agent coordination** through GitHub Actions workflows. When you have a complex task that requires multiple specialized agents, simply add the `coordination-needed` label and the system handles everything else!

## 🎯 What It Does

The workflow-driven coordination system:

1. **Analyzes** task complexity automatically
2. **Creates** a coordination plan with sub-tasks
3. **Spawns** sub-issues and assigns specialized agents
4. **Tracks** progress across all sub-tasks
5. **Aggregates** results when complete
6. **Updates** the parent issue automatically

All through GitHub Actions workflows - no manual intervention required!

## 🚀 Quick Start

### For Users: How to Request Coordination

1. **Create an issue** describing your complex task
2. **Add the label** `coordination-needed`
3. **Wait** for the workflow to analyze (usually <2 minutes)
4. **Review** the coordination plan posted in comments
5. **Track** progress as agents work on sub-tasks

That's it! The system handles the rest.

### Example

```bash
# Create issue
gh issue create \
  --title "Build user authentication system" \
  --body "We need a complete auth system with OAuth, JWT, and security best practices" \
  --label "coordination-needed"

# The workflow will:
# - Analyze complexity (likely "complex" or "highly_complex")
# - Create coordination plan
# - Spawn sub-issues:
#   1. Design auth architecture (@engineer-master)
#   2. Security review (@secure-specialist)
#   3. Implement endpoints (@engineer-master)
#   4. Add tests (@assert-specialist)
#   5. Write documentation (@document-ninja)
# - Track progress as each agent completes their work
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  User Creates Issue                     │
│  + Adds "coordination-needed" label     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Workflow: auto-coordinate-agents.yml   │
│                                         │
│  Job 1: Analyze Complexity              │
│  └─ Uses meta_agent_coordinator.py      │
│                                         │
│  Job 2: Create Coordination Plan        │
│  └─ Decomposes into sub-tasks           │
│  └─ Selects best agent for each         │
│                                         │
│  Job 3: Spawn Sub-Task Issues           │
│  └─ Creates issue for each sub-task     │
│  └─ Assigns agents                      │
│                                         │
│  Job 4: Update Parent Issue             │
│  └─ Posts coordination plan             │
│  └─ Adds progress tracking              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Agents Work on Sub-Tasks               │
│  (Each in their own issue + PR)         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Workflow: track-coordination-progress  │
│                                         │
│  Triggers:                              │
│  - Sub-issue closed                     │
│  - PR merged                            │
│                                         │
│  Actions:                               │
│  - Updates progress in parent issue     │
│  - Shows completion percentage          │
│  - Marks complete when all done         │
└─────────────────────────────────────────┘
```

## 📋 Workflows

### 1. Auto-Coordinate Agents (`auto-coordinate-agents.yml`)

**Triggers:**
- Issue labeled with `coordination-needed`
- Issue opened with `coordination-needed` label
- Manual dispatch with issue number

**Jobs:**
1. **analyze** - Determines task complexity
2. **coordinate** - Creates coordination plan
3. **spawn_subtasks** - Creates sub-issues
4. **update_parent** - Posts plan to parent issue

**Outputs:**
- Coordination plan in parent issue
- Sub-task issues created with agent assignments
- Progress tracking section added

### 2. Track Coordination Progress (`track-coordination-progress.yml`)

**Triggers:**
- Sub-task issue closed
- Sub-task PR merged
- Manual dispatch for update

**Jobs:**
1. **update_progress** - Calculates and posts progress

**Outputs:**
- Progress bar showing completion
- List of completed vs pending tasks
- Completion message when all done

## 🎯 Task Complexity Levels

The system analyzes tasks and categorizes them:

| Complexity | Description | Coordination Needed? |
|------------|-------------|---------------------|
| **Simple** | Single agent, straightforward | ❌ No |
| **Moderate** | Single agent, complex | ❌ No |
| **Complex** | Multiple agents, sequential | ✅ Yes |
| **Highly Complex** | Multiple agents, parallel + dependencies | ✅ Yes |

**Simple and Moderate** tasks are handled by single agents. The workflow will comment on the issue recommending a single agent assignment.

**Complex and Highly Complex** tasks trigger full coordination.

## 🔧 Integration with Existing Systems

This workflow-driven coordination **complements** existing systems:

| System | Purpose | When to Use |
|--------|---------|-------------|
| **meta-coordinator** | Ad-hoc CLI-based coordination | Manual coordination needs |
| **meta-coordinator-system** | Autonomous system orchestration | System-level automation |
| **a2a-coordinator** | A2A protocol multi-agent workflows | Real-time agent-to-agent communication |
| **Workflow Coordination** (THIS) | Automated GitHub Actions coordination | Issue-driven multi-agent work |

**Use this workflow system** when:
- You have a complex issue requiring multiple agents
- You want automated coordination
- You want to track progress via GitHub issues
- You prefer declarative, workflow-based orchestration

**Use meta-coordinator CLI** when:
- You need manual control over coordination
- Testing coordination strategies
- One-off coordination needs

## 👥 Agent Selection

The system uses intelligent agent selection based on:

1. **Specialization Match** - Agent expertise vs sub-task requirements
2. **Performance History** - From agent registry and performance tracking
3. **Current Workload** - Avoids overloading high-performing agents
4. **Task Complexity** - Matches agent capabilities to difficulty

Example agent assignments:
- API design → @engineer-master or @APIs-architect
- Security review → @secure-specialist
- Testing → @assert-specialist or @validator-pro
- Performance optimization → @accelerate-master
- Documentation → @document-ninja or @support-master

## 📊 Progress Tracking

Progress is tracked automatically through:

**Visual Progress Bar:**
```
██████████░░░░░░░░░░ 50%
```

**Task Lists:**
- ✅ Completed sub-tasks (with PR links)
- 🔄 In-progress sub-tasks
- ⏸️ Blocked sub-tasks (if any)

**Metrics:**
- Overall completion percentage
- Number of completed vs total tasks
- Updated timestamps

**Automatic Updates:**
- When sub-task issue closes
- When linked PR merges
- Manual trigger if needed

## 🎨 Customization

### Force Coordination on Simple Tasks

```yaml
# Manually trigger workflow with force flag
gh workflow run auto-coordinate-agents.yml \
  -f issue_number=123 \
  -f force_coordinate=true
```

### Modify Coordination Logic

Edit `tools/meta_agent_coordinator.py` to adjust:
- Task decomposition rules
- Agent selection criteria
- Complexity thresholds
- Execution order optimization

### Add Custom Labels

Modify workflows to handle additional labels:
```yaml
- label: ["coordination-needed", "high-priority"]
```

## 🧪 Testing

### Test with Sample Issue

```bash
# Create test issue
gh issue create \
  --title "Test: Build REST API with auth" \
  --body "Create a REST API with authentication, rate limiting, and documentation" \
  --label "coordination-needed,test"

# Watch workflow
gh run list --workflow=auto-coordinate-agents.yml

# Check created sub-issues
gh issue list --label "coordination-subtask"
```

### Manual Workflow Dispatch

```bash
# Trigger coordination for existing issue
gh workflow run auto-coordinate-agents.yml \
  -f issue_number=123

# Trigger progress update
gh workflow run track-coordination-progress.yml \
  -f parent_issue=123
```

## 📈 Metrics and Monitoring

Track coordination effectiveness:

1. **Coordination Success Rate** - % of coordinations that complete successfully
2. **Average Time to Complete** - Time from start to all sub-tasks done
3. **Agent Utilization** - Distribution of work across agents
4. **Sub-task Completion Rate** - % of sub-tasks completed vs abandoned

View in workflow runs:
```bash
gh run list --workflow=auto-coordinate-agents.yml --json conclusion,createdAt
```

## 🎓 Examples

### Example 1: Feature Development

**Issue:** "Implement user profile management"

**Coordination Plan Created:**
1. **Design data model** (@engineer-master)
2. **Security review** (@secure-specialist)  
3. **Implement CRUD endpoints** (@engineer-master)
4. **Add validation tests** (@assert-specialist)
5. **UI components** (@designer-chief)
6. **Documentation** (@document-ninja)

**Execution:** Sequential with some parallel work (testing + UI in parallel)

**Result:** Complete feature with tests and docs

### Example 2: System Refactoring

**Issue:** "Refactor codebase for performance"

**Coordination Plan Created:**
1. **Performance analysis** (@investigate-champion)
2. **Identify bottlenecks** (@accelerate-master)
3. **Refactor core logic** (@organize-guru)
4. **Optimize algorithms** (@accelerate-specialist)
5. **Update tests** (@validator-pro)
6. **Benchmark results** (@accelerate-master)

**Execution:** Sequential pipeline

**Result:** Optimized codebase with metrics

### Example 3: Security Audit

**Issue:** "Complete security audit"

**Coordination Plan Created:**
1. **Code security scan** (@secure-specialist)
2. **Dependency audit** (@guardian-master)
3. **API security review** (@secure-pro)
4. **Infrastructure review** (@cloud-architect)
5. **Document findings** (@document-ninja)
6. **Create remediation plan** (@secure-specialist)

**Execution:** Parallel scans, sequential reporting

**Result:** Comprehensive security report

## 🛠️ Troubleshooting

### Issue Not Being Coordinated

**Problem:** Label added but workflow doesn't run

**Solutions:**
- Check workflow file exists: `.github/workflows/auto-coordinate-agents.yml`
- Verify label is exactly `coordination-needed` (case-sensitive)
- Check workflow runs: `gh run list --workflow=auto-coordinate-agents.yml`
- View workflow logs for errors

### Wrong Agent Assigned

**Problem:** Sub-task assigned to incorrect agent

**Solutions:**
- Update agent specializations in `.github/agents/`
- Modify `meta_agent_coordinator.py` agent selection logic
- Manually reassign by editing sub-issue

### Progress Not Updating

**Problem:** Sub-tasks complete but parent not updated

**Solutions:**
- Check sub-issue has "Parent Issue: #X" in body
- Verify `track-coordination-progress.yml` workflow exists
- Manually trigger: `gh workflow run track-coordination-progress.yml -f parent_issue=X`

## 📚 Related Documentation

- **Meta-Coordinator Agent**: `.github/agents/meta-coordinator.md`
- **Agent System**: `docs/AGENT_QUICKSTART.md`
- **Workflow Development**: `docs/guides/workflow-development.md`
- **Agent Performance Tracking**: `.github/agent-system/registry.json`

## 🎹 Credits

**Implemented by:** @coordinate-wizard  
*"Orchestrating diverse talents toward a unified goal"*

**Supported by:** @meta-coordinator  
*"Systematic and collaborative, with strategic vision"*

**Inspired by:** Quincy Jones (versatile and integrative producer)

---

## 🚀 Get Started

Ready to coordinate multiple agents on your complex task?

```bash
# Just add the label!
gh issue edit YOUR_ISSUE_NUMBER --add-label "coordination-needed"
```

The workflow handles the rest! 🎹
