# Phase 3: Meta-coordinator A2A Integration - Design Document

**Status**: Planning  
**Target Start**: TBD  
**Estimated Duration**: 2-3 weeks  
**Dependencies**: Phase 1, 2A, 2B complete ✅

## Executive Summary

Phase 3 creates a new **a2a-coordinator** agent alongside the existing meta-coordinator, enabling intelligent task decomposition and multi-agent delegation through A2A protocol. This approach reduces risk by keeping the proven meta-coordinator system intact while building new A2A orchestration capabilities as a parallel system.

## Background

### Design Decision: Side-by-Side Architecture

To minimize risk to existing production workflows, we are creating an **a2a-coordinator** as a separate agent rather than modifying the existing meta-coordinator. This allows:

- **Zero Risk**: Current meta-coordinator workflows remain unchanged and production-stable
- **Parallel Development**: A2A features can be developed and tested independently
- **Clear Separation**: Single-agent assignment (meta-coordinator) vs multi-agent orchestration (a2a-coordinator)
- **Gradual Migration**: Can move functionality over time if desired, or keep both systems

### Current Meta-coordinator Capabilities
The existing meta-coordinator:
- Assigns single agents to issues based on pattern matching
- Manages agent performance tracking
- Handles PR lifecycle (review, approval, merge)
- Maintains agent registry
- Proven, production-stable system
- **Remains unchanged**

### New A2A-coordinator Capabilities
The new a2a-coordinator will:
- Decompose complex tasks into subtasks
- Delegate work to multiple agents via A2A protocol
- Coordinate agent collaboration (Tier 1 or Tier 2)
- Track multi-agent workflows
- Handle dependencies between subtasks
- Aggregate results from multiple agents

### A2A Infrastructure (Phase 1-2B)
Now available:
- ✅ 102 agents with A2A-compliant Agent Cards
- ✅ Tier 1: Same-runner HTTP communication
- ✅ Tier 2: Cross-runner GitHub-mediated communication
- ✅ Discovery service for agent lookup
- ✅ Client library for agent-to-agent calls
- ✅ Test infrastructure and examples

### Gap Addressed by A2A-coordinator
The new a2a-coordinator will fill the multi-agent orchestration gap:
- Decompose complex tasks into subtasks
- Delegate work to multiple agents via A2A
- Coordinate agent collaboration
- Track multi-agent workflows
- Handle dependencies between subtasks

## Goals

### Primary Goals
1. **Create A2A-Coordinator Agent**: New agent definition for A2A orchestration
2. **Enable Task Decomposition**: A2A-coordinator can break complex tasks into manageable subtasks
3. **Multi-Agent Delegation**: Assign subtasks to appropriate specialized agents via A2A
4. **Workflow Coordination**: Track and coordinate multi-agent workflows
5. **Intelligent Routing**: Choose between Tier 1 (fast) and Tier 2 (parallel) based on task characteristics
6. **Zero Risk to Meta-coordinator**: Keep existing meta-coordinator completely unchanged

### Secondary Goals
1. **Error Handling**: Retry failed subtasks, handle agent failures gracefully
2. **Progress Tracking**: Visibility into multi-agent workflow status
3. **Performance Optimization**: Minimize latency, maximize parallelism
4. **Production Readiness**: Robust, reliable, maintainable

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Issue                             │
│  "Implement secure REST API with comprehensive testing"     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              A2A-Coordinator (NEW)                           │
│          (Meta-coordinator remains unchanged)                │
│                                                              │
│  1. Task Analysis & Decomposition                           │
│     - Understand requirements                               │
│     - Break into subtasks                                   │
│     - Identify dependencies                                 │
│                                                              │
│  2. Agent Selection & Planning                              │
│     - Match subtasks to agents                              │
│     - Determine execution order                             │
│     - Choose tier (1 or 2)                                  │
│                                                              │
│  3. Workflow Orchestration                                  │
│     - Execute subtasks via A2A                              │
│     - Track progress                                        │
│     - Handle failures                                       │
│                                                              │
│  4. Result Aggregation                                      │
│     - Collect agent outputs                                 │
│     - Synthesize final result                               │
│     - Update issue/PR                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────┴───────────────┐
          │                              │
          ▼                              ▼
