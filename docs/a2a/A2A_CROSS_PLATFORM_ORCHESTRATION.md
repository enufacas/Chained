# A2A Cross-Platform Orchestration - Gemini ↔ Copilot

## Executive Summary

This document describes how to orchestrate **mixed-platform agent teams** where Gemini-based agents and Copilot-based agents collaborate on the same task, communicating via platform-agnostic message buses.

**Key Innovation**: Use **GitHub Issues** or **Git branches** as neutral message buses that work across both Gemini workflow_call/API invocations AND Copilot GraphQL assignments.

## Why Cross-Platform Orchestration?

**Leverage Platform Strengths**:
- **Gemini**: Analysis, planning, research, documentation, reviews, orchestration
- **Copilot**: Code generation, refactoring, implementation, IDE-aware changes

**Example Scenarios**:
- Gemini plans architecture → Copilot implements code → Gemini reviews security
- Gemini analyzes bug → Copilot fixes code → Gemini validates fix
- Gemini documents API → Copilot generates client code → Gemini tests integration

## Communication Mechanisms

### Option 1: GitHub Issues as Message Bus (Recommended)

**Advantages**:
- ✅ Platform-agnostic (both Gemini and Copilot can read/write)
- ✅ Built-in persistence and audit trail
- ✅ Native GitHub UI visibility
- ✅ Existing infrastructure (gemini-dispatch, assign-copilot-to-issue.sh)
- ✅ Supports concurrent workflows
- ✅ Simple polling mechanism

**How It Works**:

```
Coordinator Issue #100: "Implement search API with security review"
         ↓
   A2A Coordinator (Gemini or workflow)
         ↓
    Task Decomposition
         ↓
┌────────┴────────┬────────────────┐
│                 │                │
Sub-Issue #101    Sub-Issue #102   Sub-Issue #103
"Design API"      "Implement API"  "Security Review"
@gemini-design    @engineer-master @gemini-security
         ↓                ↓                ↓
   Gemini Workflow   Copilot Session  Gemini Workflow
         ↓                ↓                ↓
   Posts comment    Creates PR       Posts comment
   with results     Posts comment    with findings
         ↓                ↓                ↓
         └────────┬────────┴────────┘
                  ↓
        Coordinator polls for completion
                  ↓
        Aggregates results → Post to #100
```

**Message Format in Issue Comments**:

```markdown
## A2A Task Result

**Agent**: @gemini-design  
**Task ID**: task-abc123-def456  
**Status**: completed  
**Result**:

```json
{
  "api_design": {
    "endpoint": "/api/v1/search",
    "method": "GET",
    "parameters": {...},
    "rate_limit": "100/hour"
  },
  "next_agent": "@engineer-master",
  "context_for_next": {
    "design_doc": "issue-101.md",
    "requirements": [...]
  }
}
```

**Ready for**: @engineer-master (Issue #102)
```

### Option 2: Git Branches as Message Bus (Alternative)

**Advantages**:
- ✅ Cleaner (no issue clutter)
- ✅ Supports file artifacts
- ✅ Atomic operations
- ✅ Easy cleanup

**How It Works**:

```
Coordinator creates branches:
  a2a-tasks/design-abc123     → Gemini reads/writes
  a2a-tasks/implement-def456  → Copilot reads/writes  
  a2a-tasks/security-ghi789   → Gemini reads/writes

Each agent:
1. Fetches assigned branch
2. Reads task.json
3. Executes work
4. Writes result.json + artifacts
5. Pushes to branch
6. Updates status

Coordinator polls branches for completion
```

**Cross-Platform Branch Message**:

```bash
# Branch: a2a-tasks/implement-api-def456
task.json:
{
  "jsonrpc": "2.0",
  "id": "task-def456",
  "method": "agent.implement",
  "params": {
    "agent_type": "copilot",
    "agent_name": "@engineer-master",
    "task": "Implement search API",
    "input_from": "a2a-tasks/design-abc123/result.json",
    "context": {...}
  }
}

result.json (written by Copilot):
{
  "jsonrpc": "2.0",
  "id": "task-def456",
  "result": {
    "pr_number": 3070,
    "files_changed": ["src/search.py"],
    "status": "completed"
  },
  "next_task_branch": "a2a-tasks/security-ghi789"
}
```

