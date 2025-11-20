# Product Owner Agent Implementation Options

## Problem Statement
General issues written by humans are often:
- Vague or ambiguous in requirements
- Missing acceptance criteria or success metrics
- Lacking necessary context for implementation
- Difficult for specialized agents to consume effectively

**Goal**: Introduce a product owner agent that transforms general issues into well-structured, consumable formats for the agent fleet.

---

## Implementation Options

### Option 1: Pre-Processing Workflow ✅ (Recommended - Implemented)

**How it works:**
```
User creates issue
    ↓
Product Owner Enhancement Workflow (FIRST)
    ↓
  - Detects if issue needs enhancement
  - Assigns to Copilot with @product-owner directive
  - Product owner agent enhances issue
  - Preserves original in collapsible section
    ↓
Copilot Assignment Workflow (SECOND)
    ↓
  - Matches enhanced issue to specialized agent
  - Assigns to appropriate agent
  - Agent implements the solution
```

**Advantages:**
- ✅ Non-intrusive: Works alongside existing workflows
- ✅ Automatic: Runs on every new issue
- ✅ Preserves original: User's words are never lost
- ✅ Flexible: Can skip enhancement if not needed
- ✅ Auditable: Clear trail of original → enhanced → implemented
- ✅ Configurable: Heuristics can be tuned

**Disadvantages:**
- ⚠️  Adds latency: Enhancement happens before assignment
- ⚠️  Resource usage: Copilot runs for enhancement + implementation
- ⚠️  Complexity: Two-stage workflow orchestration

**Files Created:**
- `.github/workflows/product-owner-enhancement.yml` - Pre-processing workflow
- `.github/agents/product-owner.md` - Product owner agent definition
- `tools/match-issue-to-agent.py` - Updated with product-owner patterns

**Workflow Triggers:**
- `issues.opened` - Every new issue
- `workflow_dispatch` - Manual enhancement of existing issues

**Skip Conditions:**
- Issue already has `enhanced-by-po` label
- Issue already has structured format (`## 🎯 User Story`)
- Issue is long enough and well-structured (heuristics)

---

### Option 2: Product Owner as Specialized Agent Only

**How it works:**
```
User creates issue
    ↓
Copilot Assignment Workflow
    ↓
  - Matches issue to agent
  - If vague/general → @product-owner
  - If specific → specialized agent
    ↓
Product owner enhances OR specialist implements
```

**Advantages:**
- ✅ Simple: Single workflow, no orchestration
- ✅ Efficient: Only runs when needed
- ✅ Uses existing matching system
- ✅ No latency for well-structured issues

**Disadvantages:**
- ⚠️  Reactive: Only handles vague issues
- ⚠️  Misses opportunities: Well-structured issues don't get enhancement
- ⚠️  Requires manual trigger for enhancement
- ⚠️  Can't enhance before specialist assignment

**Implementation:**
- Already have: `.github/agents/product-owner.md`
- Already have: Matching patterns in `match-issue-to-agent.py`
- No workflow changes needed

---

### Option 3: Hybrid Approach (Best of Both Worlds)

**How it works:**
```
User creates issue
    ↓
Pre-Processing Check
    ↓
  - If VERY vague → Product owner enhancement (Option 1)
  - If somewhat vague → Match to @product-owner directly (Option 2)
  - If well-structured → Skip to specialized agent
    ↓
Copilot Assignment
    ↓
Specialized agent implements
```

**Advantages:**
- ✅ Flexible: Handles all cases optimally
- ✅ Efficient: Enhancement only when truly needed
- ✅ Powerful: Product owner available for both pre-processing and direct assignment
- ✅ Variety: Different approaches for different issue types

**Disadvantages:**
- ⚠️  Complex: More logic and decision points
- ⚠️  Harder to maintain: Multiple code paths
- ⚠️  Tuning required: Heuristics need adjustment

**Implementation:**
- Combine Option 1 and Option 2
- Add smart detection logic in both workflows
- Coordination between workflows needed

---

## Recommended Approach

### Start with Option 1 (Implemented)
**Why:**
1. **Non-intrusive**: Doesn't break existing workflows
2. **Universal benefit**: All issues can be enhanced
3. **Preserves original**: Clear audit trail
4. **Testable**: Easy to enable/disable and measure impact

### Evolution Path
1. **Phase 1**: Deploy Option 1, gather metrics
   - Measure: Enhancement quality, agent success rate, time to resolution
   - Learn: What types of issues benefit most from enhancement?
   
2. **Phase 2**: Monitor and tune
   - Adjust heuristics based on data
   - Refine enhancement template
   - Optimize for common patterns

3. **Phase 3**: Consider hybrid approach
   - If pre-processing shows high value, keep it
   - If only specific issue types benefit, switch to Option 2
   - If both are valuable, implement Option 3

---