┌─────────────────────┐      ┌─────────────────────┐
│    Tier 1 (Fast)    │      │   Tier 2 (Parallel) │
│  Same-runner HTTP   │      │  GitHub-mediated    │
│                     │      │                     │
│  ┌───────────────┐  │      │  ┌───────────────┐ │
│  │ @engineer-    │  │      │  │ @secure-      │ │
│  │  master       │  │      │  │  specialist   │ │
│  └───────────────┘  │      │  └───────────────┘ │
│  ┌───────────────┐  │      │  ┌───────────────┐ │
│  │ @organize-    │  │      │  │ @assert-      │ │
│  │  guru         │  │      │  │  specialist   │ │
│  └───────────────┘  │      │  └───────────────┘ │
└─────────────────────┘      └─────────────────────┘
```

### Component Design

#### 1. Task Analyzer
**Purpose**: Understand and decompose complex tasks

**Responsibilities**:
- Parse issue description and requirements
- Identify task type (feature, bug fix, refactor, test, etc.)
- Break into subtasks with clear objectives
- Identify dependencies between subtasks
- Estimate complexity and time

**API**:
```python
class TaskAnalyzer:
    def analyze(self, issue: Issue) -> TaskPlan:
        """Analyze issue and create execution plan."""
        
    def decompose(self, task: Task) -> List[Subtask]:
        """Break task into subtasks."""
        
    def identify_dependencies(self, subtasks: List[Subtask]) -> DAG:
        """Build dependency graph."""
```

**Example**:
```python
# Input: "Implement secure REST API with comprehensive testing"
# Output:
TaskPlan(
    task="Implement secure REST API",
    subtasks=[
        Subtask(
            id="api-design",
            description="Design REST API endpoints and data models",
            agent="engineer-master",
            dependencies=[],
            estimated_time=30m
        ),
        Subtask(
            id="security-review",
            description="Review API design for security vulnerabilities",
            agent="secure-specialist",
            dependencies=["api-design"],
            estimated_time=20m
        ),
        Subtask(
            id="implementation",
            description="Implement API endpoints",
            agent="engineer-master",
            dependencies=["security-review"],
            estimated_time=60m
        ),
        Subtask(
            id="test-suite",
            description="Create comprehensive test suite",
            agent="assert-specialist",
            dependencies=["implementation"],
            estimated_time=45m
        )
    ]
)
```

#### 2. Agent Selector
**Purpose**: Match subtasks to appropriate agents

**Responsibilities**:
- Query discovery service for available agents
- Match agent skills to subtask requirements
- Consider agent performance history
- Load balance across agents

**API**:
```python
class AgentSelector:
    def select_for_subtask(self, subtask: Subtask) -> str:
        """Select best agent for subtask."""
        
    def select_for_plan(self, plan: TaskPlan) -> Dict[str, str]:
        """Select agents for all subtasks in plan."""
        
    def get_alternatives(self, agent_name: str) -> List[str]:
        """Get alternative agents with similar skills."""
```

#### 3. Tier Selector
**Purpose**: Choose optimal execution tier

**Decision Criteria**:
- **Tier 1** (Same-runner HTTP) when:
  - All subtasks < 10 minutes total
  - Real-time coordination needed
  - Sequential execution acceptable
  - Low latency critical
  
- **Tier 2** (GitHub-mediated) when:
  - Long-running tasks (> 10 minutes)
  - Parallelism beneficial
  - Independent subtasks
  - Latency acceptable (~5s)

**API**:
```python
class TierSelector:
    def select_tier(self, plan: TaskPlan) -> Tier:
        """Determine optimal execution tier."""
        
    def can_parallelize(self, subtasks: List[Subtask]) -> bool:
        """Check if subtasks can run in parallel."""
```

#### 4. Workflow Orchestrator
**Purpose**: Execute multi-agent workflows

**Responsibilities**:
- Execute subtasks in dependency order
- Track progress and status
- Handle failures and retries
- Collect results
- Provide real-time updates

**API**:
```python
class WorkflowOrchestrator:
    async def execute_plan(self, plan: TaskPlan, tier: Tier) -> WorkflowResult:
        """Execute complete workflow."""
        
    async def execute_subtask(self, subtask: Subtask, agent: str) -> SubtaskResult:
        """Execute single subtask."""
        
    def retry_failed_subtask(self, subtask: Subtask) -> SubtaskResult:
        """Retry failed subtask with backoff."""
```

#### 5. Result Aggregator
**Purpose**: Synthesize final result from agent outputs

**Responsibilities**:
- Collect all subtask results
- Combine outputs into coherent result
- Generate summary report
- Update issue/PR with status

**API**:
```python
class ResultAggregator:
    def aggregate(self, results: List[SubtaskResult]) -> FinalResult:
        """Combine subtask results."""
        
    def generate_report(self, workflow: WorkflowResult) -> str:
        """Generate human-readable report."""
