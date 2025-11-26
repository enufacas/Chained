# A2A Gemini Implementation - Design Document

**Status**: Planning  
**Platform**: Gemini AI (Google AI Studio / Vertex AI)  
**Approach**: CLI-based orchestration via workflow_call  
**Compatibility**: Preserves Copilot orchestration path

## Executive Summary

This document outlines the implementation of Agent-to-Agent (A2A) orchestration using **Gemini AI** as the execution engine. Unlike Copilot (which has headless authentication limitations), Gemini provides pure CLI/API access that enables programmatic multi-agent workflows.

**Key Advantages of Gemini for A2A**:
- ✅ **Pure API/CLI access** - No device flow requirement
- ✅ **Programmatic invocation** - Call via workflow_call or direct API
- ✅ **MCP Server integration** - Native GitHub operations via tools
- ✅ **Flexible authentication** - API key via secrets
- ✅ **Parallel sessions** - Multiple workflow runs possible
- ✅ **Proven in production** - Already deployed (gemini-dispatch, gemini-invoke, gemini-review, gemini-triage, gemini-fix)

**Design Philosophy**: Build Gemini A2A implementation as **parallel capability** to Copilot approach, not replacement. Both paths remain viable for different use cases.

## Current Gemini Infrastructure

### Existing Workflows
1. **gemini-dispatch.yml** - Central router for @gemini-cli commands
2. **gemini-invoke.yml** - General purpose assistant
3. **gemini-review.yml** - PR code review
4. **gemini-triage.yml** - Issue classification
5. **gemini-fix.yml** - Code fixes and improvements

### Authentication Methods
- **Google AI Studio**: GEMINI_API_KEY secret (simple, recommended)
- **Vertex AI**: GOOGLE_API_KEY secret + GOOGLE_GENAI_USE_VERTEXAI variable

### Architecture Pattern
```
GitHub Event → gemini-dispatch → Workflow Selection → Gemini CLI Execution
                     ↓
          Issue/PR Context Loaded
                     ↓
          MCP Server (GitHub tools)
                     ↓
          Gemini Model Processes
                     ↓
          Results Posted to Issue/PR
```

## A2A Orchestration Design for Gemini

### Three-Tier Orchestration Model

#### Tier 0: Direct CLI Invocation (Existing)
**Current State**: Single Gemini session handles complete task
- User posts @gemini-cli command
- Dispatch routes to appropriate workflow
- Single Gemini session executes
- Results posted back

#### Tier 1: Sequential Sub-Agent Delegation (NEW)
**Orchestrator Gemini session delegates to specialized Gemini sessions**

```
GitHub Issue #100: "Implement secure REST API"
         ↓
gemini-a2a-coordinator.yml (NEW)
         ↓
   Task Analysis
         ↓
┌────────┴────────┐
│  Subtask Plan   │
│ 1. Design API   │
│ 2. Security     │
│ 3. Implement    │
│ 4. Test         │
└────────┬────────┘
         ↓
   Sequential Execution:
   
1. workflow_call: gemini-design.yml → Creates sub-issue #101
   ↓ result
2. workflow_call: gemini-security.yml → Creates sub-issue #102
   ↓ result
3. workflow_call: gemini-implement.yml → Creates sub-issue #103
   ↓ result
4. workflow_call: gemini-test.yml → Creates sub-issue #104
   ↓ results aggregated
   
Post summary to issue #100
```

#### Tier 2: Parallel Multi-Agent Delegation (NEW)
**Multiple independent Gemini sessions via sub-issues**

```
GitHub Issue #100: "Implement secure REST API"
         ↓
gemini-a2a-coordinator.yml (NEW)
         ↓
   Task Analysis
         ↓
   Parallel Subtask Creation:
   
├─ Issue #101: Design → @gemini-design /plan
│  ↓ (gemini-dispatch routes to design workflow)
│  ↓ (Gemini session executes, creates PR)
│
├─ Issue #102: Security → @gemini-security /audit
│  ↓ (gemini-dispatch routes to security workflow)
│  ↓ (Gemini session executes, creates PR)
│
├─ Issue #103: Documentation → @gemini-docs /generate
│  ↓ (gemini-dispatch routes to docs workflow)
│  ↓ (Gemini session executes, creates PR)
│
└─ Issue #104: Testing → @gemini-test /coverage
   ↓ (gemini-dispatch routes to test workflow)
   ↓ (Gemini session executes, creates PR)
   
Coordinator polls for completion, aggregates results
```

