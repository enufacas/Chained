# A2A Branch-Based Coordination for Custom Agents

## Overview

This document describes how **custom agents in separate Copilot sessions** can communicate using **Git branches as a message bus**. This solves the cross-runner communication challenge where HTTP isn't available between distinct GitHub Actions workflow runs.

## The Problem

From `A2A_COPILOT_REALITY_CHECK.md`, we learned:
- Each custom agent (@engineer-master, @secure-specialist) runs as a **separate Copilot session**
- Each session is a **distinct GitHub Actions workflow run**
- Different runs = **different runner environments** = **no shared localhost HTTP**

**Traditional A2A Tier 1 (HTTP)** won't work because agents aren't on the same runner.

## The Solution: Branches as Message Bus

**Git branches persist across workflow runs** and are accessible to all runners. We can use branches to store:
- Task definitions (JSON-RPC messages)
- Status updates
- Results
- Artifacts

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Coordinator (Agent A, Run #19694551275)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Create branch: a2a-tasks/secure-review-abc123     │   │
│  │ 2. Write task.json: {method, params, ...}            │   │
│  │ 3. git push origin a2a-tasks/secure-review-abc123    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │  GitHub Branch  │
                    │  a2a-tasks/     │
                    │  secure-review  │
                    └─────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Worker Agent (Agent B, Run #19694567890)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 4. Triggered by push event / issue assignment        │   │
│  │ 5. git fetch && checkout a2a-tasks/secure-review...  │   │
│  │ 6. Read task.json, execute work                      │   │
│  │ 7. Write result.json                                 │   │
│  │ 8. git push (same branch)                            │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Coordinator (Agent A, same or new run)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 9. Poll branch for result.json                       │   │
│  │ 10. Read result, aggregate                           │   │
│  │ 11. Delete branch (cleanup)                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Message Format

Using **JSON-RPC 2.0** for consistency with MCP:

### Task File (`task.json`)

```json
{
  "jsonrpc": "2.0",
  "id": "task-abc123-def456",
  "method": "agent.execute",
  "params": {
    "agent": "secure-specialist",
    "task": "review_security",
    "context": {
      "issue_number": 100,
      "pr_number": 3066,
      "files_changed": ["src/api.py", "src/auth.py"],
      "description": "Review authentication implementation for vulnerabilities"
    },
    "requirements": {
      "check_sql_injection": true,
      "check_xss": true,
      "check_auth_bypass": true
    }
  },
  "metadata": {
    "created_at": "2025-11-26T06:30:00Z",
    "coordinator": "a2a-coordinator",
    "coordinator_run_id": "19694551275",
    "timeout_seconds": 600,
    "priority": "high"
  }
}
```

### Status File (`status.json`)

```json
{
  "task_id": "task-abc123-def456",
  "status": "working",
  "agent": "secure-specialist",
  "agent_run_id": "19694567890",
  "started_at": "2025-11-26T06:31:00Z",
  "progress": {
    "current_step": "Analyzing authentication flow",
    "percent_complete": 45
  }
}
```

**Status values**: `submitted`, `working`, `completed`, `failed`, `timeout`

### Result File (`result.json`)

```json
{
  "jsonrpc": "2.0",
  "id": "task-abc123-def456",
  "result": {
    "status": "success",
    "findings": [
      {
        "severity": "high",
        "type": "sql_injection",
        "file": "src/api.py",
        "line": 42,
        "description": "Unsanitized user input in SQL query",
        "recommendation": "Use parameterized queries"
      },
      {
        "severity": "medium",
        "type": "weak_password",
        "file": "src/auth.py",
        "line": 15,
        "description": "Password minimum length is only 6 characters",
        "recommendation": "Increase to 12+ characters"
      }
    ],
    "summary": "Found 2 security issues: 1 high, 1 medium",
    "artifacts": ["security-report.pdf", "scan-results.json"]
  },
  "metadata": {
    "completed_at": "2025-11-26T06:36:00Z",
    "duration_seconds": 300,
    "agent": "secure-specialist",
    "agent_run_id": "19694567890"
  }
}
```

### Error Result

```json
{
  "jsonrpc": "2.0",
  "id": "task-abc123-def456",
  "error": {
    "code": -32603,
    "message": "Internal error during security scan",
    "data": {
      "error_type": "ScannerException",
      "details": "Unable to parse Python AST for src/api.py",
      "traceback": "..."
    }
  },
  "metadata": {
    "failed_at": "2025-11-26T06:33:00Z",
    "agent": "secure-specialist",
    "agent_run_id": "19694567890"
  }
}
```

## Branch Naming Convention

```
a2a-tasks/{coordinator}-{task-type}-{short-uuid}
```

Examples:
- `a2a-tasks/a2a-coordinator-security-review-abc123`
- `a2a-tasks/a2a-coordinator-api-design-def456`
- `a2a-tasks/a2a-coordinator-testing-ghi789`

**Rationale**:
- Prefix `a2a-tasks/` for easy filtering
- Coordinator identifier for tracking
- Task type for human readability
- Short UUID for uniqueness

## Branch Structure

```
a2a-tasks/a2a-coordinator-security-review-abc123/
├── task.json              # Input task definition
├── status.json            # Current status (updated by worker)
├── result.json            # Final result (written by worker)
└── artifacts/             # Optional: reports, logs, etc.
    ├── security-report.pdf
    └── scan-results.json
```

## Implementation

### 1. Coordinator: Create Task

```bash
#!/bin/bash
# In coordinator workflow

TASK_ID="task-$(date +%s)-$(uuidgen | cut -c1-8)"
BRANCH_NAME="a2a-tasks/a2a-coordinator-security-review-${TASK_ID}"

# Create branch
git checkout -b "$BRANCH_NAME"

# Write task file
cat > task.json <<EOF
{
  "jsonrpc": "2.0",
  "id": "$TASK_ID",
  "method": "agent.execute",
  "params": {
    "agent": "secure-specialist",
    "task": "review_security",
    "context": {
      "issue_number": ${ISSUE_NUMBER},
      "description": "${DESCRIPTION}"
    }
  },
  "metadata": {
    "created_at": "$(date -Iseconds)",
    "coordinator": "a2a-coordinator",
    "coordinator_run_id": "${GITHUB_RUN_ID}",
    "timeout_seconds": 600
  }
}
EOF

# Initial status
cat > status.json <<EOF
{
  "task_id": "$TASK_ID",
  "status": "submitted",
  "created_at": "$(date -Iseconds)"
}
EOF

# Commit and push
git add task.json status.json
git commit -m "A2A Task: Security review $TASK_ID"
git push origin "$BRANCH_NAME"

echo "Created A2A task on branch: $BRANCH_NAME"
```

### 2. Worker Agent: Process Task

**In custom agent instructions** (e.g., `.github/agents/secure-specialist.md`):

```markdown
## A2A Protocol Integration

When assigned to an issue that includes A2A coordination:

1. **Detect A2A Task**: Check if issue body contains `A2A-TASK-BRANCH: a2a-tasks/...`
2. **Fetch branch**: 
   ```bash
   git fetch origin
   BRANCH_NAME=$(grep "A2A-TASK-BRANCH:" issue_body.txt | cut -d' ' -f2)
   git checkout "$BRANCH_NAME"
   ```
3. **Read task**:
   ```bash
   TASK=$(cat task.json)
   METHOD=$(echo "$TASK" | jq -r '.method')
   PARAMS=$(echo "$TASK" | jq '.params')
   ```
4. **Update status**:
   ```bash
   cat > status.json <<EOF
   {
     "task_id": "$(jq -r '.id' task.json)",
     "status": "working",
     "agent": "secure-specialist",
     "agent_run_id": "${GITHUB_RUN_ID}",
     "started_at": "$(date -Iseconds)"
   }
   EOF
   git add status.json
   git commit -m "A2A: Started work"
   git push origin HEAD
   ```
5. **Execute work**: Perform the actual task based on method/params
6. **Write result**:
   ```bash
   cat > result.json <<EOF
   {
     "jsonrpc": "2.0",
     "id": "$(jq -r '.id' task.json)",
     "result": {
       "status": "success",
       "findings": $(jq -c '.findings' my_results.json)
     },
     "metadata": {
       "completed_at": "$(date -Iseconds)",
       "agent": "secure-specialist"
     }
   }
   EOF
   git add result.json
   git commit -m "A2A: Completed task"
   git push origin HEAD
   ```
7. **Update issue**: Comment on original issue with summary
```

**Workflow that triggers worker** (`.github/workflows/a2a-worker-secure-specialist.yml`):

```yaml
name: A2A Worker - Secure Specialist

on:
  push:
    branches:
      - 'a2a-tasks/**-security-review-*'

jobs:
  process-task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Get branch name
        run: echo "BRANCH_NAME=${GITHUB_REF#refs/heads/}" >> $GITHUB_ENV
      
      - name: Read task
        run: |
          git checkout "$BRANCH_NAME"
          echo "TASK_ID=$(jq -r '.id' task.json)" >> $GITHUB_ENV
          echo "AGENT=$(jq -r '.params.agent' task.json)" >> $GITHUB_ENV
      
      - name: Verify agent match
        run: |
          if [ "$AGENT" != "secure-specialist" ]; then
            echo "Task not for this agent (expected secure-specialist, got $AGENT)"
            exit 0
          fi
      
      - name: Update status to working
        run: |
          cat > status.json <<EOF
          {
            "task_id": "$TASK_ID",
            "status": "working",
            "agent": "secure-specialist",
            "agent_run_id": "$GITHUB_RUN_ID",
            "started_at": "$(date -Iseconds)"
          }
          EOF
          git add status.json
          git commit -m "A2A: Started work on $TASK_ID"
          git push origin HEAD
      
      - name: Execute task via Copilot
        uses: actions/copilot-swe-agent@v1
        with:
          issue: ${{ github.event.client_payload.issue_number }}
          agent: secure-specialist
      
      # Copilot will write result.json as part of its work
      
      - name: Push results
        run: |
          git add result.json artifacts/
          git commit -m "A2A: Completed task $TASK_ID"
          git push origin HEAD
```

### 3. Coordinator: Poll and Aggregate

```bash
#!/bin/bash
# In coordinator workflow - polling loop

BRANCH_NAME="a2a-tasks/a2a-coordinator-security-review-abc123"
TIMEOUT=600
START_TIME=$(date +%s)

while true; do
  # Fetch latest
  git fetch origin "$BRANCH_NAME"
  git checkout "origin/$BRANCH_NAME" -- status.json result.json 2>/dev/null || true
  
  # Check status
  if [ -f result.json ]; then
    echo "✅ Task completed"
    RESULT=$(cat result.json)
    STATUS=$(echo "$RESULT" | jq -r '.result.status // .error.message')
    echo "Result: $STATUS"
    
    # Process result
    if [ "$(echo "$RESULT" | jq 'has("error")')" == "true" ]; then
      echo "❌ Task failed"
      ERROR=$(echo "$RESULT" | jq -r '.error.message')
      echo "Error: $ERROR"
    else
      echo "✅ Task succeeded"
      SUMMARY=$(echo "$RESULT" | jq -r '.result.summary')
      echo "Summary: $SUMMARY"
    fi
    
    break
  fi
  
  # Check timeout
  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))
  if [ $ELAPSED -gt $TIMEOUT ]; then
    echo "⏱️ Task timeout after ${ELAPSED}s"
    # Mark as timeout
    break
  fi
  
  # Check status
  if [ -f status.json ]; then
    STATUS=$(jq -r '.status' status.json)
    echo "Status: $STATUS"
  fi
  
  # Wait before next poll
  sleep 10
done

# Cleanup
git push origin --delete "$BRANCH_NAME"
echo "Deleted A2A task branch"
```

## Coordinator Workflow Example

**`.github/workflows/a2a-coordinator-orchestrate.yml`**:

```yaml
name: A2A Coordinator - Multi-Agent Orchestration

on:
  issues:
    types: [labeled]

jobs:
  coordinate:
    if: contains(github.event.issue.labels.*.name, 'a2a-orchestrate')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Parse issue and decompose
        run: |
          # Task decomposition logic
          echo "Tasks: security-review, api-design, testing" > tasks.txt
      
      - name: Create A2A tasks
        run: |
          for TASK in security-review api-design testing; do
            ./tools/a2a/create-task-branch.sh \
              --task-type "$TASK" \
              --agent "$(./tools/match-task-to-agent.sh $TASK)" \
              --issue-number ${{ github.event.issue.number }}
          done
      
      - name: Wait for completion
        run: |
          ./tools/a2a/poll-all-tasks.sh --timeout 1800
      
      - name: Aggregate results
        run: |
          ./tools/a2a/aggregate-results.sh > aggregated_results.json
      
      - name: Post summary to issue
        run: |
          gh issue comment ${{ github.event.issue.number }} \
            --body "$(cat aggregated_results.json | jq -r '.summary')"
```

## Agent Custom Instructions Template

Add to each custom agent's `.md` file:

```markdown
---
name: secure-specialist
a2a_enabled: true
a2a_methods:
  - review_security
  - scan_vulnerabilities
  - check_dependencies
---

# Secure Specialist

## A2A Protocol Support

This agent supports A2A coordination via branch-based communication.

### Supported Methods

- `review_security`: Review code for security vulnerabilities
- `scan_vulnerabilities`: Run automated security scanners
- `check_dependencies`: Check for vulnerable dependencies

### A2A Execution Flow

When assigned to an issue with A2A coordination:

1. **Detect A2A mode**: Issue body contains `A2A-TASK-BRANCH: a2a-tasks/...`
2. **Fetch task branch**:
   ```bash
   BRANCH=$(grep "A2A-TASK-BRANCH:" <<< "$ISSUE_BODY" | awk '{print $2}')
   git fetch origin "$BRANCH"
   git checkout "$BRANCH"
   ```
3. **Read and validate task**:
   ```bash
   TASK=$(cat task.json)
   METHOD=$(jq -r '.method' <<< "$TASK")
   AGENT=$(jq -r '.params.agent' <<< "$TASK")
   
   # Verify this task is for us
   if [ "$AGENT" != "secure-specialist" ]; then
     echo "Task not for this agent"
     exit 0
   fi
   ```
4. **Update status to 'working'**:
   ```bash
   cat > status.json <<EOF
   {
     "task_id": "$(jq -r '.id' <<< "$TASK")",
     "status": "working",
     "agent": "secure-specialist",
     "agent_run_id": "$GITHUB_RUN_ID",
     "started_at": "$(date -Iseconds)"
   }
   EOF
   git add status.json
   git commit -m "A2A: Started $METHOD"
   git push origin HEAD
   ```
5. **Execute the method**: Call appropriate function based on `METHOD`
6. **Write result**:
   ```bash
   cat > result.json <<EOF
   {
     "jsonrpc": "2.0",
     "id": "$(jq -r '.id' <<< "$TASK")",
     "result": {
       "status": "success",
       "findings": [...],
       "summary": "..."
     },
     "metadata": {
       "completed_at": "$(date -Iseconds)",
       "agent": "secure-specialist"
     }
   }
   EOF
   git add result.json artifacts/
   git commit -m "A2A: Completed $METHOD"
   git push origin HEAD
   ```
7. **Update original issue**: Post summary comment

### Example Task

```json
{
  "jsonrpc": "2.0",
  "id": "task-123",
  "method": "review_security",
  "params": {
    "agent": "secure-specialist",
    "context": {
      "pr_number": 3066,
      "files_changed": ["src/api.py"]
    }
  }
}
```

### Example Result

```json
{
  "jsonrpc": "2.0",
  "id": "task-123",
  "result": {
    "status": "success",
    "findings": [
      {
        "severity": "high",
        "type": "sql_injection",
        "file": "src/api.py",
        "line": 42
      }
    ],
    "summary": "Found 1 high severity issue"
  }
}
```
```

## Advantages Over Other Approaches

### vs HTTP (Tier 1)
- ✅ Works across separate runner environments
- ✅ No need for localhost coordination
- ✅ Persistent storage between runs
- ✅ Natural audit trail (git history)

### vs GitHub Issues (Tier 2)
- ✅ Cleaner (no issue tracker clutter)
- ✅ Easy cleanup (delete branch)
- ✅ Supports file artifacts (not just JSON)
- ✅ Less visible (unprotected branches)
- ✅ More control over lifecycle

### vs Direct Assignment Only
- ✅ Enables actual inter-agent communication
- ✅ Allows dependency chains (agent A → agent B → agent C)
- ✅ Supports result passing between agents
- ✅ Enables iterative refinement

## Limitations and Mitigations

### 1. Branch Proliferation
**Problem**: Many A2A tasks = many branches

**Mitigation**:
- Automatic cleanup after completion
- Retention policy (delete branches >7 days old)
- Namespace prefix for easy filtering

### 2. Concurrent Access
**Problem**: Multiple agents pushing to same branch

**Mitigation**:
- Use different files (status.json vs result.json)
- Atomic git operations
- Pull before push to handle conflicts

### 3. Discovery
**Problem**: How does worker know which branch?

**Solutions**:
1. **Issue body**: Include `A2A-TASK-BRANCH: a2a-tasks/...` in issue description
2. **Workflow trigger**: Push event filters by branch pattern
3. **GraphQL query**: Query branches matching `a2a-tasks/**`

### 4. Authentication
**Problem**: Worker needs push access

**Mitigation**:
- Use `GITHUB_TOKEN` (automatic in Actions)
- Copilot sessions have write access by default
- Branch protection rules don't apply to `a2a-tasks/**`

## Integration with Custom Agent Assignment

Combines **branch-based communication** with **direct agent assignment**:

```bash
# 1. Create task branch
BRANCH_NAME="a2a-tasks/a2a-coordinator-security-review-abc123"
./tools/a2a/create-task-branch.sh --branch "$BRANCH_NAME" --task task.json

# 2. Create sub-issue
SUB_ISSUE=$(gh issue create \
  --title "Security Review (A2A Task)" \
  --body "A2A-TASK-BRANCH: $BRANCH_NAME"$'\n\n'"Please review for vulnerabilities" \
  --label "a2a-task")

# 3. Assign custom agent
AGENT_ID=$(gh api graphql -f query='query { 
  user(login: "secure-specialist") { id }
}' | jq -r '.data.user.id')

gh api graphql -f mutation='mutation {
  assignIssue(input: {
    issueId: "'"$SUB_ISSUE"'",
    assigneeIds: ["'"$AGENT_ID"'"]
  }) { issue { id } }
}'

# 4. Copilot session starts, reads branch, executes, writes result
# 5. Coordinator polls branch for result
```

## Next Steps

To implement branch-based A2A coordination:

1. **Add A2A instructions to custom agents** (all `.github/agents/*.md` files)
2. **Create helper scripts** in `tools/a2a/`:
   - `create-task-branch.sh`
   - `poll-task-branch.sh`
   - `aggregate-results.sh`
3. **Update a2a-coordinator agent** to use branch-based coordination
4. **Test with 2-agent pipeline** (e.g., design → implement)
5. **Extend to N-agent orchestration**

## Conclusion

**Branch-based A2A coordination solves the cross-runner communication challenge** for custom agents in separate Copilot sessions. By using Git branches as a persistent message bus:

✅ Agents can communicate across distinct workflow runs  
✅ Works within GitHub Actions constraints  
✅ Supports rich data exchange (JSON + artifacts)  
✅ Easy cleanup and lifecycle management  
✅ Combines with direct agent assignment for full orchestration  

**This makes multi-Copilot agent orchestration actually feasible!** 🚀