```

## Side-by-Side Architecture

### A2A-Coordinator vs Meta-Coordinator

This design intentionally creates a **separate a2a-coordinator agent** rather than modifying the existing meta-coordinator:

| Aspect | Meta-Coordinator | A2A-Coordinator |
|--------|------------------|-----------------|
| **Purpose** | Single-agent assignment | Multi-agent orchestration |
| **Scope** | Issue → Agent matching | Task decomposition & delegation |
| **Communication** | GitHub (issues, PRs) | A2A Protocol (Tier 1 & 2) |
| **Status** | Production, stable | New, experimental |
| **Protection** | System agent | Protected from deletion |
| **Risk** | Zero (unchanged) | Isolated, no impact on existing |

### Benefits of Side-by-Side Design

1. **Zero Risk**: Existing meta-coordinator workflows remain completely untouched
2. **Parallel Development**: Can develop and test A2A features independently
3. **Clear Separation**: Different agents, different purposes, no confusion
4. **Gradual Adoption**: Can use both systems simultaneously
5. **Rollback Safety**: Can disable a2a-coordinator without affecting production
6. **Learning Period**: Can iterate on A2A design without production pressure

### When to Use Which Coordinator

**Use Meta-Coordinator when:**
- Simple, single-agent tasks
- Standard issue assignment
- Proven, stable workflows
- Quick turnaround needed

**Use A2A-Coordinator when:**
- Complex, multi-step tasks
- Multiple specialized agents needed
- Task decomposition required
- Agent collaboration beneficial

### Integration Strategy

Both coordinators can coexist peacefully:
- **Manual selection**: Add label `a2a-orchestration` for A2A coordinator
- **Automatic routing**: Based on issue complexity (future enhancement)
- **No conflict**: Different triggers, different workflows

### Protected Status

The **a2a-coordinator is protected** from elimination:
- Listed in `.github/agent-system/config.json` under `protected_specializations`
- Cannot be deleted through performance evaluation
- Essential for A2A orchestration capabilities
- Maintained indefinitely as core infrastructure

## Implementation Plan

### Phase 3.1: Core Infrastructure (Week 1)

#### Agent Definition Created ✅
- **`.github/agents/a2a-coordinator.md`** - Agent definition with protected status
- **`.github/agent-system/config.json`** - Added to protected_specializations list

#### Files to Create
1. **`tools/a2a/task_analyzer.py`**
   - TaskAnalyzer class
   - Task decomposition logic
   - Dependency graph construction

2. **`tools/a2a/agent_selector.py`**
   - AgentSelector class
   - Skill matching algorithm
   - Performance-based selection

3. **`tools/a2a/tier_selector.py`**
   - TierSelector class
   - Tier decision logic
   - Parallelism analysis

4. **`tools/a2a/workflow_orchestrator.py`**
   - WorkflowOrchestrator class
   - Subtask execution
   - Progress tracking
   - Error handling

5. **`tools/a2a/result_aggregator.py`**
   - ResultAggregator class
   - Result synthesis
   - Report generation

#### Tests to Create
- `tests/test_a2a_task_analyzer.py`
- `tests/test_a2a_agent_selector.py`
- `tests/test_a2a_tier_selector.py`
- `tests/test_a2a_workflow_orchestrator.py`
- `tests/test_a2a_result_aggregator.py`

### Phase 3.2: A2A-Coordinator Workflows (Week 2)

**Note:** Meta-coordinator remains unchanged. All new functionality goes into a2a-coordinator.

#### New Workflows to Create
1. **`.github/workflows/a2a-orchestration.yml`**
   - Dedicated workflow for a2a-coordinator
   - Triggers on issues with `a2a-orchestration` label
   - Invokes a2a-coordinator agent for multi-agent tasks
   - Example of complex task delegation

2. **`.github/workflows/a2a-coordinator-runner.yml`**
   - Runner workflow for a2a-coordinator
   - Handles workflow execution
   - Progress reporting
   - Integration with A2A infrastructure

#### Tools to Create
1. **`tools/a2a/a2a_coordinator.py`**
   - Main coordination logic for a2a-coordinator
   - Integrates TaskAnalyzer, AgentSelector, etc.
   - Command-line interface for workflow invocation

### Phase 3.3: Production Workflows (Week 3)

#### Workflow Patterns
1. **Feature Development**: engineer → review → test → document
2. **Security Fix**: secure-specialist → review → test → deploy
3. **Refactoring**: organize-guru → review → test → document
4. **Documentation**: document-ninja → review → publish

#### Files to Create
- `.github/workflows/a2a-feature-development.yml`
- `.github/workflows/a2a-security-fix.yml`
- `.github/workflows/a2a-refactoring.yml`
- `.github/workflows/a2a-documentation.yml`

## Task Decomposition Patterns

### Pattern 1: Sequential Pipeline
**Use Case**: Tasks with strict dependencies

```
Issue: "Implement user authentication"

