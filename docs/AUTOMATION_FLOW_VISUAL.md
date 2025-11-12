# Automation Workflow Visual Flow Diagram

## Complete System Flow (User Creates Issue → Merged PR)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER ACTION (Only Manual Step)                  │
│                                                                         │
│                     User creates GitHub Issue                          │
│                   (Any topic, any specialization)                      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               │ GitHub Event: issues.opened
                               │
    ┌──────────────────────────┴──────────────────────────┐
    │                                                      │
    v                                                      v
┌───────────────────────────────────┐        ┌─────────────────────────────┐
│  copilot-graphql-assign.yml       │        │     agent-spawner.yml       │
│  Trigger: issues.opened + cron    │        │     Trigger: cron */3h      │
│  Runs: Immediately + every 3h     │        │     Runs: Every 3 hours     │
└──────────────┬────────────────────┘        └─────────┬───────────────────┘
               │                                        │
               │ 1. Check labels:                       │ 1. Check capacity
               │    - Skip if spawn-pending            │ 2. Generate agent
               │    - Skip if agent-system only        │ 3. Register agent
               │ 2. Check assignees                    │ 4. Create profile
               │ 3. Assign to Copilot via GraphQL      │
               │                                        v
               │                              ┌─────────────────────────┐
               │                              │  Creates 2 things:      │
               │                              │  1. Spawn PR (agent     │
               │                              │     registration)        │
               │                              │  2. Work Issue with     │
               │                              │     spawn-pending label │
               │                              └───────┬─────────────────┘
               │                                      │
               v                                      v
┌──────────────────────────────────┐      ┌─────────────────────────────┐
│  Issue Assigned to Copilot       │      │  Issue with spawn-pending   │
│  (with custom agent directive)   │      │  (blocked from assignment)  │
└──────────────┬───────────────────┘      └─────────┬───────────────────┘
               │                                     │
               │ Copilot analyzes issue             │ Waiting for spawn PR
               │ Copilot creates branch             │ to merge
               │                                     │
               v                                     │
┌──────────────────────────────────┐                │
│  Copilot opens PR                │                │
│  (in draft or ready state)       │                │
└──────────────┬───────────────────┘                │
               │                                     │
               └─────────────┬───────────────────────┘
                             │
                             │ Both PRs enter review cycle
                             │
                             v
                ┌────────────────────────────────────┐
                │   auto-review-merge.yml            │
                │   Trigger: PR events + cron */15m  │
                │   Runs: Every 15 minutes           │
                └─────────────┬──────────────────────┘
                              │
                              │ For Each Open PR:
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        v                     v                     v
┌───────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Check Labels  │   │ Check Draft      │   │ Check Author     │
│ - copilot     │   │ - Convert if     │   │ - Owner + label  │
│ - agent-sys   │   │   ready          │   │ - Bot + label    │
└───────┬───────┘   └────────┬─────────┘   └────────┬─────────┘
        │                    │                       │
        └────────────────────┴───────────────────────┘
                             │
                             │ Auto-merge decision
                             │
                ┌────────────┴────────────┐
                │                         │
                v                         v
         ┌──────────────┐        ┌───────────────────┐
         │  Regular PR  │        │  Agent Spawn PR   │
         │  Merged      │        │  Merged           │
         └──────┬───────┘        └─────────┬─────────┘
                │                          │
                │                          │ Special handling:
                │                          │ 1. Find linked work issue
                │                          │ 2. Remove spawn-pending
                │                          │ 3. Add copilot label
                │                          │ 4. Trigger assign workflow
                │                          │
                │                          v
                │                ┌─────────────────────────┐
                │                │  Immediate Assignment   │
                │                │  gh workflow run        │
                │                │  copilot-graphql-assign │
                │                └───────────┬─────────────┘
                │                            │
                │                            v
                │                ┌─────────────────────────┐
                │                │  Work Issue Assigned    │
                │                │  to Copilot             │
                │                └───────────┬─────────────┘
                │                            │
                │                            │ Copilot creates PR
                │                            │
                └────────────────────────────┴──────────────┘
                                     │
                                     v
                          ┌──────────────────────┐
                          │  Issue Closed        │
                          │  (via PR link)       │
                          └──────────────────────┘
```

## Timing Analysis

### Scenario 1: Regular Issue (Fastest Path)

```
T+0s      User creates issue
T+0s      issues.opened event fires
T+0s      copilot-graphql-assign.yml triggered
T+5s      Issue assigned to Copilot
T+30s-5m  Copilot analyzes and creates PR (variable)
T+5m      PR opened (draft or ready)
T+5m-20m  auto-review-merge runs (up to 15min wait)
T+20m     PR merged
T+20m     Issue closed
```

**Total Time: 20-30 minutes** (mostly Copilot thinking + auto-review schedule)

### Scenario 2: Agent Spawn Issue (With Optimization)

```
T+0h      agent-spawner.yml runs (every 3h)
T+0h      Spawn PR created
T+0h      Work issue created (spawn-pending)
T+0-15m   auto-review-merge runs
T+15m     Spawn PR merged
T+15m     spawn-pending removed
T+15m     Copilot assignment triggered immediately
T+15m+5s  Work issue assigned to Copilot
T+20m-1h  Copilot creates PR
T+1h-1h15 PR merged by auto-review
T+1h15    Work issue closed
```

**Total Time: 1-1.5 hours** (agent spawn + Copilot work + auto-review)

### Scenario 3: Agent Spawn Issue (Without Optimization - Old Behavior)

```
T+0h      agent-spawner.yml runs
T+0h      Spawn PR + work issue created
T+0-15m   auto-review-merge runs
T+15m     Spawn PR merged
T+15m     spawn-pending removed
T+15m     Copilot assignment SCHEDULED (not immediate)
T+15m-3h  Wait for next copilot-assign cron
T+3h      Work issue assigned
T+3h-4h   Copilot creates PR
T+4h-5h   PR merged
```

**Total Time: 4-5 hours** (due to scheduled assignment delay)

**Optimization Impact**: 3.5-4 hour reduction! 🎉

## Key Design Decisions

### 1. Label-Based Flow Control

```
Labels as State Machine:

