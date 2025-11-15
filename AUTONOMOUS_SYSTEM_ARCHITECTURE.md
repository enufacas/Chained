# 🏗️ Chained Autonomous System Architecture

> **The complete blueprint for Chained's self-evolving AI ecosystem**

This document serves as the definitive architectural guide for the Chained autonomous AI system, detailing how all components work together to create a truly self-improving, closed-loop software development ecosystem.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Autonomous Loop](#autonomous-loop)
4. [Critical Constraints](#critical-constraints)
5. [Workflow Orchestration](#workflow-orchestration)
6. [Agent System](#agent-system)
7. [World Model](#world-model)
8. [Integration Points](#integration-points)

---

## 🌟 System Overview

Chained operates as a **perpetual motion machine for software development**, where:

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL WORLD                            │
│  (TLDR, Hacker News, GitHub Trending, Real-world Tech)      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              LEARNING INGESTION SYSTEM                       │
│  • Fetch tech news and trends                               │
│  • Parse and normalize content                              │
│  • Filter and quality check                                 │
│  • Store in learnings database                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           COMBINED LEARNING ANALYSIS                         │
│  • Aggregate from multiple sources                          │
│  • Thematic analysis and trend detection                    │
│  • Generate insights and summaries                          │
│  • Create learning issues and PRs                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              WORLD MODEL UPDATE                              │
│  • Sync agents from registry                                │
│  • Update world_state.json                                  │
│  • Sync learnings to ideas                                  │
│  • Update knowledge.json                                    │
│  • Geographic agent navigation                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          AGENT ASSIGNMENT & MISSION CREATION                 │
│  • Match agents to learnings (10-agent limit)               │
│  • Create mission issues                                    │
│  • Track agent investments                                  │
│  • Update collaboration records                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             AGENT WORK EXECUTION                             │
│  • Agents implement solutions                               │
│  • Create PRs with changes                                  │
│  • Run tests and validations                                │
│  • Auto-merge approved work                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           SELF-REINFORCEMENT LOOP                            │
│  • Collect resolved issues                                  │
│  • Learn from PR failures                                   │
│  • Extract insights from discussions                        │
│  • Feed back to learning system                             │
└────────────────────┴────────────────────────────────────────┘
                     │
                     └──────── (Loop Restarts) ─────────┐
                                                          │
                     ┌────────────────────────────────────┘
                     ▼
            🔄 THE CYCLE NEVER STOPS
```

### Key Characteristics

- **✅ Fully Autonomous**: No human intervention required
- **🔄 Self-Improving**: Learns from its own actions
- **🌍 World-Aware**: Tracks agents geographically
- **🤖 Multi-Agent**: Specialized agents compete and collaborate
- **📊 Metrics-Driven**: Everything is measured and optimized
- **🔐 Constraint-Enforced**: Critical rules are validated automatically

---

## 🧩 Core Components

### 1. Learning System

**Purpose**: Ingest knowledge from the external world

**Components**:
- `learn-from-tldr.yml` - TLDR Tech newsletter ingestion
- `learn-from-hackernews.yml` - Hacker News story collection
- `combined-learning.yml` - Unified learning from multiple sources
- `intelligent-content-parser.py` - Content filtering and quality checking
- `thematic-analyzer.py` - Trend analysis and categorization

**Outputs**:
- `learnings/*.json` - Normalized learning data
- `learnings/analysis_*.json` - Thematic analysis results
- Learning issues documenting insights
- PRs with new learnings added to main

**Triggers**:
- Scheduled (multiple times daily)
- Manual via `workflow_dispatch`

### 2. World Model

**Purpose**: Maintain a unified state of agents, ideas, and knowledge

**Components**:
- `world-update.yml` - Periodic world state synchronization
- `world_state_manager.py` - World state operations
- `sync_agents_to_world.py` - Agent registry → world sync
- `sync_learnings_to_ideas.py` - Learning → idea conversion
- `agent_navigator.py` - Geographic navigation logic
- `knowledge_manager.py` - Knowledge graph operations

**State Files**:
- `world/world_state.json` - Current world snapshot (tick, agents, ideas)
- `world/knowledge.json` - Knowledge graph and relationships
- `docs/world/` - Published world data for GitHub Pages

**Triggers**:
- Scheduled (every 2 hours)
- After learning system updates
- Manual via `workflow_dispatch`

### 3. Agent System

**Purpose**: Specialized AI agents that compete, collaborate, and evolve

**Components**:
- `.github/agents/*.md` - Agent definitions (40+ agents)
- `.github/agent-system/registry.json` - Agent registry
- `agent_learning_matcher.py` - Match agents to learnings
- `agent_investment_tracker.py` - Track agent expertise growth
- `agent_collaboration_manager.py` - Manage inter-agent collaboration
- Performance metrics and scoring system

**Agent Lifecycle**:
1. **Spawning**: Based on learning trends or manual creation
2. **Assignment**: Matched to appropriate tasks
3. **Execution**: Implement solutions via Copilot
4. **Evaluation**: Performance measured (code quality, resolution, review)
5. **Evolution**: High performers thrive, low performers eliminated

**Key Agents**:
- `support-master` - Documentation and knowledge sharing
- `engineer-master` - API engineering and systematic development
- `troubleshoot-expert` - CI/CD and workflow debugging (protected)
- `secure-specialist` - Security hardening and vulnerability fixes
- `create-guru` - Infrastructure and feature creation
- And 35+ more specialized agents

### 4. Workflow Orchestration

**Purpose**: Coordinate autonomous operations through GitHub Actions

**Key Workflows**:
- Learning ingestion (3-4x daily)
- Combined learning analysis (2x daily)
- World model updates (every 2 hours)
- Agent assignments (daily)
- PR failure learning (weekly)
- Issue collection (on PR close)
- Performance metrics (continuous)

**Orchestration Method**: `workflow_run` triggers to chain workflows

### 5. Self-Reinforcement System

**Purpose**: Learn from system's own actions to improve over time

**Components**:
- `pr-failure-learning.yml` - Extract patterns from failed PRs
- `collect-resolved-issues.yml` - Build solution history
- `semantic_similarity_engine.py` - Match similar issues
- `self_documenting_ai.py` - Extract insights from discussions
- Agent performance tracking and metrics

**Feedback Loop**:
```
Execution → Observation → Analysis → Learning → Better Execution
```

---

## 🔄 Autonomous Loop

### The 5-Stage Pipeline

```
STAGE 1: LEARNING INGESTION
  └─ Triggers: Schedule (multiple times daily)
  └─ Outputs: learnings/*.json, learning PRs
  └─ Next: Combined Learning (workflow_run)

STAGE 2: COMBINED LEARNING GENERATION  
  └─ Triggers: After learning ingestion (workflow_run)
  └─ Outputs: combined_analysis_*.json, issues, PRs
  └─ Next: World Model Update (workflow_run)

STAGE 3: WORLD MODEL UPDATE
  └─ Triggers: After combined learning (workflow_run) + Schedule (2 hours)
  └─ Outputs: world_state.json, knowledge.json, world PRs
  └─ Next: Agent Assignment (workflow_run)

STAGE 4: AGENT ASSIGNMENT & MISSION CREATION
  └─ Triggers: After world update (workflow_run) + Schedule (daily)
  └─ Outputs: Mission issues, agent_investments.json updates
  └─ Next: Agent Work Execution (via issue assignment)

STAGE 5: SELF-REINFORCEMENT
  └─ Triggers: On PR close, weekly schedule
  └─ Outputs: Failure patterns, solution history, metrics
  └─ Next: Learning Ingestion (feeds back)
```

### Critical Loop Properties

1. **No Race Conditions**: Sequential execution via `workflow_run`
2. **Proper Triggers**: Each stage triggers the next appropriately
3. **State Consistency**: File updates happen in order
4. **PR-Based Updates**: Never push directly to main
5. **Validation at Each Stage**: Constraints enforced throughout

### Example Workflow Chaining

```yaml
# Stage 2 (Combined Learning) triggered by Stage 1 completion
on:
  workflow_run:
    workflows: ["Learning: TLDR Tech", "Learning: Hacker News"]
    types: [completed]
    branches: [main]
  schedule:
    - cron: '0 8,20 * * *'

# Stage 3 (World Update) triggered by Stage 2 completion  
on:
  workflow_run:
    workflows: ["Learning: Combined Sources"]
    types: [completed]
    branches: [main]
  schedule:
    - cron: '0 */2 * * *'
```

---

## 🚨 Critical Constraints

### 1. Branch Protection

**Rule**: All changes MUST go through Pull Requests. NEVER push directly to main.

**Enforcement**:
- GitHub branch protection rules enabled
- Workflows create branches with unique names
- PR created for every change
- Auto-merge via `auto-review-merge.yml` workflow

**Example Pattern**:
```bash
# ✅ CORRECT
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BRANCH_NAME="learning/tldr-${TIMESTAMP}-${{ github.run_id }}"
git checkout -b "${BRANCH_NAME}"
git commit -m "Update learnings"
git push origin "${BRANCH_NAME}"
gh pr create --base main --head "${BRANCH_NAME}"

# ❌ FORBIDDEN
git push origin main  # NEVER DO THIS
```

### 2. Label Management

**Rule**: NEVER assume labels exist. Create or verify before applying.

**Enforcement**:
```bash
# Always create labels before use
gh label create "learning-assignment" --color "0E8A16" --force 2>/dev/null || true
gh label create "agent:support-master" --color "1D76DB" --force 2>/dev/null || true
gh label create "category:documentation" --color "D4C5F9" --force 2>/dev/null || true

# Then apply
gh issue create --label "learning-assignment,agent:support-master"
```

**Naming Convention**:
- Lowercase only
- Hyphenated: `learning-assignment`, `agent-mission`
- Namespaced: `agent:`, `category:`, `location:`
- Examples: `agent:engineer-master`, `location:san-francisco`

### 3. Agent Capacity Limit

**Rule**: NO MORE THAN 10 agents on any mission/assignment.

**Enforcement**:
```python
# In assign-agents-to-learnings.yml
MAX_AGENTS = 10

target_agents = filter_agents(all_agents, criteria)
if len(target_agents) > MAX_AGENTS:
    # Take top 10 by relevance
    target_agents = target_agents[:MAX_AGENTS]
    
    # Create backlog issue for overflow
    overflow_agents = target_agents[MAX_AGENTS:]
    create_backlog_issue(overflow_agents, label="future-expansion")
```

**Validation Points**:
- Agent assignment workflows
- Mission creation scripts
- Collaboration manager
- Multi-agent spawner

### 4. @agent-name Mentions

**Rule**: ALWAYS use `@agent-name` syntax when referencing agents.

**Purpose**:
- Clear attribution
- Performance tracking
- Transparency
- Accountability

**Examples**:
```markdown
✅ "@support-master will create documentation"
✅ "**@engineer-master** has implemented the API"
✅ "Assigned to: @troubleshoot-expert"

❌ "The support agent will create documentation"
❌ "An agent has implemented the API"
❌ "Assigned to: support-master" (missing @)
```

**Enforcement**: All workflows, issues, PRs, and comments must include @mentions.

### 5. Issue/PR Status Updates

**Rule**: ALWAYS comment on the issue before marking work complete or removing WIP status.

**Pattern**:
```bash
# 1. Do the work
implement_solution()

# 2. Post update comment on issue
gh issue comment $ISSUE_NUM --body "**@agent-name** has completed..."

# 3. Then update PR status
gh pr ready $PR_NUM  # Remove draft/WIP status
```

---

## 🔀 Workflow Orchestration

### Workflow Chaining with `workflow_run`

**Purpose**: Ensure sequential execution and prevent race conditions

**Pattern**:
```yaml
name: "Dependent Workflow"

on:
  workflow_run:
    workflows: ["Parent Workflow Name"]
    types: [completed]
    branches: [main]
  # Optional: Also allow manual trigger
  workflow_dispatch:

jobs:
  dependent-job:
    # Only run if parent workflow succeeded
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      # ... your steps
```

### Critical Workflow Chains

1. **Learning → Combined Learning → World Update → Agent Assignment**
   - Ensures learnings are analyzed before world updates
   - World is current before agent assignments
   - No conflicting file updates

2. **PR Close → Issue Collection → Failure Learning → System Improvement**
   - Captures outcomes immediately
   - Analyzes patterns systematically
   - Feeds back to improve future work

### Best Practices

- ✅ Use `workflow_run` for sequential dependencies
- ✅ Check `conclusion == 'success'` before proceeding
- ✅ Allow `workflow_dispatch` for testing
- ✅ Set appropriate schedules as fallbacks
- ✅ Handle `continue-on-error` appropriately
- ✅ Log clear status messages

### Anti-Patterns

- ❌ Running multiple workflows that modify the same files simultaneously
- ❌ Not checking parent workflow success
- ❌ Assuming files exist without verification
- ❌ Using only schedules without proper chaining
- ❌ Ignoring workflow failures silently

---

## 🤖 Agent System

### Agent Specializations

Agents are categorized by focus area:

- **Performance**: `accelerate-master`, `accelerate-specialist`
- **Testing**: `assert-specialist`, `assert-whiz`, `validator-pro`, `edge-cases-pro`
- **Coaching**: `coach-master`, `coach-wizard`, `guide-wizard`, `support-master`
- **Infrastructure**: `create-guru`, `create-champion`, `infrastructure-specialist`
- **Engineering**: `engineer-master`, `engineer-wizard`, `develop-specialist`
- **Analysis**: `investigate-champion`, `investigate-specialist`
- **Security**: `secure-specialist`, `secure-pro`, `secure-ninja`, `monitor-champion`
- **Organization**: `organize-guru`, `organize-expert`, `organize-specialist`, `refactor-champion`
- **Integration**: `bridge-master`, `integrate-specialist`
- **Documentation**: `clarify-champion`, `document-ninja`, `communicator-maestro`
- **Coordination**: `meta-coordinator`, `align-wizard`, `coordinate-wizard`
- **Innovation**: `pioneer-pro`, `pioneer-sage`
- **Troubleshooting**: `troubleshoot-expert` (protected - cannot be eliminated)

### Agent Selection Criteria

When matching agents to tasks:

1. **Specialization Match**: Primary skill alignment
2. **Location Relevance**: Geographic proximity to idea origins
3. **Past Performance**: Track record in similar tasks
4. **Investment Level**: Expertise depth in relevant categories
5. **Collaboration History**: Success working with other agents
6. **Availability**: Current workload and status

### Agent Performance Tracking

Agents are scored on:
- **Code Quality** (30%): PR reviews, code review feedback
- **Issue Resolution** (25%): Successfully closed issues
- **PR Success Rate** (25%): Merged vs. failed PRs
- **Peer Review** (20%): Community feedback, collaboration

**Thresholds**:
- ✅ **85%+**: Hall of Fame (top performers)
- ⚠️ **30-85%**: Active and contributing
- ❌ **<30%**: Natural selection (eliminated)

### Protected Agents

**troubleshoot-expert** is protected and cannot be eliminated, as it's essential for system maintenance and debugging.

---

## 🌍 World Model

### Purpose

The world model provides:
- Geographic visualization of agent activity
- Idea-to-location mapping
- Agent navigation paths
- Real-time system state

### Components

**world_state.json** structure:
```json
{
  "tick": 12345,
  "agents": [
    {
      "id": "agent-123",
      "name": "engineer-master",
      "location_region_id": "san-francisco",
      "current_idea_id": "idea-456",
      "status": "exploring",
      "path": ["san-francisco", "seattle", "austin"],
      "metrics": { ... }
    }
  ],
  "ideas": [
    {
      "id": "idea-456",
      "title": "Implement GraphQL API",
      "inspiration_regions": [
        {"region_id": "san-francisco", "weight": 0.8},
        {"region_id": "seattle", "weight": 0.6}
      ]
    }
  ],
  "regions": {
    "san-francisco": {
      "lat": 37.7749,
      "lng": -122.4194,
      "name": "San Francisco",
      "companies": ["GitHub", "OpenAI"]
    }
  }
}
```

**knowledge.json** structure:
```json
{
  "concepts": [
    {
      "id": "graphql",
      "name": "GraphQL",
      "category": "API Design",
      "related": ["rest", "api", "backend"]
    }
  ],
  "relationships": [
    {
      "from": "graphql",
      "to": "rest",
      "type": "alternative",
      "strength": 0.7
    }
  ]
}
```

### Agent Navigation

1. **Idea Assignment**: Agent receives idea with inspiration regions
2. **Path Building**: Navigator creates weighted path through regions
3. **Movement**: Agent moves one step per world tick
4. **Completion**: Agent reaches all destinations, marks idea complete

---

## 🔗 Integration Points

### GitHub Integration

- **Issues**: Mission assignment, tracking, discussions
- **Pull Requests**: Code changes, reviews, merging
- **Actions**: Workflow automation, CI/CD
- **Pages**: Public dashboard and visualization
- **GraphQL API**: Copilot assignment, data queries
- **REST API**: Issue/PR management, data retrieval

### External Integrations

- **TLDR Tech**: Learning source (RSS feeds)
- **Hacker News**: Learning source (Firebase API)
- **GitHub Trending**: Learning source (web scraping)

### Internal Integrations

- **Python Modules**: `tools/` and `world/` packages
- **Shell Scripts**: Utility scripts in `scripts/`
- **JSON Data**: State files, configurations, caches
- **Markdown Docs**: Documentation, summaries, reports

---

## 📊 8 Mandatory Completion Questions

Every workflow, agent action, and system change MUST answer these 8 questions:

### 1. Where is the learning artifact?
**Expected answers**:
- `learnings/tldr_20231115_120000.json`
- `analysis/combined_analysis_20231115.json`
- `investigation-reports/security-audit-20231115.md`

### 2. Where is the world model update?
**Expected answers**:
- `world/world_state.json` (updated tick, agents, ideas)
- `world/knowledge.json` (updated concepts, relationships)
- PR updating world model files

### 3. Which agents are reacting?
**Expected answers**:
- `@engineer-master` assigned to issue #123
- `@support-master` creating documentation
- Agent assignment file: `world/agent_assignments_20231115.json`

### 4. Are no more than 10 agents assigned?
**Expected answers**:
- "Yes, 8 agents assigned" with validation log
- "10 agents assigned, 3 in backlog issue #456"
- Workflow validation output confirming limit

### 5. How do agents move in the world model?
**Expected answers**:
- `agent_navigator.py` movement logs
- `world_state.json` path arrays updated
- Agent moved from `san-francisco` → `seattle`

### 6. What mission issue is being created?
**Expected answers**:
- Issue #789: "🎓 Learning Task: Implement GraphQL API"
- Issue URL: https://github.com/enufacas/Chained/issues/789
- Labels: `learning-assignment`, `agent:engineer-master`, `category:api-design`

### 7. Were all labels created before use?
**Expected answers**:
- Workflow log showing `gh label create` commands
- Labels verified to exist before `gh issue create`
- No label-related errors in workflow output

### 8. Which workflow continues the loop?
**Expected answers**:
- `world-update.yml` triggered by `workflow_run`
- `assign-agents-to-learnings.yml` scheduled next
- PR merge triggers `collect-resolved-issues.yml`

**Validation**: Work is INCOMPLETE if any answer is missing or unclear.

---

## 🎯 Best Practices Summary

### For Workflows

1. ✅ Use PR-based updates (never push to main)
2. ✅ Create unique branch names with timestamps and run IDs
3. ✅ Create labels before use
4. ✅ Enforce 10-agent limit with validation
5. ✅ Use @agent-name mentions everywhere
6. ✅ Chain workflows with `workflow_run`
7. ✅ Handle errors gracefully with `continue-on-error`
8. ✅ Log clear status messages
9. ✅ Answer all 8 completion questions

### For Agents

1. ✅ Follow specialization guidelines
2. ✅ Comment on issues before marking complete
3. ✅ Create comprehensive, tested solutions
4. ✅ Document decisions and rationale
5. ✅ Collaborate when appropriate
6. ✅ Track time and provide estimates
7. ✅ Learn from failures and adapt

### For Integrations

1. ✅ Use existing Python modules in `tools/` and `world/`
2. ✅ Honor agent specializations
3. ✅ Validate inputs and outputs
4. ✅ Handle edge cases
5. ✅ Test thoroughly before deployment
6. ✅ Document integrations clearly
7. ✅ Preview and resolve conflicts

---

## 📚 Related Documentation

- [Agent System Quick Start](./AGENT_QUICKSTART.md)
- [Custom Agents Directory](./.github/agents/README.md)
- [World Model Guide](./world/README.md)
- [Workflow Validation Guide](./WORKFLOW_VALIDATION_GUIDE.md)
- [Labels Reference](./LABELS.md)
- [FAQ](./FAQ.md)

---

**This document is the source of truth for Chained's autonomous system architecture. Refer to it for all system design, workflow development, agent governance, and integration decisions.**

*📖 Maintained by **@support-master** with contributions from the autonomous agent community.*
