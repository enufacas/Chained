# Product Owner Agent: Example Interactions

This document shows real examples of how the product owner agent enhances issues.

---

## Example 1: Performance Issue (Very Vague)

### Original Issue (by User)
```markdown
Title: Performance is bad
Body: The site is really slow. Can we make it faster?
```

### Product Owner Enhancement
```markdown
# Performance is bad - Enhanced

## 📋 Original Request
<details>
<summary>View original issue content</summary>

The site is really slow. Can we make it faster?

</details>

## 🎯 User Story
As a user of the Chained system,
I want the application pages to load and respond quickly,
So that I can work efficiently without waiting and have a smooth experience.

## 📖 Context & Background
The Chained autonomous AI ecosystem involves multiple components that could contribute
to performance issues:
- **GitHub Pages Dashboard**: Agent leaderboard, timeline, world map
- **Learning Pipeline**: TLDR, Hacker News, GitHub Trending ingestion
- **Agent Workflows**: Spawning, evaluation, assignment, execution
- **Data Processing**: Knowledge graphs, analysis, summarization

Performance impacts user experience and the autonomous system's ability to operate
efficiently. This issue aims to identify and resolve bottlenecks.

## ✅ Acceptance Criteria

### Performance Benchmarks
Given the current system state,
When measuring page load and response times,
Then the following targets should be met:

- [ ] **GitHub Pages Load Time**: Main pages load in < 2 seconds (currently ~4-5s)
- [ ] **Agent Dashboard**: Leaderboard displays in < 1.5 seconds
- [ ] **World Map**: 3D visualization initializes in < 3 seconds
- [ ] **Workflow Execution**: Average workflow runtime reduced by 20%
- [ ] **API Response**: GitHub API calls return in < 500ms (p95)

### Deliverables
- [ ] Performance profiling report identifying top 3 bottlenecks
- [ ] Implementation of optimizations with measured improvements
- [ ] Before/after metrics documented
- [ ] No regression in functionality or test coverage

## 🔧 Technical Considerations

**Potential Areas to Investigate:**
1. **Frontend (GitHub Pages)**
   - JavaScript bundle size
   - Image optimization
   - Three.js scene complexity
   - API call patterns

2. **Backend (GitHub Actions)**
   - Workflow concurrency limits
   - API rate limiting
   - Data processing efficiency
   - Caching strategies

3. **Data Layer**
   - JSON file sizes
   - Knowledge graph complexity
   - Unnecessary data fetching

**Dependencies:**
- Access to GitHub Pages analytics
- Workflow runtime logs
- Browser performance profiling

**Constraints:**
- Must maintain existing functionality
- Cannot exceed GitHub Actions limits
- All tests must continue passing

## 🎨 Examples

**Example 1: Page Load Optimization**
- **Current**: docs/agents.html loads in 4.2 seconds
- **Target**: docs/agents.html loads in < 2 seconds
- **Approach**: Lazy load agent cards, optimize JSON parsing

**Example 2: Workflow Optimization**
- **Current**: agent-spawner.yml takes 3 minutes
- **Target**: agent-spawner.yml takes < 2 minutes
- **Approach**: Parallel job execution, reduce API calls

**Example 3: 3D Rendering**
- **Current**: World map renders at 25fps on mid-range device
- **Target**: World map renders at 60fps
- **Approach**: Use InstancedMesh, reduce draw calls

## 📚 Related

**Related Issues:**
- #[previous_performance_issue] if any exist

**Documentation:**
- `docs/WORKFLOWS.md` - Workflow architecture
- `docs/organism.html` - 3D visualization implementation
- `.github/workflows/` - All workflow definitions

**Code:**
- `docs/*.html` - Frontend pages
- `docs/*.js` - JavaScript implementations
- `.github/workflows/*.yml` - Backend workflows
- `tools/*.py` - Data processing scripts

## 🤖 Recommended Agent

**Primary:** @accelerate-master
- **Specialization**: Performance optimization and algorithm acceleration
- **Approach**: Thoughtful and deliberate, focuses on efficiency
- **Why**: Expert in identifying bottlenecks and implementing optimizations

**Potential Collaborators:**
- @render-3d-master - For 3D rendering optimization
- @workflows-tech-lead - For workflow performance tuning
- @investigate-champion - For profiling and analysis

---
*Enhanced by @product-owner for improved agent consumption*
```

### Result
- ✅ Clear, measurable acceptance criteria
- ✅ Multiple specific areas to investigate
- ✅ Concrete before/after examples
- ✅ Perfect agent match (@accelerate-master)
- ✅ Original preserved

---

## Example 2: Feature Request (Somewhat Vague)

### Original Issue (by User)
```markdown
Title: Add better analytics
Body: It would be nice to see more stats about the agents
```

### Product Owner Enhancement
```markdown
# Add better analytics - Enhanced

## 📋 Original Request
<details>
<summary>View original issue content</summary>

It would be nice to see more stats about the agents

</details>

## 🎯 User Story
As a user monitoring the Chained autonomous AI ecosystem,
I want to view comprehensive analytics about agent performance and behavior,
So that I can understand system dynamics, identify trends, and make informed decisions.

## 📖 Context & Background
The current agent dashboard (`docs/agents.html`) displays basic metrics:
- Active agent count
- Hall of Fame members
- Individual agent scores
- Simple leaderboard

However, deeper insights would help understand:
- **Trends**: How do agent scores change over time?
- **Patterns**: Which specializations succeed most?
- **Behaviors**: What workflows do agents interact with?
- **Efficiency**: How long do tasks take on average?

Enhanced analytics would improve system observability and enable data-driven
improvements to the agent ecosystem.

## ✅ Acceptance Criteria

### Analytics Dashboard Features
Given the agent system is running,
When viewing the analytics dashboard,
Then the following information should be available:

#### Time Series Data
- [ ] **Score Trends**: Line chart showing agent scores over past 30 days
- [ ] **Population Dynamics**: Active/eliminated agent counts over time
- [ ] **Specialization Distribution**: Pie chart of active agent types

#### Performance Metrics
- [ ] **Success Rates**: % of completed vs failed tasks by agent
- [ ] **Average Resolution Time**: Mean time to close issues by agent
- [ ] **Hall of Fame Trajectory**: Time to reach 85% score threshold

#### Behavioral Insights
- [ ] **Workflow Usage**: Which workflows agents interact with most
- [ ] **Issue Type Preferences**: Types of issues each agent claims
- [ ] **Collaboration Patterns**: Which agents work together frequently

#### System Health
- [ ] **Spawning Rate**: New agents per week
- [ ] **Elimination Rate**: Agents removed per week
- [ ] **Quality Trend**: Overall system score moving average

### Technical Requirements
- [ ] Data visualization using Chart.js or similar
- [ ] Historical data stored in `.github/agent-system/analytics/`
- [ ] Dashboard accessible at `docs/analytics.html`
- [ ] Responsive design (mobile-friendly)
- [ ] Updates automatically via GitHub Pages workflow

## 🔧 Technical Considerations

**Data Sources:**
- `.github/agent-system/registry.json` - Current state
- `.github/agent-system/profiles/*.json` - Individual agents
- `.github/agent-system/archive/*.json` - Historical data
- Issue/PR history via GitHub API

**Implementation Approach:**
1. Create data aggregation script (`tools/aggregate-analytics.py`)
2. Run in workflow to generate `docs/data/analytics.json`
3. Build dashboard HTML/JS to visualize data
4. Integrate with existing GitHub Pages deployment

**Storage:**
- Time series data: JSON format
- Historical snapshots: Daily aggregation
- Retention: 90 days of daily data

**Libraries:**
- Chart.js for visualizations
- D3.js if more complex charts needed
- Existing GitHub Pages CSS framework

## 🎨 Examples

**Example 1: Score Trend Chart**
```javascript
// Time series line chart
{
  labels: ['Day 1', 'Day 2', ...],
  datasets: [{
    label: 'bug-hunter-alpha',
    data: [65, 70, 72, 68, ...],
  }, ...]
}
```

**Example 2: Specialization Distribution**
```javascript
// Pie chart
{
  labels: ['Bug Hunter', 'Feature Architect', 'Test Guru', ...],
  data: [8, 5, 3, ...]
}
```

**Example 3: Success Rate Table**
| Agent | Issues Completed | Success Rate | Avg Time |
|-------|-----------------|--------------|----------|
| bug-hunter-alpha | 12 | 92% | 3.2 days |
| feature-arch-beta | 8 | 87% | 5.1 days |

## 📚 Related

**Related Issues:**
- Existing agent dashboard: `docs/agents.html`
- Agent evaluation system: `.github/workflows/agent-evaluator.yml`

**Documentation:**
- `docs/AGENT_SYSTEM.md` - Agent architecture
- `.github/agent-system/README.md` - Registry structure

**Code:**
- `docs/agents.html` - Current dashboard
- `docs/script.js` - Dashboard JavaScript
- `tools/` - Data processing utilities

## 🤖 Recommended Agent

**Primary:** @investigate-champion
- **Specialization**: Data analysis and metrics investigation
- **Approach**: Visionary and analytical, inspired by Ada Lovelace
- **Why**: Expert in analyzing patterns and presenting insights

**Potential Collaborators:**
- @designer-engineer - For UI/UX design of dashboard
- @create-guru - For infrastructure setup
- @communicator-maestro - For data visualization best practices

---
*Enhanced by @product-owner for improved agent consumption*
```

### Result
- ✅ Specific feature requirements with examples
- ✅ Technical implementation approach
- ✅ Clear data sources and structure
- ✅ Perfect agent match (@investigate-champion)
- ✅ Scope is clear and bounded

---

## Example 3: Well-Structured Issue (No Enhancement Needed)

### Original Issue (by User)
```markdown
Title: Fix null pointer exception in UserService.authenticate()

Body:
## Bug Description
When calling `UserService.authenticate(username, password)` with a null password,
the method throws an unhandled NullPointerException instead of returning an error.

## Steps to Reproduce
1. Call `UserService.authenticate("testuser", null)`
2. Observe NullPointerException

## Expected Behavior
- Should return `AuthResult.failure("Password cannot be null")`
- Should not throw unhandled exception

## Actual Behavior
```java
NullPointerException at UserService.java:142
    at UserService.authenticate(UserService.java:142)
```

## Proposed Solution
Add null check at beginning of method:
```java
if (password == null) {
    return AuthResult.failure("Password cannot be null");
}
```

## Acceptance Criteria
- [ ] Null password returns error instead of throwing exception
- [ ] Unit test added for null password case
- [ ] Similar null checks added for username
- [ ] All existing tests pass
```

### Product Owner Action
```
✅ SKIPPED - Issue already well-structured

Reason: Issue contains:
- Clear bug description
- Steps to reproduce
- Expected vs actual behavior
- Proposed solution
- Acceptance criteria

No enhancement needed. Proceeding directly to agent assignment.
```

### Result
- ✅ Product owner recognizes good structure
- ✅ No unnecessary enhancement
- ✅ Efficiency preserved
- ✅ Issue goes directly to @troubleshoot-expert

---

## Example 4: Epic/Multi-Part Issue (Needs Splitting)

### Original Issue (by User)
```markdown
Title: Improve the agent system
Body: We need to make agents better. They should be faster, smarter, and more reliable.
```

### Product Owner Enhancement
```markdown
# Improve the agent system - Enhanced (EPIC)

## 📋 Original Request
<details>
<summary>View original issue content</summary>

We need to make agents better. They should be faster, smarter, and more reliable.

</details>

## 🎯 Epic Goal
As the Chained autonomous AI ecosystem operator,
I want to improve the overall agent system performance, intelligence, and reliability,
So that agents deliver better results, resolve issues faster, and operate more dependably.

## 📖 Context & Background
The request encompasses three major improvement areas that should be addressed separately:
1. **Performance ("faster")**: Execution speed and efficiency
2. **Intelligence ("smarter")**: Decision-making and matching quality
3. **Reliability ("more reliable")**: Stability and success rates

Due to the broad scope, this issue should be split into focused sub-issues
that specialized agents can tackle independently.

## 🔀 Recommended Issue Breakdown

### Issue 1: Improve Agent Performance (Faster)
**User Story:**
As an agent in the Chained ecosystem,
I want to execute tasks more quickly,
So that issues are resolved faster and system throughput increases.

**Key Areas:**
- Workflow optimization
- Parallel execution where possible
- Caching and data reuse
- Algorithm efficiency

**Recommended Agent:** @accelerate-master

---

### Issue 2: Improve Agent Intelligence (Smarter)
**User Story:**
As the agent matching system,
I want to select more appropriate agents for each issue,
So that first-time success rates increase and mismatches decrease.

**Key Areas:**
- Enhance matching patterns
- Improve agent specialization definitions
- Add learning from past assignments
- Refine confidence scoring

**Recommended Agent:** @investigate-champion + @agents-tech-lead

---

### Issue 3: Improve Agent Reliability (More Reliable)
**User Story:**
As a user of the Chained system,
I want agents to complete tasks successfully and consistently,
So that I can trust the autonomous system to deliver results.

**Key Areas:**
- Error handling improvements
- Retry mechanisms
- Health monitoring
- Fallback strategies

**Recommended Agent:** @troubleshoot-expert + @guardian-master

---

## 🎯 Action Required

### Option A: Create Sub-Issues (Recommended)
I can create three focused issues based on the breakdown above:
1. "Improve Agent Performance (Faster)" → @accelerate-master
2. "Improve Agent Intelligence (Smarter)" → @investigate-champion
3. "Improve Agent Reliability (More Reliable)" → @troubleshoot-expert

Each issue will have:
- ✅ Specific user story
- ✅ Clear acceptance criteria
- ✅ Technical considerations
- ✅ Linked back to this epic

### Option B: Keep as Epic
Keep this issue as a parent epic and manually create sub-issues,
each referencing this issue number.

## 📚 Related

**Related Systems:**
- Agent matching: `tools/match-issue-to-agent.py`
- Agent registry: `.github/agent-system/registry.json`
- Agent workflows: `.github/workflows/agent-*.yml`
- Agent evaluation: `.github/workflows/agent-evaluator.yml`

**Documentation:**
- `AGENT_QUICKSTART.md` - Agent system overview
- `docs/AGENT_SYSTEM.md` - Detailed architecture

---

## 🤖 Recommended Next Steps

**@product-owner suggests:**

1. ✅ **Approve sub-issue creation** (comment "create sub-issues")
2. ✅ **Label this as epic** (add `epic` label)
3. ✅ **Create sub-issues** with focused scope
4. ✅ **Link sub-issues** back to this epic

**OR**

1. ✅ **Provide more specific focus** (which area is most important?)
2. ✅ **Create single focused issue** for priority area
3. ✅ **Address other areas** in future issues

---
*Enhanced by @product-owner for improved agent consumption*
*NOTE: This issue needs splitting due to broad scope*
```

### Result
- ✅ Recognizes multi-part issue
- ✅ Proposes logical breakdown
- ✅ Recommends separate agents for each part
- ✅ Provides action options
- ✅ Preserves original intent

---

## Example 5: Already Enhanced Issue (Skipped)

### Original Issue (by User who learned the template)
```markdown
Title: Add code coverage reporting to test pipeline

Body:
## 🎯 User Story
As a developer,
I want to see code coverage metrics in pull requests,
So that I can ensure adequate test coverage before merging.

## 📖 Context
Currently, we run tests but don't measure coverage. This makes it hard to
identify untested code paths.

## ✅ Acceptance Criteria
- [ ] Coverage report generated on every PR
- [ ] Coverage threshold set to 80%
- [ ] Coverage badge added to README
- [ ] PR comments show coverage changes
```

### Product Owner Action
```
✅ SKIPPED - Issue already has structured format

Reason: Issue contains:
- User story (🎯)
- Context section (📖)
- Acceptance criteria (✅)
- Clear scope

Detection: Found "## 🎯 User Story" in body.

No enhancement needed. Proceeding directly to agent assignment.
```

### Result
- ✅ Smart detection of existing structure
- ✅ No duplicate enhancement
- ✅ User learns the format
- ✅ Future issues can follow template

---

## Workflow Decision Tree

```
Issue Created
    ↓
    ├─→ Has "## 🎯 User Story"? → YES → Skip enhancement
    │
    ├─→ Has `enhanced-by-po` label? → YES → Skip enhancement
    │
    ├─→ Body length > 500 chars? → YES → Likely good → Skip
    │
    ├─→ Contains acceptance criteria? → YES → Likely good → Skip
    │
    ├─→ Contains vague language? → YES → Needs enhancement → ENHANCE
    │
    ├─→ Body length < 100 chars? → YES → Needs enhancement → ENHANCE
    │
    └─→ Manual trigger? → YES → Always enhance → ENHANCE

ENHANCE:
    1. Assign to @product-owner
    2. Add `enhanced-by-po` label
    3. Product owner updates issue body
    4. Preserves original in <details>
    5. Adds structure with template
    6. Recommends appropriate agent

SKIP:
    1. Add comment "Issue structure detected, skipping enhancement"
    2. Proceed directly to copilot assignment
    3. Match to specialized agent
```

---

## Summary

The product owner agent:
- ✅ **Detects** issues that need enhancement
- ✅ **Transforms** vague requests into structured requirements
- ✅ **Preserves** original content for reference
- ✅ **Recommends** appropriate specialized agents
- ✅ **Recognizes** well-structured issues (skips unnecessary work)
- ✅ **Handles** complex scenarios (epics, multi-part issues)

**Result:** Better requirements → Better agent matching → Better implementations

---

*These examples show how the product owner agent improves issue consumability across different scenarios.*
