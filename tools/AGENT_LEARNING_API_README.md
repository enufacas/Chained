# Agent Learning API - Proactive PR Failure Intelligence

> **Built by @APIs-architect** - Enabling AI agents to learn from historical PR failures and improve code generation quality before starting work.

## 🎯 Overview

The Agent Learning API provides a systematic, reliable interface for AI agents to query historical learning from PR failures and success patterns. This proactive guidance system helps agents avoid common pitfalls and follow proven best practices **before** they start writing code.

### Key Features

- **Proactive Guidance**: Get recommendations before starting work
- **Risk Assessment**: Evaluate risk for specific file changes
- **Historical Learning**: Learn from past PR failures and successes
- **Agent-Specific Insights**: Tailored guidance based on agent specialization
- **Success Patterns**: Identify what works well in this codebase
- **Reliable Fallbacks**: Always provides useful guidance, even with limited data

## 🏗️ Architecture

### Design Principles (by @APIs-architect)

1. **Reliability First**: Always returns useful guidance, even when data is limited
2. **Clear Structure**: Well-defined data models with consistent JSON responses
3. **Seamless Integration**: Works with existing PR failure learning infrastructure
4. **Performance**: Fast query responses (&lt;1 second typical)
5. **Actionable Output**: Provides specific, implementable recommendations

### Data Sources

The API integrates multiple learning sources:

```
┌─────────────────────────────────────────┐
│     Agent Learning API                   │
│  (agent-learning-api.py)                │
└──────────────┬──────────────────────────┘
               │
               ├──► learnings/pr_failures.json
               │    (Historical PR failure data)
               │
               ├──► learnings/pr_intelligence/code_patterns.json
               │    (Success/failure patterns)
               │
               └──► learnings/pr_intelligence/agent_profiles/*.json
                    (Agent-specific learning profiles)
```

## 📋 CLI Interface

### Commands

#### 1. Query Guidance

Get comprehensive proactive guidance before starting work:

```bash
python tools/agent-learning-api.py query \
  --agent AGENT_ID \
  --task-type TASK_TYPE \
  --task-description "Optional description"
```

**Example:**
```bash
python tools/agent-learning-api.py query \
  --agent engineer-master \
  --task-type "api-development" \
  --task-description "Create REST API endpoint for user management"
```

**Response:**
```json
{
  "agent_id": "engineer-master",
  "task_type": "api-development",
  "confidence": 0.8,
  "risk_level": "medium",
  "recommendations": [
    "✅ Design clear, RESTful endpoints",
    "✅ Include comprehensive error handling",
    "✅ Add request/response validation",
    "✅ Document API with examples"
  ],
  "warnings": [
    "⚠️ You have 5 past review rejections. Follow code review guidelines carefully."
  ],
  "best_practices": [
    "📚 Read existing code to understand patterns",
    "🧪 Test locally before committing",
    "📝 Write clear commit messages"
  ],
  "similar_failures": [
    {
      "pr_number": 1234,
      "title": "Add user API endpoint",
      "failure_type": "review_rejection",
      "lesson": "Review PR #1234 to avoid similar issues"
    }
  ],
  "success_patterns": [
    "Small PRs (≤10 files) have 100.0% success rate",
    "PRs including test files have 100.0% success rate"
  ],
  "timestamp": "2025-11-22T04:00:00+00:00"
}
```

#### 2. Assess Risk

Evaluate risk for specific file changes:

```bash
python tools/agent-learning-api.py assess-risk \
  --agent AGENT_ID \
  --files "file1.py,file2.yml,file3.md"
```

**Example:**
```bash
python tools/agent-learning-api.py assess-risk \
  --agent secure-specialist \
  --files ".github/workflows/ci.yml,src/auth.py,tests/test_auth.py"
```

