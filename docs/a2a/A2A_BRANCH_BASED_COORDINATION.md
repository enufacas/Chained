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

## Complete Multi-Agent Scenario: API Feature Development

This section demonstrates a realistic scenario where **a2a-coordinator** orchestrates **engineer-master** (API agent), **support-master** (documentation agent), and **accelerate-master** (performance agent) to implement a new API endpoint.

### Scenario: "Add rate-limited user search API endpoint"

**Parent Issue #500**: User story requesting a new search endpoint with rate limiting and documentation.

#### Phase 1: Coordination Agent Decomposes Task

**a2a-coordinator** analyzes the issue and creates a task decomposition:

```bash
# a2a-coordinator session (Run #19700001)

# Step 1: Analyze and decompose
TASKS=(
  "design_and_implement_api:engineer-master"
  "add_documentation:support-master"
  "optimize_performance:accelerate-master"
)

# Step 2: Create sub-issues for agent assignment
gh issue create \
  --title "[API] Implement rate-limited user search endpoint" \
  --body "Design and implement /api/v1/users/search with rate limiting..." \
  --label "api,backend"

gh issue create \
  --title "[Docs] Document user search API endpoint" \
  --body "Create API documentation for new search endpoint..." \
  --label "documentation"

gh issue create \
  --title "[Perf] Optimize user search performance" \
  --body "Profile and optimize search query performance..." \
  --label "performance"

# Step 3: Assign custom agents to sub-issues (via GraphQL)
# (This triggers Copilot sessions for each agent)
```

#### Phase 2: Engineer-Master Implements API