Subtasks:
1. @engineer-master: Design auth system
2. @secure-specialist: Security review
3. @engineer-master: Implement auth
4. @assert-specialist: Create tests
5. @document-ninja: Write docs
```

**Execution**: Sequential (Tier 1 or 2)

### Pattern 2: Parallel Independent
**Use Case**: Tasks that can run simultaneously

```
Issue: "Add comprehensive testing"

Subtasks (parallel):
1. @assert-specialist: Unit tests
2. @validator-pro: Integration tests
3. @edge-cases-pro: Edge case tests
4. @verify-maven: End-to-end tests
```

**Execution**: Parallel (Tier 2)

### Pattern 3: Fan-out/Fan-in
**Use Case**: Multiple perspectives, single synthesis

```
Issue: "Design system architecture"

Fan-out (parallel):
1. @engineer-master: Technical design
2. @secure-specialist: Security architecture
3. @optimize-director: Performance design
4. @organize-guru: Code structure

Fan-in:
5. @meta-coordinator: Synthesize final design
```

**Execution**: Tier 2 (parallel) → Tier 1 (synthesis)

### Pattern 4: Iterative Refinement
**Use Case**: Tasks requiring multiple rounds

```
Issue: "Optimize database queries"

Round 1:
1. @optimize-director: Identify bottlenecks
2. @accelerate-master: Propose optimizations

Round 2:
3. @engineer-master: Implement changes
4. @assert-specialist: Benchmark results

Round 3 (if needed):
5. Repeat with new optimizations
```

**Execution**: Iterative Tier 1

## Error Handling Strategy

### Failure Scenarios

#### 1. Agent Unavailable
**Detection**: Agent not responding to health check  
**Recovery**: 
- Select alternative agent with similar skills
- Retry with backoff
- Escalate if no alternatives

#### 2. Subtask Failure
**Detection**: Agent returns error result  
**Recovery**:
- Retry up to 3 times with exponential backoff
- Try alternative agent if available
- Mark subtask as failed, continue workflow if not critical

#### 3. Timeout
**Detection**: Subtask exceeds estimated time  
**Recovery**:
- Poll for progress
- Extend timeout if making progress
- Cancel and retry if stuck

#### 4. Dependency Failure
**Detection**: Prerequisite subtask failed  
**Recovery**:
- Skip dependent subtasks
- Mark workflow as partially complete
- Report which subtasks completed successfully

### Retry Policy
```python
RetryConfig(
    max_attempts=3,
    initial_delay=5,  # seconds
    max_delay=60,     # seconds
    backoff_factor=2,
    retryable_errors=["timeout", "agent_unavailable", "transient_error"]
)
```

## Progress Tracking

### Real-time Updates

**Issue Comments**:
```markdown
## 🔄 Multi-Agent Workflow In Progress

**Plan**: Implement secure REST API

**Subtasks**:
- ✅ API Design (@engineer-master) - Completed in 25m
- 🔄 Security Review (@secure-specialist) - In progress (15m elapsed)
- ⏳ Implementation (@engineer-master) - Waiting for security review
- ⏳ Test Suite (@assert-specialist) - Waiting for implementation

**Overall Progress**: 1/4 complete (25%)
```

**PR Description**:
```markdown
## Multi-Agent Collaboration

This PR was created through multi-agent coordination:

1. **@engineer-master** - Designed and implemented API endpoints
2. **@secure-specialist** - Reviewed security, added authentication
3. **@assert-specialist** - Created comprehensive test suite
4. **@document-ninja** - Wrote API documentation

