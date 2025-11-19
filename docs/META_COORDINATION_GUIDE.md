# 🎯 Meta-Agent Coordination Quick Start Guide

> **Activate the meta-agent coordination system for complex tasks**

## What is Meta-Agent Coordination?

The meta-agent coordination system enables **@meta-coordinator** to automatically:
- Analyze task complexity
- Decompose complex tasks into sub-tasks
- Assign specialized agents to each sub-task
- Track dependencies and execution order
- Coordinate multi-agent collaboration

Think of it as having an **AI project manager** that orchestrates multiple specialized AI developers.

## When Does Coordination Trigger?

The `meta-agent-coordination.yml` workflow automatically activates when:

1. **Complex Issues**: Issues with multiple specializations required
2. **Labeled Issues**: Issues with specific coordination labels
3. **Manual Trigger**: Via workflow_dispatch for any issue

### Complexity Levels

| Level | Description | Agents | Example |
|-------|-------------|--------|---------|
| **Simple** | Single specialization | 1 | "Add README documentation" |
| **Moderate** | One specialization, complex | 1 | "Refactor code structure" |
| **Complex** | Multiple specializations | 2-4 | "Build API with security and tests" |
| **Highly Complex** | System-wide changes | 5+ | "Full user management system" |

## Quick Start

### 1. Create a Complex Issue

```markdown
Title: Build Authentication API

Description:
We need a comprehensive authentication system with:
- Security audit of current auth
- Design secure API endpoints
- Implement with performance optimization
- Add comprehensive test coverage
- Document the API fully
```

### 2. Watch the Magic

The `meta-agent-coordination` workflow will:

1. **Analyze** the issue complexity
2. **Decompose** into sub-tasks:
   - Security work → @secure-specialist
   - API design → @engineer-master
   - Performance → @accelerate-master
   - Testing → @assert-specialist
   - Documentation → @support-master

3. **Create sub-issues** for each agent
4. **Post coordination plan** on the parent issue

### 3. Track Progress

Monitor the parent issue for:
- Sub-issue links
- Completion status
- Integration updates from @meta-coordinator

## Manual Coordination

You can manually trigger coordination for any issue:

### Via GitHub Actions UI

1. Go to **Actions** → **Meta-Agent Coordination**
2. Click **Run workflow**
3. Enter the issue number
4. Optionally force coordination for simple tasks

### Via GitHub CLI

```bash
gh workflow run meta-agent-coordination.yml \
  -f issue_number=123 \
  -f force_coordination=true
```

## Understanding the Coordination Plan

When @meta-coordinator creates a plan, you'll see:

### Plan Comment Structure

```markdown
## 🎯 Meta-Agent Coordination Plan

**Complexity:** complex
**Coordination ID:** coord-issue-123-1234567890
**Estimated Duration:** medium (4-8 hours)

### Sub-Tasks

1. ⏳ Security work: Audit and fix vulnerabilities
   - Specializations: @secure-specialist
   - Priority: 10/10 (highest)
   - Dependencies: None (starts first)

2. ⏳ API work: Design and implement endpoints
   - Specializations: @engineer-master
   - Priority: 6/10
   - Dependencies: Security work

3. ⏳ Testing work: Add comprehensive tests
   - Specializations: @assert-specialist
   - Priority: 5/10
   - Dependencies: API work

### Execution Order

security → api → testing → documentation

### Parallel Opportunities

- performance + documentation (can run concurrently)
```

## Using the CLI Tools

### Analyze Task Complexity

```bash
python3 tools/meta_agent_coordinator.py analyze \
  --description "Your task description here"
```

Output:
```json
{
  "complexity": "complex",
  "plan": {
    "sub_tasks": [...],
    "execution_order": [...],
    "required_agents": [...]
  }
}
```

### Create Coordination Plan

```bash
python3 tools/meta_agent_coordinator.py coordinate \
  --task-id "issue-123" \
  --description "Build authentication API..." \
  --context '{"labels": ["api", "security"]}'
```

### View Coordination Summary

```bash
python3 tools/meta_agent_coordinator.py summary
```

### View Specific Coordination

```bash
python3 tools/meta_agent_coordinator.py summary \
  --coordination-id "coord-issue-123-1234567890"
```

## Hierarchical Agent System

The coordination follows a three-tier hierarchy:

### Tier 1: Coordinators
- **@meta-coordinator** - Overall task coordination
- **@coach-master** - Code review coordination
- **@support-master** - Documentation coordination

**Responsibilities:**
- High-level task analysis
- Delegation to specialists
- Integration of contributions
- Quality oversight

### Tier 2: Specialists
- **@engineer-master** - API and infrastructure
- **@secure-specialist** - Security implementation
- **@create-guru** - Feature creation
- **@organize-guru** - Code organization
- **@investigate-champion** - Analysis

**Responsibilities:**
- Domain-specific implementation
- Delegation to workers
- Technical decision-making
- Quality assurance

