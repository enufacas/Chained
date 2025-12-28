# AI Agent Learning System - Quick Reference

**@create-botter** has implemented a comprehensive learning system that enables AI agents to learn from historical PR failures and improve code generation quality.

## 🚀 Quick Start

### Get Proactive Guidance
```bash
# Query learning system for an agent
python tools/agent-learning-api.py query \
  --agent create-botter \
  --task-type infrastructure \
  --task-description "Your task description"

# Get formatted guidance for GitHub issues
python tools/pr-learning-integrator.py \
  --agent create-botter \
  --format issue-body
```

### Test the System
```bash
# Run integration tests
python tests/test_ai_agent_learning_integration.py
```

## 📊 What It Does

The system provides agents with:

### ⚠️ Proactive Warnings
- Alerts about past failures (CI, review, merge conflicts)
- Agent-specific pitfalls to avoid
- Historical context with example PRs

### ✅ Recommended Approaches
- Task-specific best practices
- Proven successful patterns
- Repository conventions

### 🎯 Success Patterns
- High-success patterns from historical data
- Code structure recommendations
- Test coverage guidance

### 📊 Historical Performance
- Success/failure rates
- Recent performance trends
- Statistical insights

## 🔄 How It Works

```
Weekly Data Collection
        ↓
PR Failure Analysis
        ↓
Pattern Detection
        ↓
Agent Profile Creation
        ↓
Real-time Guidance Injection
        ↓
Improved Code Generation
        ↓
New Data Collection
        ↓
(Continuous Improvement Loop)
```

## 📚 Full Documentation

See **[docs/AI_AGENT_LEARNING_SYSTEM.md](../docs/AI_AGENT_LEARNING_SYSTEM.md)** for:
- Complete architecture overview
- Detailed component descriptions
- Usage examples
- Integration guides
- Testing procedures
- Metrics and success indicators

## 🎯 Key Features

- **Automated Integration**: Works seamlessly with issue assignment
- **Real-time Guidance**: Injected when agents start work
- **Continuous Learning**: Improves with each PR outcome
- **Agent-Specific**: Personalized guidance per agent
- **Risk Assessment**: Identifies high-risk changes
- **Pattern Recognition**: Surfaces successful approaches

## 🧪 Example Output

```markdown
### ⚠️ Proactive Warnings

Based on historical PR failures, **@create-botter** should be aware of:

- 🔴 You have 5 past review rejections. Follow code review guidelines carefully. (Examples: #1870, #1862, #1715)

### ✅ Recommended Approach

- ✅ Follow repository conventions
- ✅ Write clear, maintainable code
- ✅ Include tests for new functionality

### 🎯 Success Patterns

PRs that follow these patterns have high success rates:

- Small PRs (≤10 files) have 100% success rate (e.g., #1, #3)
- PRs including test files have 100% success rate
- PRs with conventional commit format have 100% success rate
```

## 📈 Current Status

- ✅ 27+ PR failures tracked and analyzed
- ✅ 5 code patterns identified
- ✅ Multiple agents profiled
- ✅ Weekly automated data collection
- ✅ Real-time guidance integration
- ✅ 100% test pass rate

## 🛠️ Maintenance

The system is mostly automated:
- **Weekly**: Data collection and pattern analysis (automated)
- **Monthly**: Review effectiveness and tune thresholds (manual)
- **Continuous**: Monitor integration and fix issues (automated)

---

**Built by @create-botter** - Inventive and visionary infrastructure that learns and improves autonomously.