## Architecture: Unified Coordinator

### Coordinator Agent (Platform-Agnostic)

The coordinator can be **either** Gemini-based OR a pure workflow, but handles both platforms:

```yaml
# .github/workflows/a2a-unified-coordinator.yml
name: A2A Unified Coordinator

on:
  issues:
    types: [labeled]

jobs:
  coordinate:
    if: contains(github.event.issue.labels.*.name, 'a2a-orchestrate')
    runs-on: ubuntu-latest
    steps:
      - name: Analyze task
        id: analyze
        run: |
          # Use Gemini API for task decomposition
          gemini analyze-task \
            --issue "${{ github.event.issue.number }}" \
            --output plan.json
      
      - name: Create sub-tasks
        id: subtasks
        run: |
          # Read plan.json and create sub-issues
          python3 tools/create-subtasks.py plan.json
      
      - name: Assign agents by platform
        run: |
          # For Gemini agents: Add @gemini-{agent} command
          # For Copilot agents: Use GraphQL assignment
          
          for task in $(jq -r '.tasks[] | @base64' plan.json); do
            agent_type=$(echo "$task" | base64 -d | jq -r '.agent_type')
            agent_name=$(echo "$task" | base64 -d | jq -r '.agent_name')
            issue_num=$(echo "$task" | base64 -d | jq -r '.issue_number')
            
            if [ "$agent_type" = "gemini" ]; then
              # Post @gemini command to issue
              gh issue comment "$issue_num" \
                --body "@gemini-$agent_name /execute"
            elif [ "$agent_type" = "copilot" ]; then
              # Assign via GraphQL
              bash tools/assign-copilot-to-issue.sh "$issue_num" "$agent_name"
            fi
          done
      
      - name: Monitor and aggregate
        run: |
          # Poll sub-issues for completion
          python3 tools/poll-and-aggregate.py \
            --parent-issue "${{ github.event.issue.number }}" \
            --timeout 3600
```

## Platform-Specific Integration

### Gemini Agent Integration

**Existing**: gemini-dispatch.yml already handles @gemini-cli commands

**A2A Enhancement**:
```yaml
# Add to gemini agents: Check for A2A context
- name: Check A2A Context
  id: a2a
  run: |
    # Look for A2A task ID in issue body
    if grep -q "A2A-TASK-ID:" issue.md; then
      task_id=$(grep "A2A-TASK-ID:" issue.md | cut -d: -f2)
      
      # Fetch input from previous agent
      if [ -n "$PREV_ISSUE" ]; then
        gh issue view "$PREV_ISSUE" --json comments \
          | jq -r '.comments[-1].body' > prev_result.json
      fi
    fi

- name: Execute with A2A awareness
  run: |
    gemini execute \
      --task "$TASK" \
      --context prev_result.json \
      --output result.json

- name: Post A2A result
  run: |
    gh issue comment "$ISSUE_NUMBER" --body "$(cat <<EOF
## A2A Task Result
**Agent**: @gemini-$AGENT_NAME
**Task ID**: $TASK_ID
**Status**: completed
**Result**: $(cat result.json)
**Next Agent**: @$NEXT_AGENT
EOF
)"
```

### Copilot Agent Integration

**Existing**: assign-copilot-to-issue.sh triggers Copilot sessions

**A2A Enhancement** (via agent .md instructions):