spawn-pending → Blocks assignment until spawn PR merges
agent-system  → Handled by spawner, not regular flow
agent-work    → Can be assigned after spawn completes
copilot       → Enables auto-merge
copilot-assigned → Tracking label
```

### 2. Trust-Based Auto-Merge

```
Auto-Merge Criteria:
  IF (author == repo_owner AND has_copilot_label) OR
     (author == trusted_bot AND has_copilot_label)
  THEN
    approve/comment (as appropriate)
    merge immediately
    handle special cases (agent-spawn)
  ENDIF
```

### 3. Schedule vs. Event-Driven

```
Event-Driven (Fast):
  - issues.opened → immediate assignment
  - pull_request.* → immediate review
  - spawn PR merge → immediate assignment trigger

Schedule-Based (Safety Net):
  - */3h → catch missed assignments
  - */15m → batch review all open PRs
  - daily → agent evaluation
```

## Failure Modes & Recovery

### Failure: Assignment Fails (No Copilot Access)

```
copilot-graphql-assign → 
  ❌ Can't find Copilot actor →
    Add comment explaining issue →
      Add copilot-assigned label for tracking →
        Manual: User can assign from UI
```

**Recovery**: 
- Scheduled run retries in 3 hours
- Manual assignment possible
- Issue labeled for tracking

### Failure: PR Can't Merge (Conflicts)

```
auto-review-merge → 
  ❌ mergeable != MERGEABLE →
    Add comment explaining conflict →
      Skip merge →
        Next run (15m) checks again
```

**Recovery**:
- PR remains open
- Comment added with details
- System retries every 15 minutes
- Manual merge if persistent

### Failure: Workflow Trigger Doesn't Fire

```
spawn PR merged →
  ❌ workflow_dispatch fails →
    Comment explains failure →
      Fall back to scheduled assignment
```

**Recovery**:
- Scheduled copilot-assign (3h) picks it up
- Issue remains labeled correctly
- System self-heals

## Workflow Dependencies Graph

```
system-kickoff.yml (one-time)
   │
   ├─→ Creates labels
   ├─→ Initializes directories
   └─→ Triggers initial workflows

agent-spawner.yml (cron)
   │
   ├─→ Creates: agent-system PR
   ├─→ Creates: work issue (spawn-pending)
   └─→ Depends on: auto-review-merge

copilot-graphql-assign.yml (event + cron)
   │
   ├─→ Triggered by: issues.opened
   ├─→ Triggered by: spawn PR merge
   ├─→ Depends on: COPILOT_PAT secret
   └─→ Assigns: GitHub Copilot

auto-review-merge.yml (event + cron)
   │
   ├─→ Triggered by: pull_request.*
   ├─→ Triggered by: schedule
   ├─→ Merges: PRs with copilot label
   ├─→ Special: Handles agent-spawn PRs
   └─→ Triggers: copilot-graphql-assign

agent-evaluator.yml (daily)
   │
   ├─→ Evaluates: Agent performance
   ├─→ Promotes: Top performers
   └─→ Eliminates: Poor performers

system-monitor.yml (cron)
   │
   ├─→ Checks: Workflow health
   ├─→ Creates: Alert issues
   └─→ Tracks: Failure rates

workflow-failure-handler.yml (event)
   │
   ├─→ Triggered by: workflow failures
   ├─→ Creates: Diagnostic issues
   └─→ Tags: For investigation
```

## Configuration Requirements

### Required Secrets

```yaml
COPILOT_PAT:
  Purpose: Assign issues to GitHub Copilot
  Scope: repo (full control)
  Why: GITHUB_TOKEN can't assign Copilot due to licensing
  Usage: copilot-graphql-assign.yml, auto-review-merge.yml
```

### Required Labels

```yaml
copilot:         "Marks Copilot PRs for auto-merge"
copilot-assigned: "Tracking label for assigned issues"
agent-system:    "Agent ecosystem activity"
agent-work:      "Work assigned to agents"
spawn-pending:   "Waiting for spawn PR to merge"
automated:       "Auto-generated content"
```

### Repository Settings

```yaml
GitHub Copilot:
  Enabled: true
  Subscription: Required (Individual/Business/Enterprise)

Actions:
  Allow: All actions
  Permissions: Read/Write for workflows
```

## Monitoring & Metrics

### Key Metrics Tracked

1. **Assignment Success Rate**
   - Tracked in workflow logs
   - Creates alert if <80%

2. **Merge Success Rate**
   - PRs merged vs. created
   - Tracks auto-merge effectiveness

3. **Time to Assignment**
   - Issue created → Copilot assigned
   - Target: <1 minute

4. **Time to Merge**
   - PR created → Merged
   - Target: <20 minutes

5. **Agent Spawn Cycle**
   - Spawn start → Work assigned
   - Current: ~15 minutes
   - Target: ~5 minutes

### Health Checks

```yaml
system-monitor.yml runs every 3h:
  - Workflow failure rate
  - Open PRs age
  - Unassigned issues age
  - Agent capacity

Alerts created when:
  - Failure rate >15%
  - PRs open >24h
  - Issues unassigned >6h
  - Capacity issues
```

---

**Last Updated**: 2025-11-12
**System Status**: Highly Automated ✅
**Optimization Status**: Phase 2 In Progress
