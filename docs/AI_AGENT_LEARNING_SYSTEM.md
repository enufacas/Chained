# AI Agent Learning System - Complete Implementation Guide

**Built by @create-botter** - System for AI agents to learn from failed PRs and improve code generation

## 🎯 Overview

The AI Agent Learning System integrates historical PR failure data into the code generation process, providing **proactive guidance** to AI agents before they start work. This creates a continuous learning feedback loop where the system improves over time.

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Data Collection Layer                      │
├─────────────────────────────────────────────────────────────┤
│ pr-failure-learning.yml (weekly)                             │
│   ↓                                                          │
│ learnings/pr_failures.json (27+ failures tracked)            │
│                                                              │
│ pr-failure-intelligence.yml (weekly)                         │
│   ↓                                                          │
│ learnings/pr_intelligence/code_patterns.json                 │
│ learnings/pr_intelligence/agent_profiles/*.json              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Learning Integration Layer                 │
├─────────────────────────────────────────────────────────────┤
│ tools/agent-learning-api.py                                  │
│   - Query guidance for agents                                │
│   - Assess risk for file changes                             │
│   - Provide best practices                                   │
│   - Generate warnings                                        │
│                                                              │
│ tools/pr-learning-integrator.py                              │
│   - Load and analyze failure data                            │
│   - Generate proactive warnings                              │
│   - Surface success patterns                                 │
│   - Format for GitHub issues                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   Code Generation Layer                      │
├─────────────────────────────────────────────────────────────┤
│ tools/assign-copilot-to-issue.sh                             │
│   ↓                                                          │
│ Issues get agent assignment with:                            │
│   - ⚠️ Proactive Warnings                                    │
│   - ✅ Recommended Approach                                  │
│   - 🎯 Success Patterns                                      │
│   - 📊 Historical Performance                                │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Components

### 1. Data Collection Workflows

**pr-failure-learning.yml**
- Runs: Weekly (Sunday midnight UTC)
- Collects closed PRs that weren't merged
- Analyzes failure types (CI, review, merge conflict)
- Stores in `learnings/pr_failures.json`

**pr-failure-intelligence.yml**
- Runs: Weekly (Sunday 12:30 AM UTC)
- Analyzes code patterns from PR history
- Generates agent learning profiles
- Creates intelligence summaries

### 2. Learning API

**agent-learning-api.py**
```python
# Get proactive guidance for an agent
python tools/agent-learning-api.py query \
  --agent create-botter \
  --task-type infrastructure \
  --task-description "Add learning system"

# Assess risk for specific files
python tools/agent-learning-api.py assess-risk \
  --agent secure-specialist \
  --files auth.py,tests/test_auth.py

# Get best practices for an agent
python tools/agent-learning-api.py best-practices \
  --agent engineer-master

# Get warnings about common pitfalls
python tools/agent-learning-api.py warnings \
  --agent refactor-champion \
  --task-type refactoring
```

**Output Format:**
```json
{
  "agent_id": "create-botter",
  "task_type": "infrastructure",
  "confidence": 0.8,
  "risk_level": "medium",
  "recommendations": [
    "✅ Follow repository conventions",
    "✅ Write clear, maintainable code"
  ],
  "warnings": [
    "⚠️ You have 5 past review rejections. Follow guidelines carefully."
  ],
  "best_practices": [
    "📚 Read existing code to understand patterns",
    "🧪 Test locally before committing"
  ],
  "similar_failures": [
    {
      "pr_number": 1870,
      "title": "[WIP] Learn from sources",
      "failure_type": "review_rejection",
      "lesson": "Review PR #1870 to avoid similar issues"
    }
  ],
  "success_patterns": [
    "Small PRs (≤10 files) have 100% success rate",
    "PRs including test files have 100% success rate"
  ],
  "timestamp": "2025-12-28T10:20:05Z"
}
```

### 3. PR Learning Integrator

**pr-learning-integrator.py**
```bash
# Generate guidance for issue body injection
python tools/pr-learning-integrator.py \
  --agent create-botter \
  --format issue-body

# Get JSON output for programmatic use
python tools/pr-learning-integrator.py \
  --agent engineer-master \
  --format json
```

### 4. Issue Assignment Integration

The `assign-copilot-to-issue.sh` script (lines 238-291) automatically:

1. Detects which agent will be assigned
2. Queries the learning API for guidance
3. Injects warnings, recommendations, and success patterns into issue body
4. Adds historical context

**Example Issue Body Section:**
```markdown
> **🤖 Agent Assignment**
> 
> This issue has been assigned to GitHub Copilot with the **@create-botter** custom agent profile.
> 
> **@create-botter** - Please use the specialized approach defined in .github/agents/create-botter.md.
> 
> **IMPORTANT**: Always mention **@create-botter** by name in all conversations.

### ⚠️ Proactive Warnings

Based on historical PR failures, **@create-botter** should be aware of:

- 🔴 You have 5 past review rejections. Follow code review guidelines carefully. (Examples: #1870, #1862, #1715)

### ✅ Recommended Approach

- ✅ Follow repository conventions
- ✅ Write clear, maintainable code
- ✅ Include tests for new functionality

### 🎯 Success Patterns

PRs that follow these patterns have high success rates:

- Small PRs (≤10 files) have 100% success rate (e.g., ##1, ##3)
- PRs including test files have 100% success rate
- PRs with conventional commit format have 100% success rate
```

## 📈 Data Flow

### Collection Phase (Weekly)
1. **pr-failure-learning.yml** runs every Sunday
2. Collects unmerged, closed PRs from last 30 days
3. Analyzes failure types, check runs, review comments
4. Stores structured data in `learnings/pr_failures.json`

### Analysis Phase (Weekly)
1. **pr-failure-intelligence.yml** runs 30 min after collection
2. Analyzes patterns in successful vs failed PRs
3. Generates agent-specific profiles
4. Creates code patterns with success rates

### Integration Phase (Real-Time)
1. **assign-copilot-to-issue.sh** runs when issue is opened
2. Determines best agent via pattern matching
3. Queries **agent-learning-api.py** for guidance
4. Injects proactive warnings and success patterns into issue
5. Agent receives historical context when starting work

### Learning Phase (Continuous)
1. New PRs complete (merged or failed)
2. Results feed back into learning data
3. Patterns refined based on outcomes
4. System improves over time

## 🎓 Learning Categories

### 1. Failure Pattern Detection
- **CI Failures**: Track which checks fail most often
- **Review Rejections**: Identify common review issues
- **Merge Conflicts**: Detect conflict-prone work patterns
- **Large PRs**: Flag changesets that tend to fail

### 2. Success Pattern Recognition
- **Small focused PRs**: Identify optimal PR size
- **Test coverage**: Correlate tests with success
- **Commit conventions**: Track format adherence
- **Documentation**: Measure impact of docs

### 3. Agent Profiling
- **Success rate per agent**: Track individual performance
- **Common failure types**: Identify agent-specific issues
- **Best practices**: Extract successful approaches
- **Avoid patterns**: Document problematic behaviors

### 4. Risk Assessment
- **File-based risk**: Identify high-risk files
- **Task-type risk**: Assess risk by task category
- **Agent-specific risk**: Calculate based on history
- **Confidence scoring**: Indicate data quality

## 🔬 Testing the System

### Manual Test
```bash
# Test the learning API
python tools/agent-learning-api.py query \
  --agent create-botter \
  --task-type infrastructure \
  --task-description "Test learning system"

# Test the integrator
python tools/pr-learning-integrator.py \
  --agent create-botter \
  --format issue-body

# Test risk assessment
python tools/agent-learning-api.py assess-risk \
  --agent secure-specialist \
  --files tools/agent-learning-api.py,tests/test_learning.py
```

### Automated Test
The system is tested automatically through:
1. Weekly data collection workflow runs
2. Issue assignment workflow runs
3. Real PR outcomes feeding back into learning

## 📚 Usage Examples

### Example 1: Agent Starting New Work
```markdown
Issue: "Implement user authentication API"

Agent receives:
⚠️ You have 3 past CI failures. Ensure tests pass locally.
✅ Follow repository conventions
✅ Design clear, RESTful endpoints
🎯 PRs including test files have 90% success rate
```

### Example 2: High-Risk Task
```markdown
Issue: "Refactor security module"

Agent receives:
⚠️ File src/auth.py was involved in 2 past failures
⚠️ You have 1 past security review rejection
✅ Make small, focused changes
✅ Validate all inputs
🎯 Small PRs (≤10 files) have 100% success rate
```

### Example 3: Success Pattern Guidance
```markdown
Issue: "Add documentation for API"

Agent receives:
✅ PRs including documentation have 100% success rate
✅ Keep PRs focused on single purpose
🎯 Documentation changes are low-risk
```

## 🔄 Feedback Loop

```
┌─────────────────────────────────────────────────────────┐
│ 1. Agent receives issue with historical context         │
│    - Warnings about past failures                       │
│    - Success patterns to follow                         │
│    - Risk assessment                                    │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Agent generates code with proactive awareness        │
│    - Avoids known pitfalls                              │
│    - Follows successful patterns                        │
│    - Tests comprehensively                              │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ 3. PR is reviewed and outcome recorded                  │
│    - Success → Reinforce patterns                       │
│    - Failure → Add to learning data                     │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Learning data updates weekly                         │
│    - Patterns refined                                   │
│    - Agent profiles updated                             │
│    - Success rates recalculated                         │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Next agent benefits from improved guidance           │
│    ← FEEDBACK LOOP CONTINUES ←                          │
└─────────────────────────────────────────────────────────┘
```

## 📊 Metrics & Success Indicators

### System Health
- **Data Coverage**: 27+ PR failures tracked
- **Pattern Confidence**: 0.7-0.9 confidence scores
- **Agent Profiles**: Multiple agents profiled
- **Success Rates**: 70-100% for high-success patterns

### Agent Performance
- **Before Learning**: Baseline failure rate
- **After Learning**: Reduced failure rate (target: 30-50% reduction)
- **Pattern Adoption**: % of PRs following success patterns
- **Warning Effectiveness**: Reduction in warned-about failures

### Learning Quality
- **Warning Accuracy**: % of warnings that prevent actual failures
- **Pattern Validity**: Success rate of recommended patterns
- **Risk Assessment**: Correlation between risk score and outcome
- **Coverage**: % of issues receiving guidance

## 🛠️ Maintenance

### Weekly Tasks (Automated)
- ✅ Collect PR failure data
- ✅ Analyze code patterns
- ✅ Update agent profiles
- ✅ Generate intelligence reports

### Monthly Review (Manual)
- Review system effectiveness
- Validate pattern accuracy
- Tune risk thresholds
- Update documentation

### Continuous
- Monitor learning data quality
- Fix integration issues
- Improve guidance formatting
- Add new pattern detection

## 🚀 Future Enhancements

### Planned Features
1. **Real-time learning**: Update profiles immediately after PR closure
2. **Context-aware guidance**: Tailor warnings to specific issue types
3. **Multi-agent collaboration**: Learn from agent pair programming
4. **Success prediction**: ML model to predict PR success probability
5. **Automated coaching**: Suggest specific code improvements

### Research Opportunities
1. **Transfer learning**: Apply patterns across agents
2. **Temporal analysis**: Detect improving/degrading trends
3. **Causal inference**: Identify true cause-effect relationships
4. **Ensemble methods**: Combine multiple learning signals

## 📖 References

### Key Files
- **Workflows**: `.github/workflows/pr-failure-learning.yml`
- **Workflows**: `.github/workflows/pr-failure-intelligence.yml`
- **API**: `tools/agent-learning-api.py`
- **Integrator**: `tools/pr-learning-integrator.py`
- **Assignment**: `tools/assign-copilot-to-issue.sh`
- **Data**: `learnings/pr_failures.json`
- **Patterns**: `learnings/pr_intelligence/code_patterns.json`

### Documentation
- **Issue Template**: `.github/ISSUE_TEMPLATE/`
- **Agent Profiles**: `.github/agents/`
- **System Architecture**: `docs/AUTONOMOUS_SYSTEM_ARCHITECTURE.md`

---

**Built by @create-botter** - Inventive and visionary infrastructure, inspired by Nikola Tesla.

*"The system learns from every failure, improving with each iteration. This is the foundation of autonomous AI excellence."*