### Architecture Comparison

| Aspect | Gemini Tier 1 | Gemini Tier 2 | Copilot (GraphQL) |
|--------|---------------|---------------|-------------------|
| **Invocation** | workflow_call | Sub-issues + @gemini-cli | Sub-issues + GraphQL assign |
| **Execution** | Sequential | Parallel | Parallel |
| **Isolation** | Same workflow run | Separate runs | Separate runs |
| **Communication** | Workflow outputs | Issue comments | Branch files |
| **Speed** | Fast (seconds) | Medium (minutes) | Medium (minutes) |
| **Complexity** | Low | Medium | High |
| **Best For** | Dependent subtasks | Independent subtasks | Copilot-specific agents |

## Implementation Components

### 1. A2A Coordinator Workflow (NEW)

**File**: `.github/workflows/gemini-a2a-coordinator.yml`

```yaml
name: '🎯 Gemini A2A Coordinator'

on:
  workflow_call:
    inputs:
      parent_issue_number:
        type: number
        required: true
      task_description:
        type: string
        required: true
      tier_preference:
        type: string
        default: 'auto'
        description: 'auto, tier1, tier2'

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
      pull-requests: write
    outputs:
      subtasks: ${{ steps.decompose.outputs.subtasks }}
      tier: ${{ steps.decompose.outputs.tier }}
      strategy: ${{ steps.decompose.outputs.strategy }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Analyze and Decompose Task
        id: decompose
        uses: google-github-actions/run-gemini-cli@v0
        with:
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          google_api_key: ${{ secrets.GOOGLE_API_KEY }}
          use_vertex_ai: ${{ vars.GOOGLE_GENAI_USE_VERTEXAI || false }}
          prompt: |
            /a2a-analyze
            
            Task: ${{ inputs.task_description }}
            Tier Preference: ${{ inputs.tier_preference }}
            
            Decompose this task into subtasks suitable for A2A orchestration.
            Output JSON format:
            {
              "subtasks": [
                {
                  "id": "1",
                  "title": "Design API",
                  "description": "...",
                  "agent_type": "design",
                  "dependencies": []
                }
              ],
              "tier": "tier1|tier2",
              "strategy": "sequential|parallel"
            }

  orchestrate_tier1:
    needs: analyze
    if: ${{ needs.analyze.outputs.tier == 'tier1' }}
    runs-on: ubuntu-latest
    steps:
      - name: Execute Sequential Subtasks
        run: |
          # For each subtask, invoke specialized workflow
          # Collect results
          # Post aggregated summary
          
  orchestrate_tier2:
    needs: analyze
    if: ${{ needs.analyze.outputs.tier == 'tier2' }}
    runs-on: ubuntu-latest
    steps:
      - name: Create Subtask Issues
        run: |
          # Create sub-issues with @gemini-cli commands
          # Wait for completion (poll)
          # Aggregate results
```

### 2. Specialized Gemini Agent Workflows

Create specialized workflows that can be called programmatically:

- **gemini-design.yml** - API design and planning
- **gemini-security.yml** - Security audit and recommendations  
- **gemini-implement.yml** - Code implementation
- **gemini-test.yml** - Test generation and execution
- **gemini-docs.yml** - Documentation generation
- **gemini-optimize.yml** - Performance optimization

Each follows the pattern:
```yaml
name: 'Gemini Agent: [Specialization]'
on:
  workflow_call:
    inputs:
      subtask_context:
        type: string
        required: true
      parent_issue:
        type: number
        required: true
```

### 3. A2A Communication Protocols

#### Protocol 1: Workflow Call (Tier 1)
```yaml
- name: Call specialized agent
  uses: ./.github/workflows/gemini-design.yml
  with:
    subtask_context: ${{ steps.decompose.outputs.subtask_1 }}
    parent_issue: ${{ inputs.parent_issue_number }}
```