### Tier 3: Workers
- **@accelerate-master** - Performance optimization
- **@assert-specialist** - Test creation
- **@refactor-champion** - Code refactoring
- **@document-ninja** - Documentation writing

**Responsibilities:**
- Focused execution
- Specific task completion
- Following specialist guidance

## Delegation Flow Example

```
Issue: "Build payment processing system"
         ↓
   @meta-coordinator analyzes
         ↓
   Complexity: HIGHLY_COMPLEX
         ↓
┌────────┴────────┬────────────┬──────────┐
│                 │            │          │
Security      API Design   Database   Testing
   ↓               ↓            ↓          ↓
@secure-    @engineer-   @create-   @assert-
specialist     master       guru     specialist
   ↓               ↓                     ↓
Monitoring    Unit Tests            Integration
   ↓               ↓                  Tests
@monitor-     @assert-              ↓
champion      specialist        @assert-
                               specialist
```

## Integration Examples

### Example 1: Security Audit + API

```yaml
# The workflow detects this needs coordination
Task: "Add authentication to existing API endpoints"

Coordination Plan:
  1. @secure-specialist - Security audit (priority: 10)
  2. @engineer-master - Update API endpoints (priority: 8)
  3. @assert-specialist - Update tests (priority: 6)
  4. @document-ninja - Update API docs (priority: 4)

Dependencies: audit → api → tests → docs
```

### Example 2: Performance Optimization

```yaml
Task: "Optimize database queries for user dashboard"

Coordination Plan:
  1. @investigate-champion - Profile performance (priority: 8)
  2. @accelerate-master - Optimize queries (priority: 7)
  3. @assert-specialist - Add performance tests (priority: 6)

Dependencies: profile → optimize → tests
```

### Example 3: Full Feature Development

```yaml
Task: "Build complete user notification system"

Coordination Plan:
  1. @investigate-champion - Research notification patterns
  2. @secure-specialist - Security and privacy review
  3. @create-guru - Database schema design
  4. @engineer-master - API implementation
  5. @accelerate-master - Performance optimization
  6. @assert-specialist - Comprehensive testing
  7. @document-ninja - User and API documentation

Dependencies:
  research → security
  security → schema → api
  api → performance, api → testing
  testing → documentation
  
Parallel: performance + testing (after API)
```

## Best Practices

### 1. Clear Task Descriptions

✅ **Good:**
```markdown
Build user authentication:
- Security audit current implementation
- Design OAuth2 endpoints
- Implement with rate limiting
- Add unit and integration tests
- Document API endpoints
```

❌ **Bad:**
```markdown
Fix authentication
```

### 2. Include Context

Provide additional context for better coordination:
```json
{
  "labels": ["security", "api", "high-priority"],
  "related_issues": [456, 789],
  "constraints": ["Must maintain backward compatibility"]
}
```

### 3. Let Coordination Happen

Don't manually assign agents to complex issues. Let @meta-coordinator:
- Analyze complexity
- Select best agents
- Establish execution order
- Track dependencies

### 4. Monitor Progress

Check the parent issue regularly for:
- Sub-issue completion
- Integration updates
- Coordination adjustments

## Troubleshooting

### Issue Not Coordinated

**Problem:** Issue wasn't complex enough

**Solution:**
```bash
# Force coordination manually
gh workflow run meta-agent-coordination.yml \
  -f issue_number=123 \
  -f force_coordination=true
```

### Wrong Agent Assigned

**Problem:** Sub-task assigned to incorrect agent

**Solution:**
1. Close the sub-issue
2. Manually create new sub-issue
3. Assign correct agent with `agent:agent-name` label

### Missing Dependencies

**Problem:** Sub-task started before dependencies completed

**Solution:**
- Dependencies are tracked in sub-issue descriptions
- Assigned agents should check before starting
- @meta-coordinator will comment if issues arise

## Performance Metrics

The coordination system tracks:
- Total coordinations
- Success rate
- Average agents per task
- Average completion time
- Agent utilization

View statistics:
```bash
python3 tools/meta_agent_coordinator.py summary
```

## Related Documentation

- [Meta-Agent Coordinator README](../tools/META_AGENT_COORDINATOR_README.md)
- [Hierarchical Agent System README](../tools/HIERARCHICAL_AGENT_SYSTEM_README.md)
- [Meta-Coordinator Agent Definition](../.github/agents/meta-coordinator.md)
- [Agent System Overview](../.github/agent-system/README.md)

## Interactive Demo

Run the interactive demonstration:

```bash
python3 tools/demo_meta_coordination.py
```

This shows:
- Simple task handling
- Moderate task coordination
- Complex multi-agent scenarios
- Hierarchical delegation examples

## Support

For questions or issues:
1. Check existing documentation
2. Run the demo script for examples
3. Create an issue with label `coordination`
4. @meta-coordinator will respond

---

*🎯 Part of the Chained autonomous AI ecosystem - Orchestrating brilliant collaborations.*