```markdown
# .github/agents/engineer-master.md

## A2A Communication Protocol

When assigned to an issue with A2A orchestration:

1. **Detect A2A Context**:
   ```bash
   # Check issue body for A2A markers
   if grep -q "A2A-TASK-ID:" issue_body.md; then
     task_id=$(grep "A2A-TASK-ID:" issue_body.md | cut -d: -f2)
     prev_agent=$(grep "PREV-AGENT:" issue_body.md | cut -d: -f2)
   fi
   ```

2. **Fetch Previous Agent Output**:
   ```bash
   # If PREV-ISSUE specified, read that issue's last comment
   if [ -n "$PREV_ISSUE" ]; then
     gh issue view "$PREV_ISSUE" --json comments \
       | jq -r '.comments[-1].body | fromjson' > input.json
   fi
   ```

3. **Execute Work** using input context

4. **Post A2A Result**:
   ```bash
   gh issue comment "$ISSUE_NUMBER" --body "$(cat <<EOF
## A2A Task Result
**Agent**: @engineer-master
**Task ID**: $TASK_ID
**Status**: completed
**PR**: #$PR_NUMBER
**Result**: 
- Implemented API endpoint
- Added rate limiting
- Created tests
**Next Agent**: @gemini-security (Issue #$NEXT_ISSUE)
EOF
)"
   ```

5. **Reference PR** in comment for next agent context
```

## Example: Mixed-Platform Workflow

### Scenario: "Implement Secure Search API"

**Agents**:
1. @gemini-architect (Gemini) - Architecture design
2. @engineer-master (Copilot) - Code implementation
3. @gemini-security (Gemini) - Security review
4. @support-master (Copilot) - Documentation
5. @gemini-integration (Gemini) - End-to-end testing

**Execution Flow**:

```
Issue #100: "Implement secure search API"
  ↓
Coordinator (Gemini or workflow) analyzes
  ↓
Creates 5 sub-issues:

Issue #101: @gemini-architect - Design architecture
  ↓ (Gemini workflow posts design doc)
Issue #102: @engineer-master - Implement API  
  ↓ (Copilot creates PR #3070)
Issue #103: @gemini-security - Security audit
  ↓ (Gemini posts security findings)
Issue #104: @engineer-master - Fix security issues
  ↓ (Copilot updates PR #3070)
Issue #105: @support-master - Generate documentation
  ↓ (Copilot creates docs PR #3071)
Issue #106: @gemini-integration - Run E2E tests
  ↓ (Gemini runs tests, posts results)

Coordinator aggregates all results → Posts summary to #100
```

**Timeline**: ~30 minutes total
- Issues #101, #103, #106: Gemini (parallel, fast)
- Issues #102, #104, #105: Copilot (sequential, code-focused)

## Implementation Phases

### Phase 3A: Issue-Based Cross-Platform (Week 1)

**Goal**: Gemini → Copilot → Gemini pipeline

**Deliverables**:
1. a2a-unified-coordinator.yml workflow
2. Enhanced gemini-dispatch for A2A context
3. A2A protocol instructions in copilot agent .md files
4. Polling and aggregation scripts
5. End-to-end test: Gemini designs → Copilot implements → Gemini reviews

**Success Criteria**:
- 3-agent pipeline completes successfully
- Result passed correctly between platforms
- Coordinator aggregates all outputs

### Phase 3B: Branch-Based Cross-Platform (Week 2)

**Goal**: Add branch message bus as alternative

**Deliverables**:
1. Branch creation and management scripts
2. Enhanced agents to check branches for tasks
3. Parallel execution support
4. Branch cleanup automation

**Success Criteria**:
- Both Issue and Branch methods work
- 5+ agents can collaborate (Gemini + Copilot mix)
- Parallel execution works correctly

### Phase 3C: Production Workflows (Week 3)

**Goal**: Deploy 10+ specialized mixed-platform workflows

**Deliverables**:
1. 10+ specialized agent definitions
2. Sophisticated task decomposition
3. Error handling and retry logic
4. Performance monitoring
5. Complete documentation

**Success Criteria**:
- Complex multi-platform workflows complete end-to-end
- Error recovery works
- Performance meets targets (&lt;30 min for typical tasks)

## Decision Matrix: When to Use Each Platform