**Response:**
```json
{
  "overall_risk": 0.1,
  "file_risks": {
    ".github/workflows/ci.yml": 0.3,
    "src/auth.py": 0.0,
    "tests/test_auth.py": 0.0
  },
  "risk_factors": [
    "Workflow file .github/workflows/ci.yml requires extra care"
  ],
  "recommendations": [
    "Validate YAML syntax for .github/workflows/ci.yml",
    "Test workflow thoroughly before committing",
    "Add tests for src/auth.py"
  ],
  "similar_issues": [1234, 5678]
}
```

#### 3. Get Best Practices

Retrieve agent-specific and general best practices:

```bash
python tools/agent-learning-api.py best-practices --agent AGENT_ID
```

**Example:**
```bash
python tools/agent-learning-api.py best-practices --agent organize-guru
```

**Response:**
```json
{
  "agent_id": "organize-guru",
  "best_practices": [
    "📚 Read existing code to understand patterns",
    "🧪 Test locally before committing",
    "📝 Write clear commit messages",
    "🔍 Review your own changes before creating PR",
    "💬 Respond to review feedback constructively",
    "🎯 Keep PRs focused on single purpose",
    "📊 Include test coverage for new code"
  ]
}
```

#### 4. Get Warnings

Get warnings about common pitfalls:

```bash
python tools/agent-learning-api.py warnings \
  --agent AGENT_ID \
  --task-type TASK_TYPE
```

**Example:**
```bash
python tools/agent-learning-api.py warnings \
  --agent refactor-champion \
  --task-type "refactoring"
```

**Response:**
```json
{
  "agent_id": "refactor-champion",
  "warnings": [
    "⚠️ Don't change behavior - only structure",
    "⚠️ Run all tests before and after refactoring"
  ]
}
```

## 🔌 Integration

### Automated Integration

The Agent Learning API is automatically integrated into the agent assignment workflow:

1. **Issue Created** → Agent matched via `match-issue-to-agent.py`
2. **Agent Assigned** → Learning API queried for proactive guidance
3. **Guidance Added** → Warnings, recommendations, and success patterns added to issue body
4. **Copilot Starts** → Sees learning insights in issue description

### Workflow Integration

The API is called in `tools/assign-copilot-to-issue.sh`:

```bash
# Query Agent Learning API for proactive guidance
learning_guidance=$(python3 tools/agent-learning-api.py query \
  --agent "$matched_agent" \
  --task-type "general" \
  --task-description "$issue_title")

# Extract and format insights
warnings=$(echo "$learning_guidance" | jq -r '.warnings[]')
recommendations=$(echo "$learning_guidance" | jq -r '.recommendations[]')
success_patterns=$(echo "$learning_guidance" | jq -r '.success_patterns[]')

# Add to issue body
# ... (see assign-copilot-to-issue.sh for full implementation)
```

## 📊 Data Models

### ProactiveGuidance

```python
@dataclass
class ProactiveGuidance:
    agent_id: str                      # Agent requesting guidance
    task_type: str                     # Type of task
    confidence: float                  # 0.0-1.0 confidence score
    risk_level: str                    # "low", "medium", "high"
    recommendations: List[str]         # Actionable recommendations
    warnings: List[str]                # Things to watch out for
    best_practices: List[str]          # Best practices to follow
    similar_failures: List[Dict]       # Past failures to learn from
    success_patterns: List[str]        # Patterns that lead to success
    timestamp: str                     # ISO 8601 timestamp
```

### RiskAssessment

```python
@dataclass
class RiskAssessment:
    overall_risk: float                # 0.0-1.0 overall risk score
    file_risks: Dict[str, float]       # Per-file risk scores
    risk_factors: List[str]            # Identified risk factors
    recommendations: List[str]         # Risk mitigation recommendations
    similar_issues: List[int]          # Similar PR numbers
```

## 🎓 Task-Specific Recommendations

The API provides specialized recommendations based on task type:

### API Development
- ✅ Design clear, RESTful endpoints
- ✅ Include comprehensive error handling
- ✅ Add request/response validation
- ✅ Document API with examples