**engineer-master** session starts (Run #19700010), assigned to issue #501:

```bash
# engineer-master Copilot session (Run #19700010)

# Step 1: Check issue body for A2A coordination context
ISSUE_BODY=$(gh issue view 501 --json body -q .body)
PARENT_ISSUE=$(echo "$ISSUE_BODY" | grep "Parent: #500" | cut -d'#' -f2)

# Step 2: Implement the API endpoint
# (Creates src/api/search.py with rate limiting)

# Step 3: Create A2A task branch for documentation agent
TASK_ID="doc-search-api-$(date +%s)"
BRANCH_NAME="a2a-tasks/${TASK_ID}"

git checkout -b "$BRANCH_NAME"

# Write task for documentation agent
cat > task.json <<EOF
{
  "jsonrpc": "2.0",
  "id": "$TASK_ID",
  "method": "agent.document_api",
  "params": {
    "agent": "support-master",
    "task": "document_new_endpoint",
    "context": {
      "parent_issue": 500,
      "implementation_pr": 3100,
      "endpoint": "/api/v1/users/search",
      "files_to_document": [
        "src/api/search.py"
      ],
      "api_spec": {
        "method": "GET",
        "path": "/api/v1/users/search",
        "query_params": {
          "q": "Search query (required)",
          "limit": "Max results (optional, default 20)",
          "offset": "Pagination offset (optional, default 0)"
        },
        "rate_limit": "100 requests/minute per user",
        "response": {
          "users": "Array of user objects",
          "total": "Total matching users",
          "has_more": "Boolean pagination indicator"
        }
      }
    },
    "requirements": {
      "add_openapi_spec": true,
      "add_usage_examples": true,
      "add_rate_limit_docs": true,
      "update_changelog": true
    }
  },
  "metadata": {
    "created_at": "2025-11-26T07:00:00Z",
    "coordinator": "engineer-master",
    "coordinator_run_id": "19700010",
    "parent_task": "design_and_implement_api",
    "timeout_seconds": 600
  }
}
EOF

# Write status
cat > status.json <<EOF
{
  "status": "submitted",
  "submitted_at": "2025-11-26T07:00:00Z",
  "assigned_to": "support-master"
}
EOF

git add task.json status.json
git commit -m "A2A task: Document search API endpoint"
git push origin "$BRANCH_NAME"

# Step 4: Add branch reference to issue for support-master
gh issue comment 502 --body "A2A-TASK-BRANCH: ${BRANCH_NAME}
Please document the new search API endpoint. Implementation details in task.json."

# Step 5: Continue with own work - create PR for API implementation
# (engineer-master creates PR #3100)
```

#### Phase 3: Support-Master Documents API

**support-master** session starts (Run #19700020), assigned to issue #502:

```bash
# support-master Copilot session (Run #19700020)

# Step 1: Check for A2A task branch
ISSUE_BODY=$(gh issue view 502 --json body,comments -q .)
TASK_BRANCH=$(echo "$ISSUE_BODY" | grep "A2A-TASK-BRANCH:" | cut -d' ' -f2)

if [ -n "$TASK_BRANCH" ]; then
  # Step 2: Fetch and read task
  git fetch origin "$TASK_BRANCH"
  TASK_JSON=$(git show "origin/${TASK_BRANCH}:task.json")
  
  # Parse task details
  ENDPOINT=$(echo "$TASK_JSON" | jq -r '.params.context.endpoint')
  API_SPEC=$(echo "$TASK_JSON" | jq -r '.params.context.api_spec')
  
  # Step 3: Create documentation
  # - Add OpenAPI spec to docs/api/openapi.yml
  # - Create docs/api/user-search.md with usage examples
  # - Update CHANGELOG.md
  # - Add rate limiting documentation
  
  # Step 4: Write result back to A2A branch
  git checkout "$TASK_BRANCH"
  
  cat > result.json <<EOF
{
  "jsonrpc": "2.0",
  "id": "$(echo "$TASK_JSON" | jq -r '.id')",
  "result": {
    "success": true,
    "files_created": [
      "docs/api/user-search.md",
      "docs/api/rate-limiting.md"
    ],
    "files_updated": [
      "docs/api/openapi.yml",
      "CHANGELOG.md"
    ],
    "documentation_pr": 3101,
    "review_notes": "Added comprehensive usage examples including rate limit handling"
  },
  "metadata": {
    "completed_at": "2025-11-26T07:05:00Z",
    "agent": "support-master",
    "run_id": "19700020"
  }
}
EOF

  # Update status
  cat > status.json <<EOF
{
  "status": "completed",
  "submitted_at": "2025-11-26T07:00:00Z",
  "started_at": "2025-11-26T07:02:00Z",
  "completed_at": "2025-11-26T07:05:00Z",
  "assigned_to": "support-master"
}
EOF

  git add result.json status.json
  git commit -m "A2A result: Documentation completed"
  git push origin "$TASK_BRANCH"
  
  # Step 5: Create task for performance agent
  PERF_TASK_ID="perf-search-api-$(date +%s)"
  PERF_BRANCH="a2a-tasks/${PERF_TASK_ID}"
  
  git checkout -b "$PERF_BRANCH"
  
  cat > task.json <<EOF
{
  "jsonrpc": "2.0",
  "id": "$PERF_TASK_ID",
  "method": "agent.optimize_performance",
  "params": {
    "agent": "accelerate-master",
    "task": "optimize_search_query",
    "context": {
      "parent_issue": 500,
      "implementation_pr": 3100,
      "documentation_pr": 3101,
      "target_endpoint": "/api/v1/users/search",
      "current_implementation": "src/api/search.py",
      "performance_requirements": {
        "p95_latency": "<100ms",
        "throughput": ">1000 req/s",
        "database_queries": "<=2 per request"
      }
    },
    "requirements": {
      "profile_current_performance": true,
      "optimize_database_queries": true,
      "add_caching": true,
      "add_performance_tests": true
    }
  },
  "metadata": {
    "created_at": "2025-11-26T07:06:00Z",
    "coordinator": "support-master",
    "coordinator_run_id": "19700020",
    "parent_task": "add_documentation",
    "timeout_seconds": 900
  }
}
EOF

  cat > status.json <<EOF
{
  "status": "submitted",
  "submitted_at": "2025-11-26T07:06:00Z",
  "assigned_to": "accelerate-master"
}
EOF

  git add task.json status.json
  git commit -m "A2A task: Optimize search performance"
  git push origin "$PERF_BRANCH"
  
  # Notify performance agent
  gh issue comment 503 --body "A2A-TASK-BRANCH: ${PERF_BRANCH}
Please optimize the search API endpoint. Requirements in task.json."
fi

# Step 6: Create PR for documentation
# (support-master creates PR #3101)
```

#### Phase 4: Accelerate-Master Optimizes Performance

**accelerate-master** session starts (Run #19700030), assigned to issue #503:

```bash
# accelerate-master Copilot session (Run #19700030)

# Step 1: Read A2A task from branch
ISSUE_COMMENTS=$(gh issue view 503 --json comments -q '.comments[].body')
TASK_BRANCH=$(echo "$ISSUE_COMMENTS" | grep "A2A-TASK-BRANCH:" | cut -d' ' -f2)

git fetch origin "$TASK_BRANCH"
TASK_JSON=$(git show "origin/${TASK_BRANCH}:task.json")

# Step 2: Profile current performance
python tools/profile_api.py --endpoint /api/v1/users/search \
  --requests 1000 --output profile-before.json

# Current: p95=250ms, 400 req/s, 5 DB queries per request

# Step 3: Optimize implementation
# - Add database indexes on user.name, user.email
# - Implement Redis caching for common searches
# - Optimize SQL query (reduce 5 queries to 1)
# - Add query result pagination at DB level

# Step 4: Profile optimized performance
python tools/profile_api.py --endpoint /api/v1/users/search \
  --requests 1000 --output profile-after.json

# Optimized: p95=45ms, 1500 req/s, 1 DB query per request ✅

# Step 5: Request opinion from engineer-master on approach
OPINION_TASK_ID="opinion-caching-$(date +%s)"
OPINION_BRANCH="a2a-tasks/${OPINION_TASK_ID}"

git checkout -b "$OPINION_BRANCH"

cat > task.json <<EOF
{
  "jsonrpc": "2.0",
  "id": "$OPINION_TASK_ID",
  "method": "agent.provide_opinion",
  "params": {
    "agent": "engineer-master",
    "task": "review_caching_strategy",
    "context": {
      "optimization_pr": 3102,
      "caching_approach": "Redis with 5-minute TTL",
      "cache_key_pattern": "search:{query}:{limit}:{offset}",
      "invalidation_strategy": "Time-based (5min) + event-based (user updates)",
      "concern": "Is 5-minute TTL too aggressive for user data?"
    },
    "question": "Should we use shorter TTL (1 min) or is 5 minutes acceptable given user update frequency?"
  },
  "metadata": {
    "created_at": "2025-11-26T07:15:00Z",
    "coordinator": "accelerate-master",
    "coordinator_run_id": "19700030",
    "timeout_seconds": 300,
    "priority": "medium"
  }
}
EOF

cat > status.json <<EOF
{
  "status": "submitted",
  "submitted_at": "2025-11-26T07:15:00Z",
  "assigned_to": "engineer-master"
}
EOF

git add task.json status.json
git commit -m "A2A task: Opinion on caching TTL"
git push origin "$OPINION_BRANCH"

# Notify engineer-master (comment on original issue or new issue)
gh issue comment 501 --body "A2A-TASK-BRANCH: ${OPINION_BRANCH}
@engineer-master - Please review caching strategy for search optimization."

# Step 6: Wait for opinion (poll branch)
for i in {1..10}; do
  git fetch origin "$OPINION_BRANCH"
  if git show "origin/${OPINION_BRANCH}:result.json" &>/dev/null; then
    OPINION=$(git show "origin/${OPINION_BRANCH}:result.json")
    RECOMMENDATION=$(echo "$OPINION" | jq -r '.result.recommendation')
    
    echo "Received opinion: $RECOMMENDATION"
    # Opinion: "5 min TTL acceptable, user updates are rare, add event-based invalidation"
    break
  fi
  sleep 30
done

# Step 7: Write performance optimization result
git checkout "$TASK_BRANCH"

cat > result.json <<EOF
{
  "jsonrpc": "2.0",
  "id": "$(echo "$TASK_JSON" | jq -r '.id')",
  "result": {
    "success": true,
    "optimizations_applied": [
      "Added database indexes (user.name, user.email)",
      "Implemented Redis caching (5-min TTL + event-based invalidation)",
      "Optimized SQL query (5 queries → 1 query)",
      "Added query result pagination at DB level"
    ],
    "performance_improvement": {
      "before": {
        "p95_latency_ms": 250,
        "throughput_rps": 400,
        "db_queries_per_request": 5
      },
      "after": {
        "p95_latency_ms": 45,
        "throughput_rps": 1500,
        "db_queries_per_request": 1
      }
    },
    "all_requirements_met": true,
    "performance_pr": 3102,
    "test_coverage": "Added load tests covering 1000+ req/s scenarios"
  },
  "metadata": {
    "completed_at": "2025-11-26T07:20:00Z",
    "agent": "accelerate-master",
    "run_id": "19700030"
  }
}
EOF

cat > status.json <<EOF
{
  "status": "completed",
  "submitted_at": "2025-11-26T07:06:00Z",
  "started_at": "2025-11-26T07:10:00Z",
  "completed_at": "2025-11-26T07:20:00Z",
  "assigned_to": "accelerate-master"
}
EOF

git add result.json status.json
git commit -m "A2A result: Performance optimization completed"
git push origin "$TASK_BRANCH"

# Step 8: Create PR for performance optimizations
# (accelerate-master creates PR #3102)
```

#### Phase 5: Coordinator Aggregates Results

**a2a-coordinator** polls task branches and aggregates final results:

```bash
# a2a-coordinator session (Run #19700001 or new run)

# Step 1: Poll all task branches for completion
TASK_BRANCHES=(
  "a2a-tasks/doc-search-api-1732600000"
  "a2a-tasks/perf-search-api-1732600360"
)

ALL_COMPLETE=false
TIMEOUT=1800  # 30 minutes

START_TIME=$(date +%s)
while [ "$ALL_COMPLETE" = false ]; do
  CURRENT_TIME=$(date +%s)
  if [ $((CURRENT_TIME - START_TIME)) -gt $TIMEOUT ]; then
    echo "Timeout waiting for task completion"
    break
  fi
  
  COMPLETE_COUNT=0
  for BRANCH in "${TASK_BRANCHES[@]}"; do
    git fetch origin "$BRANCH"
    STATUS=$(git show "origin/${BRANCH}:status.json" | jq -r '.status')
    if [ "$STATUS" = "completed" ]; then
      ((COMPLETE_COUNT++))
    fi
  done
  
  if [ $COMPLETE_COUNT -eq ${#TASK_BRANCHES[@]} ]; then
    ALL_COMPLETE=true
  else
    sleep 30
  fi
done

# Step 2: Aggregate results from all branches
declare -A RESULTS

for BRANCH in "${TASK_BRANCHES[@]}"; do
  RESULT=$(git show "origin/${BRANCH}:result.json")
  AGENT=$(echo "$RESULT" | jq -r '.metadata.agent')
  RESULTS[$AGENT]=$RESULT
done

# Step 3: Create summary on parent issue
SUMMARY="## Multi-Agent Task Completion Summary

### Task: Add rate-limited user search API endpoint

All sub-tasks completed successfully! 🎉

#### 1. API Implementation (engineer-master)
- **PR**: #3100
- **Status**: ✅ Merged
- **Implementation**: \`/api/v1/users/search\` with rate limiting
- **Files**: \`src/api/search.py\`

#### 2. Documentation (support-master)
- **PR**: #3101
- **Status**: ✅ Merged
- **Created**: API docs, OpenAPI spec, rate limit docs
- **Updated**: CHANGELOG.md

#### 3. Performance Optimization (accelerate-master)
- **PR**: #3102
- **Status**: ✅ Merged
- **Performance Improvement**:
  - Latency: 250ms → 45ms (82% faster)
  - Throughput: 400 req/s → 1500 req/s (3.75x)
  - DB queries: 5 → 1 per request (80% reduction)

#### Agent Collaboration
- engineer-master → support-master: Provided API spec for documentation
- support-master → accelerate-master: Passed implementation details
- accelerate-master → engineer-master: Requested caching strategy review

**Total execution time**: 25 minutes (parallel + sequential phases)
**A2A branches cleaned up**: ✅
**All requirements met**: ✅"

gh issue comment 500 --body "$SUMMARY"
gh issue close 500 --comment "Feature complete and deployed!"

# Step 4: Cleanup A2A branches
for BRANCH in "${TASK_BRANCHES[@]}"; do
  git push origin --delete "$BRANCH"
done

# Also cleanup opinion branch
git push origin --delete "a2a-tasks/opinion-caching-1732600500"
```

### Key Takeaways from This Scenario

1. **Sequential + Parallel Execution**: 
   - API implementation (parallel with docs planning)
   - Documentation (after API details available)
   - Performance optimization (after implementation)
   - Opinion request (parallel within optimization phase)

2. **Rich Inter-Agent Communication**:
   - engineer-master shares API spec with support-master
   - support-master forwards context to accelerate-master
   - accelerate-master requests opinion from engineer-master
   - All via A2A task branches

3. **Autonomy**: Each agent works independently but coordinates through branches

4. **Transparency**: All coordination visible in branches, easy to audit

5. **Resilience**: Timeouts, status tracking, and error handling built-in

This demonstrates how **branch-based A2A enables sophisticated multi-agent workflows** that would be impossible with simple sequential tool calls!

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