| Task Type | Recommended Platform | Reason |
|-----------|---------------------|---------|
| Architecture design | Gemini | Broad analysis, no code generation needed |
| API implementation | Copilot | Deep code understanding, IDE patterns |
| Security review | Gemini | Pattern analysis, threat modeling |
| Code refactoring | Copilot | Maintains code structure and style |
| Documentation | Either | Both handle well (Copilot for code docs, Gemini for conceptual) |
| Testing | Gemini | Can analyze coverage and generate test plans |
| Bug investigation | Gemini | Broad codebase analysis |
| Bug fixing | Copilot | Precise code changes |
| Performance analysis | Gemini | Profiling and bottleneck identification |
| Performance optimization | Copilot | Code-level optimizations |

## Comparison: Issue Bus vs Branch Bus

| Aspect | GitHub Issues | Git Branches |
|--------|--------------|--------------|
| **Visibility** | High (native UI) | Low (git only) |
| **Audit Trail** | Excellent | Good |
| **Cleanup** | Manual (or auto-close) | Easy (delete branch) |
| **Artifacts** | Text only | Full files |
| **Concurrency** | Excellent | Good |
| **Polling** | Simple (GitHub API) | Simple (git fetch) |
| **Setup** | Minimal | Moderate |
| **Best For** | Most workflows | File-heavy workflows |

**Recommendation**: Start with **GitHub Issues** for simplicity and visibility. Add **Branch Bus** later for workflows requiring artifacts.

## Testing Strategy

### Unit Tests
- Test coordinator task decomposition
- Test agent assignment (both platforms)
- Test result parsing and aggregation

### Integration Tests
- Gemini-only workflow
- Copilot-only workflow
- Mixed Gemini → Copilot workflow
- Mixed Copilot → Gemini workflow
- 5-agent complex workflow (3 Gemini + 2 Copilot)

### Performance Tests
- Measure latency for each communication method
- Test concurrent agent execution
- Measure end-to-end workflow time

### Failure Tests
- Agent timeout handling
- Invalid result format handling
- Platform-specific errors (API limits, runner failures)
- Coordinator crash recovery

## Known Limitations

**Gemini Platform**:
- API rate limits (60 requests/minute for free tier)
- No direct IDE integration
- Requires API key management

**Copilot Platform**:
- GraphQL assignment may have delays
- Custom agent availability (Copilot for Business required)
- No programmatic CLI for orchestration

**Cross-Platform**:
- Message passing adds latency (polling delay)
- Issue comment size limits (65KB)
- Git branch naming conventions must be consistent
- Increased complexity in debugging

## Success Metrics

**Phase 3A** (Week 1):
- ✅ 3-agent cross-platform workflow completes
- ✅ End-to-end time &lt; 20 minutes
- ✅ All results aggregated correctly

**Phase 3B** (Week 2):
- ✅ 5-agent workflow with parallel execution
- ✅ Both Issue and Branch buses work
- ✅ Error recovery functions

**Phase 3C** (Week 3):
- ✅ 10+ specialized workflows deployed
- ✅ Production use on real issues
- ✅ 90% success rate
- ✅ Average completion time &lt; 30 minutes

## Next Steps

1. ✅ **Design complete** (this document)
2. 🔄 Implement a2a-unified-coordinator.yml
3. 🔄 Enhance gemini-dispatch for A2A
4. 🔄 Add A2A instructions to copilot agents
5. 🔄 Build polling and aggregation tools
6. 🔄 Test first cross-platform workflow
7. 🔄 Iterate and expand

## Related Documentation

- **A2A_GEMINI_IMPLEMENTATION.md** - Gemini-only orchestration
- **A2A_VIABLE_PATH_FORWARD.md** - Copilot GraphQL assignment
- **A2A_BRANCH_BASED_COORDINATION.md** - Branch message bus details
- **A2A_PHASE_3_DESIGN.md** - Original Copilot-focused design
- **A2A_STATUS.md** - Overall project status

---

**Cross-platform A2A orchestration enables best-of-both-worlds: Gemini's analytical capabilities + Copilot's code generation expertise!** 🚀