### Refactoring
- ✅ Make small, focused changes
- ✅ Don't change behavior, only structure
- ✅ Run all tests before and after
- ✅ Document what and why you refactored

### Testing
- ✅ Test both success and failure cases
- ✅ Include edge cases
- ✅ Keep tests independent and isolated
- ✅ Use descriptive test names

### Security
- ✅ Validate all inputs
- ✅ Use parameterized queries
- ✅ Don't expose sensitive data in logs
- ✅ Follow principle of least privilege

## 🔄 Learning Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. PR Failures Collected                               │
│     (pr-failure-learning.yml)                           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  2. Patterns Analyzed                                   │
│     (pr-failure-intelligence.yml)                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  3. Agent Profiles Generated                            │
│     (learnings/pr_intelligence/agent_profiles/)         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  4. Agent Learning API Queries Learning                 │
│     (agent-learning-api.py)                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  5. Proactive Guidance Provided                         │
│     (Added to issue body before work starts)            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  6. Agent Uses Guidance                                 │
│     (Copilot follows recommendations when working)      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  7. New PR Created                                      │
│     (With improved quality from learning)               │
└─────────────────────────────────────────────────────────┘
```

## 🧪 Testing

### Manual Testing

```bash
# Test query command
python tools/agent-learning-api.py query \
  --agent engineer-master \
  --task-type "api-development" \
  --verbose

# Test risk assessment
python tools/agent-learning-api.py assess-risk \
  --agent secure-specialist \
  --files "src/auth.py,tests/test_auth.py" \
  --verbose

# Test best practices
python tools/agent-learning-api.py best-practices \
  --agent organize-guru \
  --verbose

# Test warnings
python tools/agent-learning-api.py warnings \
  --agent refactor-champion \
  --task-type "refactoring" \
  --verbose
```

### Integration Testing

Test the full integration in the assignment workflow:

```bash
# Trigger assignment workflow
gh workflow run copilot-graphql-assign.yml

# Or manually run the assignment script
./tools/assign-copilot-to-issue.sh
```

## 📈 Performance

- **Query Response Time**: &lt;1 second typical
- **Data Loading**: Cached on initialization
- **Memory Usage**: &lt;50 MB typical
- **Reliability**: Graceful fallbacks ensure guidance always provided

## 🎯 Success Metrics

Track the impact of the Agent Learning API:

1. **PR Success Rate**: Measure improvement in PR merge rate
2. **Review Rejection Rate**: Monitor decrease in review rejections
3. **CI Failure Rate**: Track reduction in CI failures
4. **Time to Merge**: Measure faster PR approval times
5. **Agent Performance**: Compare scores before/after API integration

## 🔮 Future Enhancements

Potential improvements for future iterations:

- **Real-time Learning**: Update guidance as new PRs are merged/rejected
- **Context-Aware Guidance**: Use issue labels and file paths for more specific advice
- **Interactive Feedback**: Allow agents to report whether guidance was helpful
- **Predictive Analytics**: Forecast PR success probability before work starts
- **Multi-Agent Insights**: Learn from successful agent collaborations

## 📚 Related Documentation

- [PR Failure Learning System](./PR_FAILURE_LEARNING_README.md)
- [PR Failure Intelligence System](./PR_FAILURE_INTELLIGENCE_README.md)
- [Agent System Documentation](../docs/AGENT_QUICKSTART.md)
- [Data Storage Lifecycle](../docs/DATA_STORAGE_LIFECYCLE.md)

## 🤝 Contributing

The Agent Learning API follows @APIs-architect principles:

- **Reliability**: Always provide useful guidance
- **Clarity**: Clear, well-structured responses
- **Integration**: Seamless workflow integration
- **Documentation**: Comprehensive usage examples
- **Testing**: Thorough validation before deployment

---

*Built by **@APIs-architect** - Ensuring reliability first, enabling agents to learn from the past and succeed in the future.*
