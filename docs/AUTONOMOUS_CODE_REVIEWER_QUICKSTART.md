# Autonomous Code Reviewer - Quick Start

## What Is This?

An AI-powered code reviewer that **learns and improves** over time. It reviews your PRs, learns from the outcomes, and continuously evolves its criteria to become more accurate.

## Key Features

🎯 **Self-Improving**: Gets better with each review cycle  
📊 **Multi-Dimensional**: Evaluates 5 key code quality aspects  
🔄 **Feedback Loop**: Learns from merge/reject outcomes  
📈 **Metrics Tracking**: Monitors its own accuracy  
🤖 **Fully Automated**: Works via GitHub Actions

## How It Works

```
1. PR Created → 2. Auto Review → 3. Score & Feedback
                       ↓
                 5. Better Reviews ← 4. Learn from Outcome
```

## Quick Usage

### View Statistics

```bash
python3 tools/autonomous-code-reviewer.py --show-stats
```

### Review a PR

```bash
python3 tools/autonomous-code-reviewer.py --review PR_NUMBER
```

### Teach It From Outcomes

```bash
python3 tools/autonomous-code-reviewer.py --learn-from-outcome PR_NUMBER --outcome merged
```

## What Gets Reviewed

1. **Code Complexity** (25%) - Maintainability
2. **Code Style** (15%) - Formatting consistency
3. **Documentation** (20%) - Comments and docs
4. **Test Coverage** (20%) - Tests presence
5. **Security** (20%) - Vulnerability detection

## Integration

The workflow runs automatically:
- ✅ When PRs are opened/updated
- ✅ When PRs are closed (learning phase)
- ✅ Manual trigger for batch updates

## Learning Mechanism

- **Merged PR with low score** → Loosen thresholds
- **Rejected PR with high score** → Tighten thresholds
- **Predictive criteria** → Increase weight
- **Non-predictive criteria** → Decrease weight

## Files

- `tools/autonomous-code-reviewer.py` - Main tool
- `.github/workflows/autonomous-code-reviewer.yml` - Workflow
- `learnings/review_criteria.json` - Evolving criteria
- `learnings/review_history/` - Review and outcome history
- `tests/test_autonomous_code_reviewer.py` - Test suite

## Full Documentation

See [AUTONOMOUS_CODE_REVIEWER.md](./AUTONOMOUS_CODE_REVIEWER.md) for complete details.

## Credits

**Built by**: @create-botter  
**Inspiration**: Tesla's vision of self-improving systems  
**Part of**: Chained Autonomous AI Ecosystem