## Interaction with Copilot Assignment Workflow

### Current Flow (Without Product Owner)
```yaml
copilot-graphql-assign.yml:
  triggers: [issues.opened, schedule, workflow_dispatch]
  
  steps:
    1. Get issue content
    2. Run match-issue-to-agent.py
    3. Select specialized agent
    4. Assign to Copilot with agent directive
    5. Copilot implements using agent profile
```

### New Flow (With Product Owner - Option 1)
```yaml
product-owner-enhancement.yml:
  triggers: [issues.opened]  # Runs FIRST
  priority: Higher than copilot-graphql-assign
  
  steps:
    1. Check if issue needs enhancement
    2. If yes:
       a. Assign to Copilot with @product-owner directive
       b. Product owner enhances issue (updates body)
       c. Adds 'enhanced-by-po' label
    3. If no: Skip (issue is already good)

# THEN (on issue update or after enhancement)

copilot-graphql-assign.yml:
  triggers: [issues.opened, schedule]
  
  steps:
    1. Check if already assigned to Copilot
    2. If yes: Skip (already being worked on)
    3. Get issue content (now enhanced if needed)
    4. Run match-issue-to-agent.py
    5. Select specialized agent (better match due to enhancement)
    6. Assign to Copilot with agent directive
    7. Copilot implements using agent profile
```

### Concurrency Handling
```yaml
# product-owner-enhancement.yml
concurrency:
  group: product-owner-${{ github.event.issue.number }}
  cancel-in-progress: false

# copilot-graphql-assign.yml  
concurrency:
  group: copilot-assignment-${{ github.event.issue.number }}
  cancel-in-progress: false
```

**Key Points:**
- Different concurrency groups prevent conflicts
- Product owner workflow runs first (on `issues.opened`)
- Copilot assignment checks if already assigned (skips if so)
- Both workflows have race condition protection via labels

### Label-Based Coordination
```
Labels used:
- 'enhanced-by-po' - Product owner has enhanced this issue
- 'copilot-assigned' - Issue is assigned to Copilot
- 'agent:product-owner' - Product owner is the assigned agent
```

**Workflow Logic:**
1. Product owner workflow adds `enhanced-by-po` immediately
2. Copilot assignment workflow checks for `copilot-assigned` label
3. Both workflows respect existing labels to prevent duplicate work

---

## Testing Strategy

### Unit Tests
```bash
# Test matching patterns
python3 tools/match-issue-to-agent.py \
  "Improve the system" \
  "We need to make things better"
# Should match: product-owner

python3 tools/match-issue-to-agent.py \
  "Add REST API endpoint for user authentication" \
  "Create /api/v1/auth/login with JWT tokens"
# Should match: APIs-architect (not product-owner)
```

### Integration Tests
1. **Create vague issue**: "Make the dashboard better"
   - Expected: Product owner enhancement runs
   - Expected: Issue body updated with structure
   - Expected: Then assigned to specialized agent

2. **Create specific issue**: "Fix null pointer in UserService.java line 42"
   - Expected: Product owner enhancement skips (already clear)
   - Expected: Directly assigned to appropriate agent

3. **Create structured issue**: Issue with user story and acceptance criteria
   - Expected: Product owner enhancement skips (already structured)
   - Expected: Directly assigned to appropriate agent

### Metrics to Track
- **Enhancement Rate**: % of issues enhanced
- **Match Quality**: Do enhanced issues match better agents?
- **Resolution Time**: Do enhanced issues resolve faster?
- **Agent Success**: Do agents complete enhanced issues more successfully?
- **User Satisfaction**: Are enhanced issues clearer?

---

## Configuration and Tuning

### Heuristics (in product-owner-enhancement.yml)

**Current heuristics:**
```bash
# Very short body (< 100 chars)
body_length < 100 → needs_enhancement=true

# Contains vague language
matches(improve|enhance|better|make it|should|need to) → needs_enhancement=true

# Missing acceptance criteria
!matches(acceptance|criteria|success|expected) → needs_enhancement=true

# Manual trigger
workflow_dispatch → needs_enhancement=true
```

**Tuning knobs:**
- Character threshold: Adjust 100 to higher/lower
- Vague language patterns: Add/remove keywords
- Acceptance criteria check: Make more sophisticated
- Add new heuristics: Check for specific patterns

### Agent Profile Tuning

Edit `.github/agents/product-owner.md`:
- **Enhancement template**: Modify structure
- **Personality**: Adjust communication style
- **Best practices**: Add/remove guidelines
- **Examples**: Update with project-specific examples

---

## Example Scenarios

### Scenario 1: Vague Feature Request
**Input:**
```
Title: Improve performance
Body: The system is slow. Make it faster.
```