**Workflow Duration**: 2h 15m  
**Agents Involved**: 4  
**Subtasks Completed**: 4/4  
```

## Performance Optimization

### Optimization Strategies

#### 1. Caching
- Cache agent cards (avoid regeneration)
- Cache discovery results (5 minute TTL)
- Cache task analysis (similar issues)

#### 2. Parallelism
- Execute independent subtasks in parallel (Tier 2)
- Batch agent discoveries
- Concurrent result collection

#### 3. Smart Routing
- Use Tier 1 for < 10 minute workflows
- Use Tier 2 for long-running or parallelizable tasks
- Avoid unnecessary agent hops

#### 4. Early Termination
- Stop workflow on critical failure
- Skip non-essential subtasks on timeout
- Provide partial results

### Expected Performance

**Tier 1 Workflow** (3 agents, 30 minutes total):
- Setup overhead: ~100ms
- Communication overhead: ~10ms per call
- Total overhead: < 1 minute

**Tier 2 Workflow** (4 agents, parallel, 60 minutes total):
- Setup overhead: ~30 seconds
- Polling overhead: ~5 seconds per status check
- Total overhead: ~5 minutes

## Testing Strategy

### Unit Tests
- Test each component independently
- Mock agent responses
- Test error conditions

### Integration Tests
- Test component interactions
- Use real A2A client/server
- Test both tiers

### End-to-End Tests
- Complete workflows with multiple agents
- Real GitHub integration
- Production-like scenarios

### Example Test Cases

**Test 1**: Simple sequential workflow (Tier 1)
```
Subtasks: design → implement → test
Agents: 3
Expected: All complete successfully
```

**Test 2**: Parallel workflow (Tier 2)
```
Subtasks: 4 independent tasks
Agents: 4
Expected: All run in parallel
```

**Test 3**: Error handling
```
Subtasks: 3 tasks
Failure: Agent 2 fails
Expected: Retry, use alternative agent
```

**Test 4**: Complex dependency graph
```
Subtasks: 5 with mixed dependencies
Expected: Correct execution order
```

## Success Metrics

### Phase 3.1 (Core Infrastructure)
- [ ] TaskAnalyzer can decompose 5+ example tasks
- [ ] AgentSelector correctly matches 90%+ of subtasks
- [ ] TierSelector makes optimal decisions 95%+ of time
- [ ] WorkflowOrchestrator handles 100+ subtasks without error
- [ ] ResultAggregator produces coherent reports

### Phase 3.2 (Meta-coordinator Integration)
- [ ] Meta-coordinator can execute multi-agent workflows
- [ ] 3+ real workflows running in production
- [ ] Error handling works for common failure scenarios
- [ ] Progress tracking provides useful visibility

### Phase 3.3 (Production Workflows)
- [ ] 10+ production multi-agent workflows
- [ ] Average workflow success rate > 90%
- [ ] Average subtask retry rate < 10%
- [ ] User feedback positive

## Risks and Mitigations

### Risk 1: Complexity Explosion
**Risk**: Too many subtasks, hard to manage  
**Mitigation**: 
- Limit decomposition to 10 subtasks max
- Focus on coarse-grained subtasks
- Progressive refinement if needed

### Risk 2: Tier 2 Latency
**Risk**: GitHub polling too slow for production use  
**Mitigation**:
- Use Tier 1 where possible
- Optimize polling intervals
- Add webhook support (future)

### Risk 3: Agent Failures
**Risk**: One agent failure blocks entire workflow  
**Mitigation**:
- Robust retry logic
- Alternative agent fallback
- Graceful degradation

### Risk 4: Discovery Overhead
**Risk**: Too many discovery lookups slow things down  
**Mitigation**:
- Cache discovery results
- Batch lookups
- Pre-populate common agents

## Dependencies

### External
- A2A SDK (already installed)
- GitHub API access (already available)
- Existing agent infrastructure

### Internal
- Phase 1, 2A, 2B complete ✅
- Meta-coordinator system understanding
- Agent performance tracking data

## Timeline

### Week 1: Core Infrastructure
- Days 1-2: Task analyzer and agent selector
- Days 3-4: Tier selector and workflow orchestrator
- Day 5: Result aggregator and unit tests

### Week 2: Integration
- Days 1-2: Meta-coordinator integration
- Days 3-4: Integration testing
- Day 5: Bug fixes and refinement

### Week 3: Production
- Days 1-2: Create production workflows
- Days 3-4: End-to-end testing
- Day 5: Documentation and rollout

## Rollout Plan

### Phase A: Limited Beta (Week 3)
- Enable for 1-2 issue types only
- Monitor closely
- Gather feedback

### Phase B: Expanded Beta (Week 4)
- Enable for 5+ issue types
- Validate performance
- Refine based on feedback

### Phase C: General Availability (Week 5+)
- Enable for all suitable issues
- Production monitoring
- Continuous improvement

## Conclusion

Phase 3 represents a major leap in capabilities:
- From single-agent assignment → multi-agent orchestration
- From sequential execution → intelligent parallelism
- From simple delegation → complex workflow coordination

This enables the Chained autonomous AI ecosystem to tackle far more complex tasks through true agent collaboration.

---

**Status**: Planning Complete - Ready for Implementation  
**Next Step**: Begin Phase 3.1 implementation  
**Review Date**: TBD  
**Approval**: Pending