#### Protocol 2: Issue-Based (Tier 2)
```bash
# Coordinator creates sub-issue
gh issue create \
  --title "Design API (subtask 1 of 4)" \
  --body "@gemini-design

## Context
Parent Issue: #$PARENT_ISSUE

## Task
Design REST API endpoints for user search functionality.

## Requirements
- Rate limiting support
- RESTful conventions
- OpenAPI spec

---
A2A-PARENT: #$PARENT_ISSUE
A2A-SUBTASK-ID: design-001
"

# gemini-dispatch automatically routes @gemini-design to design workflow
# Design workflow executes, posts results
# Coordinator polls and aggregates
```

#### Protocol 3: Branch-Based (Future)
Preserve branch-based communication path for cross-agent data sharing:
```bash
# Agent A creates task branch
git checkout -b "a2a-tasks/optimize-api-${TASK_ID}"
echo '{"method": "optimize_performance", "params": {...}}' > task.json
git push origin "a2a-tasks/optimize-api-${TASK_ID}"

# Trigger Agent B via workflow_dispatch or issue
# Agent B reads branch, executes, writes result.json
# Agent A polls branch for completion
```

## Implementation Phases

### Phase 3A: Tier 1 Orchestration (Week 1)

**Deliverables**:
1. ✅ gemini-a2a-coordinator.yml workflow
2. ✅ Task analysis and decomposition via Gemini
3. ✅ Sequential workflow_call orchestration
4. ✅ 3 specialized agent workflows (design, implement, test)
5. ✅ Result aggregation and reporting
6. ✅ Testing with simple 2-3 subtask scenarios

**Success Criteria**:
- Coordinator can decompose task into subtasks
- Sequential execution via workflow_call works
- Results aggregated correctly
- End-to-end test completes successfully

### Phase 3B: Tier 2 Orchestration (Week 2)

**Deliverables**:
1. ✅ Parallel sub-issue creation
2. ✅ @gemini-cli command injection in sub-issues
3. ✅ gemini-dispatch routing to specialized workflows
4. ✅ Polling and status tracking
5. ✅ Result aggregation from multiple issues
6. ✅ Testing with 3-5 parallel subtasks

**Success Criteria**:
- Parallel subtask execution works
- All subtasks complete independently
- Results correctly aggregated
- No race conditions or conflicts

### Phase 3C: Agent Specializations (Week 3)

**Deliverables**:
1. ✅ 6-10 specialized agent workflows
2. ✅ Agent capability documentation
3. ✅ Agent selection logic in coordinator
4. ✅ Production-ready error handling
5. ✅ Performance benchmarking
6. ✅ Documentation and examples

**Success Criteria**:
- 10+ specialized agents available
- Coordinator selects appropriate agents
- Error handling robust
- Performance acceptable (&lt;5 min for typical task)

## Key Design Decisions

### 1. Preserve Copilot Path
**Decision**: Gemini A2A is **additive**, not replacement
- Copilot GraphQL assignment path remains valid
- Branch-based communication available to both
- Shared A2A protocol definitions
- Documentation covers both approaches

**Rationale**: Different platforms have different strengths. Gemini excels at programmatic orchestration; Copilot excels at code generation. Keep both options.

### 2. Use Existing Dispatch Infrastructure  
**Decision**: Extend gemini-dispatch.yml, don't replace
- Add @gemini-a2a command routing
- Reuse authentication and MCP setup
- Minimal changes to existing workflows

**Rationale**: Proven, stable infrastructure. Build on what works.

### 3. Issue-Based Communication for Tier 2
**Decision**: Use GitHub Issues as message bus for parallel execution
- Natural fit with existing @gemini-cli pattern
- Visible audit trail
- Easy polling and status tracking
- Automatic routing via gemini-dispatch

**Rationale**: Simpler than branch-based for Gemini (though branch-based remains available).

### 4. Workflow Call for Tier 1
**Decision**: Use workflow_call for sequential orchestration
- Fast (no extra workflow dispatch overhead)
- Clean dependency chain
- Built-in GitHub Actions features
- Easy result passing via outputs

