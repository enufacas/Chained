# PR Failure Learning Integration

A comprehensive integration module that enables AI agents to learn from historical PR failures and improve future code generation.

**Built by @create-guru** as part of the Chained autonomous AI ecosystem.

## Overview

The PR Failure Learning Integration provides:

1. **Pre-task Learning Context** - Generates proactive warnings and recommendations for agents before they start working on an issue
2. **Improvement Checklists** - Creates prioritized checklists based on agent-specific failure history
3. **Learning Tracking** - Tracks PR outcomes to measure improvement over time
4. **Success Pattern Recognition** - Identifies and communicates patterns that lead to PR success

## Quick Start

### Generate Learning Context

Get proactive warnings and recommendations before starting work:

```bash
# Basic usage
python tools/pr-failure-learning-integration.py --agent create-guru --issue-number 2946

# Output in markdown format (for issue injection)
python tools/pr-failure-learning-integration.py --agent create-guru --markdown
```

### Generate Improvement Checklist

Get a pre-submission checklist tailored to your past failures:

```bash
# JSON output
python tools/pr-failure-learning-integration.py --agent engineer-master --checklist

# Markdown output
python tools/pr-failure-learning-integration.py --agent engineer-master --checklist --markdown
```

### Track PR Outcomes

Track whether PRs succeeded or failed for learning improvement:

```bash
# Track successful PR
python tools/pr-failure-learning-integration.py \
  --agent engineer-master \
  --track-improvement \
  --pr-number 456 \
  --success

# Track failed PR
python tools/pr-failure-learning-integration.py \
  --agent engineer-master \
  --track-improvement \
  --pr-number 457 \
  --failure-type test_failure
```

### Get Learning Statistics

View an agent's improvement trajectory:

```bash
python tools/pr-failure-learning-integration.py --agent engineer-master --stats
```

## Integration with Issue Assignment

The learning integration is designed to work with the issue assignment workflow. Here's how to inject learning context into issues:

### Workflow Integration Example

```yaml
- name: Generate learning context
  id: learning
  run: |
    learning_context=$(python tools/pr-failure-learning-integration.py \
      --agent "$AGENT_ID" \
      --issue-number "$ISSUE_NUMBER" \
      --markdown)
    echo "context<<EOF" >> $GITHUB_OUTPUT
    echo "$learning_context" >> $GITHUB_OUTPUT
    echo "EOF" >> $GITHUB_OUTPUT

- name: Update issue with learning context
  run: |
    gh issue comment "$ISSUE_NUMBER" --body "${{ steps.learning.outputs.context }}"
```

## Output Formats

### Learning Context (JSON)

```json
{
  "agent_id": "engineer-master",
  "issue_number": 2946,
  "proactive_warnings": [
    "You have 3 past review rejections. Follow code review guidelines carefully.",
    "You have 2 past test failures. Ensure all tests pass before submitting."
  ],
  "recommended_approach": [
    "Follow repository conventions",
    "Write clear, maintainable code",
    "Include tests for new functionality"
  ],
  "success_patterns": [
    "Small PRs (≤10 files) have 100.0% success rate",
    "PRs including test files have 100.0% success rate"
  ],
  "past_failures_count": 5,
  "past_rejections_count": 3,
  "improvement_trajectory": "improving",
  "confidence_score": 0.75
}
```

### Learning Context (Markdown)

```markdown
### ⚠️ Proactive Warnings

Based on historical PR failures, **@engineer-master** should be aware of:

- ⚠️ You have 3 past review rejections. Follow code review guidelines carefully.
- ⚠️ You have 2 past test failures. Ensure all tests pass before submitting.

### ✅ Recommended Approach

- ✅ Follow repository conventions
- ✅ Write clear, maintainable code
- ✅ Include tests for new functionality

### 🎯 Success Patterns

PRs that follow these patterns have high success rates:

- Small PRs (≤10 files) have 100.0% success rate
- PRs including test files have 100.0% success rate
```

### Improvement Checklist (Markdown)

```markdown
## 📋 Pre-Submission Checklist

**Priority Focus Areas:**
- 🎯 Focus on comprehensive testing
- 🎯 Carefully follow code review guidelines

**Checklist:**
- [ ] 🔴 Run all tests locally before submitting
- [ ] 🔴 Run linter and fix all issues
- [ ] 🟢 Check PR size (aim for ≤10 files)
- [ ] 🟢 Sync branch with main to avoid conflicts
- [ ] 🔴 Include tests for new functionality
- [ ] 🟡 Update documentation if needed
- [ ] 🟡 Use conventional commit format in PR title
- [ ] 🟡 Review code for security implications
```

## Data Sources

The integration pulls data from:

1. **`learnings/pr_failures.json`** - Historical PR failure data collected by `pr-failure-learner.py`
2. **`learnings/pr_intelligence/code_patterns.json`** - Success patterns identified by `pr-failure-intelligence.py`
3. **`learnings/pr_intelligence/agent_learning_tracker.json`** - Per-agent learning and improvement tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  PR Failure Learning System                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────┐   │
│  │  pr-failure-    │    │  pr-failure-intelligence.py  │   │
│  │  learner.py     │    │  (Pattern Analysis)          │   │
│  │  (Data Collection)│   └───────────────┬─────────────┘   │
│  └────────┬────────┘                    │                  │
│           │                             │                  │
│           ▼                             ▼                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              pr_failures.json                        │  │
│  │              code_patterns.json                      │  │
│  └────────────────────────┬────────────────────────────┘  │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │     pr-failure-learning-integration.py              │  │
│  │     (Learning Context & Checklists)                 │  │
│  └────────────────────────┬────────────────────────────┘  │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          Issue Assignment Workflow                   │  │
│  │          (Injects warnings into issues)             │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Failure Types

The system tracks and learns from these failure types:

| Type | Description | Example Warning |
|------|-------------|-----------------|
| `test_failure` | Tests failed in CI | "Ensure all tests pass before submitting" |
| `ci_failure` | CI pipeline failed | "Run lint and build locally before submitting" |
| `review_rejection` | PR rejected by reviewer | "Follow code review guidelines carefully" |
| `merge_conflict` | PR had merge conflicts | "Keep PRs small and sync frequently with main" |

## Success Patterns

High-success patterns are automatically identified and communicated:

- **Small PRs** - PRs with ≤10 files have significantly higher success rates
- **Test Inclusion** - PRs that include test files succeed more often
- **Conventional Commits** - PRs following commit conventions are more likely to be accepted
- **Documentation** - PRs with documentation updates succeed more frequently

## Testing

Run the test suite:

```bash
python -m pytest tests/test_pr_failure_learning_integration.py -v
```

## Related Tools

- [`pr-failure-learner.py`](./pr-failure-learner.py) - Collects PR failure data from GitHub
- [`pr-failure-intelligence.py`](./pr-failure-intelligence.py) - Analyzes patterns and generates agent profiles
- [`agent-learning-api.py`](./agent-learning-api.py) - RESTful API for agent learning queries

## Workflow Integration

This tool is designed to be used with:

- `.github/workflows/pr-failure-learning.yml` - Collects failure data
- `.github/workflows/pr-failure-intelligence.yml` - Analyzes patterns
- `.github/workflows/copilot-graphql-assign.yml` - Assigns agents to issues

---

*Built by **@create-guru** - Inventive and visionary infrastructure creation*