**Product Owner Enhancement:**
```markdown
# Improve performance - Enhanced

## 📋 Original Request
<details>
<summary>View original issue content</summary>

The system is slow. Make it faster.

</details>

## 🎯 User Story
As a system user,
I want the application to respond faster,
So that I can complete tasks more efficiently and have a better experience.

## 📖 Context & Background
The current system performance has been identified as an issue affecting user
experience. This enhancement aims to identify and optimize performance bottlenecks
across the application.

## ✅ Acceptance Criteria
- [ ] Identify top 3 performance bottlenecks via profiling
- [ ] Page load time reduced by at least 30%
- [ ] API response time under 200ms for 95th percentile
- [ ] No regression in functionality or test coverage

## 🔧 Technical Considerations
- Profile the application to identify bottlenecks
- Consider: Database queries, API calls, frontend rendering
- May affect: All application layers
- Dependencies: Existing test suite must pass

## 🎨 Examples
- Example 1: Dashboard load time: Current 3s → Target <2s
- Example 2: User list API: Current 400ms → Target <200ms

## 📚 Related
- Related issues: None identified
- Documentation: docs/PERFORMANCE.md
- Code: Entire codebase potentially affected

## 🤖 Recommended Agent
**@accelerate-master** - Performance optimization specialist with focus on 
identifying and eliminating bottlenecks.

---
*Enhanced by @product-owner for improved agent consumption*
```

**Result:**
- Clear scope and measurable goals
- Specific technical considerations
- Appropriate agent selected (@accelerate-master, not generic)
- Original preserved for reference

### Scenario 2: Well-Structured Issue (Skipped)
**Input:**
```
Title: Add JWT authentication to /api/v1/auth/login endpoint

Body:
As an API user,
I want to authenticate with JWT tokens,
So that I can securely access protected endpoints.

Acceptance Criteria:
- POST /api/v1/auth/login accepts username/password
- Returns JWT token with 1-hour expiration
- Token includes user ID and roles
- All existing tests pass

Technical Notes:
- Use jsonwebtoken library
- Store secret in environment variable
- Add middleware for token validation
```

**Product Owner Enhancement:**
- **Skipped** (already well-structured)
- Directly assigned to @APIs-architect or @secure-specialist
- No enhancement needed

---

## Rollback Plan

If the product owner enhancement causes issues:

### Quick Disable
```yaml
# In product-owner-enhancement.yml
jobs:
  enhance-issue:
    if: false  # Disable entire workflow
```

### Remove Workflow
```bash
git rm .github/workflows/product-owner-enhancement.yml
```

### Keep Agent Only (Fallback to Option 2)
- Keep `.github/agents/product-owner.md`
- Keep matching patterns in `match-issue-to-agent.py`
- Remove workflow
- Product owner becomes a standard specialized agent

---

## Success Criteria

The product owner agent implementation is successful if:

### Quantitative Metrics
- ✅ 80%+ of vague issues are enhanced
- ✅ Enhanced issues have 20%+ better agent match scores
- ✅ Enhanced issues resolve 15%+ faster
- ✅ Agent success rate on enhanced issues is 10%+ higher
- ✅ Zero issues where original content is lost

### Qualitative Metrics
- ✅ Issues are clearer and more actionable
- ✅ Specialized agents report better requirements
- ✅ Fewer clarification questions needed
- ✅ Product owner enhancements add value (not just noise)
- ✅ Human feedback is positive

### System Health
- ✅ No negative impact on existing workflows
- ✅ No performance degradation
- ✅ Workflows remain maintainable
- ✅ Documentation is clear and up-to-date

---

## Next Steps

### Immediate (In This PR)
- [x] Create product owner agent definition
- [x] Add matching patterns for product owner
- [x] Create pre-processing workflow
- [x] Document implementation options
- [ ] Test with example issues
- [ ] Update main README to mention product owner

### Short Term (After PR Merge)
- [ ] Monitor product owner enhancement quality
- [ ] Gather metrics on success rates
- [ ] Tune heuristics based on data
- [ ] Collect feedback from specialized agents

### Long Term (Future Iterations)
- [ ] Consider hybrid approach if needed
- [ ] Expand product owner capabilities
- [ ] Add product owner to agent evaluation system
- [ ] Create product owner performance dashboard

---

## Questions for Discussion

1. **Heuristics**: Are the current heuristics for detecting vague issues appropriate?
2. **Enhancement Template**: Does the structure work for your use cases?
3. **Workflow Timing**: Should product owner run on ALL issues or just detected ones?
4. **Agent Recommendation**: Should product owner recommend agents or let matching handle it?
5. **Manual Override**: How should users skip product owner enhancement if they don't want it?
6. **Performance**: Is the added latency acceptable?
7. **Evolution**: Should we start with Option 1, Option 2, or jump to Option 3?

---

*This document provides a comprehensive analysis of product owner agent implementation options for the Chained autonomous AI ecosystem.*