**Rationale**: Most efficient for dependent subtasks.

## Testing Strategy

### Unit Tests
1. Task decomposition logic
2. Agent selection algorithm
3. Subtask dependency resolution
4. Result aggregation

### Integration Tests
1. Tier 1: Sequential 3-subtask workflow
2. Tier 2: Parallel 4-subtask workflow
3. Mixed: Sequential + parallel phases
4. Error scenarios: Agent failure, timeout

### End-to-End Tests
1. **Simple**: "Add logging to API endpoint"
   - Design → Implement → Test (Tier 1)
2. **Medium**: "Implement rate-limited search API"
   - Design + Security (parallel) → Implement → Test + Docs (parallel) (Tier 2)
3. **Complex**: "Refactor authentication system"
   - Analysis → Design → Implementation (3 modules parallel) → Testing (3 suites parallel) → Documentation (Tier 1 + Tier 2)

## Monitoring and Observability

### Metrics to Track
- Orchestration latency (time to first subtask)
- Subtask execution time (per agent type)
- Success rate (completion without errors)
- Retry count (failed subtask retries)
- Parallelism efficiency (Tier 2 speedup)

### Dashboards
- Real-time workflow status
- Agent utilization
- Error rates by agent type
- Performance trends

### Alerts
- Orchestration failure rate &gt; 10%
- Average subtask time &gt; 10 minutes
- Agent availability &lt; 95%

## Migration and Rollout

### Phase 1: Internal Testing (Week 1-2)
- Test with synthetic tasks
- Iterate on coordinator logic
- Refine agent specializations

### Phase 2: Limited Production (Week 3-4)  
- Enable for select issue labels
- Manual trigger only (@gemini-a2a)
- Monitor closely

### Phase 3: Gradual Expansion (Week 5-8)
- Auto-trigger for specific scenarios
- Increase agent count
- Performance optimization

### Phase 4: Full Production (Week 9+)
- Auto-trigger widely
- Complete agent suite
- Production monitoring

## Comparison: Gemini vs Copilot A2A

| Aspect | Gemini A2A | Copilot A2A |
|--------|------------|-------------|
| **Authentication** | API key (simple) | Classic PAT + GraphQL |
| **Invocation** | workflow_call or @gemini-cli | GraphQL assignment |
| **Orchestration** | Coordinator workflow | Coordinator workflow |
| **Communication** | Issues or workflow_call | Branches or issues |
| **Parallelism** | Native (separate runs) | Native (separate runs) |
| **Agent Tools** | MCP servers | MCP tools |
| **Best For** | Any AI task | Code generation |
| **Status** | Ready to implement | Proven, working |
| **Complexity** | Medium | Medium-High |

**Both approaches are viable and complementary.**

## Open Questions

1. **Agent Discovery**: Should we create agent registry for Gemini agents similar to custom Copilot agents?
2. **Result Format**: Standardize output format across agent types?
3. **Timeout Handling**: What's appropriate timeout for different subtask types?
4. **Cost Management**: How to track and limit Gemini API usage per orchestration?
5. **Human-in-Loop**: When should coordinator pause for human approval?

## References

- **Existing Docs**: docs/a2a/A2A_PHASE_3_DESIGN.md (Copilot approach)
- **Workflows**: .github/workflows/gemini-*.yml (existing Gemini workflows)
- **A2A Protocol**: docs/a2a/A2A_INTEGRATION_DESIGN.md
- **Branch Communication**: docs/a2a/A2A_BRANCH_BASED_COORDINATION.md

## Next Steps

1. ✅ **This document** approved and merged
2. 🔄 Create gemini-a2a-coordinator.yml workflow skeleton
3. 🔄 Implement task decomposition via Gemini
4. 🔄 Build Tier 1 sequential orchestration
5. 🔄 Create 3 specialized agent workflows
6. 🔄 End-to-end test of simple scenario
7. 🔄 Iterate based on test results

---

**Status**: 📋 Planning Complete - Ready for Implementation  
**Owner**: @copilot  
**Last Updated**: 2025-11-26
