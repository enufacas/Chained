# Git Commit Strategy Learning System - Developer Guide

**Created by @create-botter** - Autonomous learning infrastructure for optimal commit strategies

## 🎯 Overview

This system learns optimal git commit strategies from your repository's history and provides actionable recommendations to improve commit quality. It embodies Tesla's vision of elegant, powerful automation that continuously evolves.

## 🏗️ Architecture

### Components

1. **Learning Engine** (`tools/commit-strategy-learner.py`)
   - Analyzes commit history
   - Identifies successful patterns
   - Generates confidence-scored recommendations
   - Tracks trends over time

2. **Dashboard** (`tools/commit-strategy-dashboard.py`)
   - Visual insights into commit patterns
   - Real-time metrics and trends
   - Interactive recommendations

3. **Pre-commit Hooks** (`tools/install-commit-hooks.sh`)
   - Automatic commit validation
   - Actionable suggestions before commits
   - Easy opt-out with `--no-verify`

4. **CI/CD Integration** (`.github/workflows/validate-commit-quality.yml`)
   - PR-level commit quality checks
   - Automated feedback on pull requests
   - Non-blocking warnings

5. **Automated Learning Workflows**
   - `learn-commit-strategies.yml` - Daily analysis
   - `apply-commit-strategies.yml` - Weekly applications

## 🚀 Quick Start

### Installation

#### 1. Pre-commit Hook (Recommended)

```bash
# Install validation hook
bash tools/install-commit-hooks.sh

# Now your commits will be validated automatically
git commit -m "feat: add new feature"

# Skip validation if needed
git commit -m "wip: rough draft" --no-verify
```

#### 2. Manual Validation

```bash
# Validate a commit message
python tools/commit-strategy-learner.py --validate "fix: correct bug"

# Validate with file info
python tools/commit-strategy-learner.py --validate "refactor: improve code" --files 5 --lines 120

# Get JSON output for automation
python tools/commit-strategy-learner.py --validate "docs: update readme" --json
```

### Usage

#### Analyze Repository History

```bash
# Analyze last 30 days
python tools/commit-strategy-learner.py --analyze

# Analyze last 60 days
python tools/commit-strategy-learner.py --analyze --since 60

# Analyze with verbose logging
python tools/commit-strategy-learner.py --analyze --verbose
```

#### Generate Recommendations

```bash
# General recommendations
python tools/commit-strategy-learner.py --recommend

# Context-specific recommendations
python tools/commit-strategy-learner.py --recommend --context feature
python tools/commit-strategy-learner.py --recommend --context bugfix
python tools/commit-strategy-learner.py --recommend --context refactor
python tools/commit-strategy-learner.py --recommend --context docs

# Lower confidence threshold to get more recommendations
python tools/commit-strategy-learner.py --recommend --min-confidence 0.6
```

#### View Dashboard

```bash
# Start interactive dashboard
python tools/commit-strategy-dashboard.py

# Specify port
python tools/commit-strategy-dashboard.py --port 8080

# Export to HTML
python tools/commit-strategy-dashboard.py --export-html dashboard.html

# Don't open browser automatically
python tools/commit-strategy-dashboard.py --no-browser
```

#### Generate Reports

```bash
# Print report to stdout
python tools/commit-strategy-learner.py --report

# Save report to file
python tools/commit-strategy-learner.py --report --output reports/commit-strategies.md
```

#### Analyze Trends

```bash
# Analyze trends over 30 days
python tools/commit-strategy-learner.py --trends

# Custom period
python tools/commit-strategy-learner.py --trends --period 60
```

## 📊 Understanding the Metrics

### Commit Quality Score (0-100)

- **90-100** (✅ Excellent): Best practices followed
- **70-89** (👍 Good): Minor improvements possible
- **50-69** (⚠️ Acceptable): Several issues to address
- **0-49** (❌ Needs Improvement): Significant quality issues

### Pattern Types

1. **Message Patterns**
   - Conventional commit format
   - Message length and clarity
   - Body presence for complex changes

2. **Size Patterns**
   - Files per commit (ideal: 5-7)
   - Lines changed (ideal: ~100)
   - Focused vs scattered changes

3. **Organization Patterns**
   - File type focus
   - Directory organization
   - Related changes grouped

4. **Timing Patterns**
   - Peak commit hours
   - Optimal development times

### Success Metrics

- **Success Rate**: Percentage of commits that merged successfully
- **Confidence Score**: How confident the system is in a pattern (0-100%)
- **Trend**: Whether pattern is improving, stable, or declining

## 💡 Best Practices

### Commit Message Format

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance
- `perf`: Performance
- `style`: Code style
- `build`: Build system
- `ci`: CI/CD

**Examples:**

```bash
# Good
git commit -m "feat(auth): add OAuth2 support"
git commit -m "fix(parser): handle edge case in CSV parsing"
git commit -m "docs(readme): update installation instructions"

# With body for complex changes
git commit -m "refactor(api): restructure error handling

Consolidate error handling logic into centralized middleware.
This improves code reusability and makes errors more consistent.

Closes #123"
```

### Commit Size Guidelines

- **Ideal**: 5-7 files, ~100 lines changed
- **Maximum**: 15 files, 500 lines changed
- **Principle**: One logical change per commit

**Good practices:**
```bash
# Use selective staging
git add -p  # Review and stage changes interactively

# Split large changes
git add file1.py file2.py
git commit -m "feat: add feature part 1"

git add file3.py file4.py
git commit -m "feat: add feature part 2"
```

### File Organization

- Group related changes together
- Keep file types consistent per commit
- Avoid mixing unrelated changes

**Example workflow:**
```bash
# Good: focused changes
git add src/auth/*.py
git commit -m "feat(auth): add login endpoint"

git add tests/test_auth.py
git commit -m "test(auth): add login tests"

# Avoid: mixing concerns
# Don't: git add src/auth/*.py src/billing/*.py
```

## 🔧 Advanced Usage

### Integration with CI/CD

The system automatically runs on pull requests. To customize:

Edit `.github/workflows/validate-commit-quality.yml`:

```yaml
# Fail PRs with low scores
- name: Check commit quality
  run: |
    if [ "${{ steps.analyze.outputs.average_score }}" -lt "70" ]; then
      echo "Commit quality too low"
      exit 1
    fi
```

### Custom Patterns

Extend the learner for custom patterns:

```python
# In tools/commit-strategy-learner.py
def _identify_custom_pattern(self, commits):
    # Your custom pattern logic
    custom_commits = [c for c in commits if self._matches_custom_criteria(c)]
    
    if custom_commits:
        return CommitPattern(
            pattern_name="custom_pattern",
            pattern_type="custom",
            description="Your custom pattern description",
            success_rate=len(custom_commits) / len(commits),
            # ... other fields
        )
```

### Automation Scripts

Create custom automation using the API:

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'tools')
from commit_strategy_learner import CommitStrategyLearner

# Initialize
learner = CommitStrategyLearner(repo_path='.')

# Analyze
learner.analyze_commits(since_days=30)

# Get recommendations
recs = learner.generate_recommendations(context='feature')

# Custom processing
for rec in recs:
    if rec.confidence_score > 0.8:
        print(f"High confidence: {rec.title}")
```

## 📈 Monitoring and Improvement

### Track Progress Over Time

```bash
# Generate periodic reports
python tools/commit-strategy-learner.py --report --output reports/$(date +%Y-%m-%d).md

# Analyze trends
python tools/commit-strategy-learner.py --trends --period 90

# View dashboard
python tools/commit-strategy-dashboard.py
```

### Team Metrics

```bash
# Analyze specific author
git log --author="alice" --since="30 days ago" --format="%H" | \
while read hash; do
    python tools/commit-strategy-learner.py --validate "$(git log -1 --format=%B $hash)"
done
```

## 🎓 Learning from the System

### Patterns to Recognize

1. **High Success Patterns**
   - Small, focused commits
   - Clear conventional messages
   - Good balance of code and tests

2. **Low Success Patterns**
   - Large, scattered commits
   - Vague messages
   - Missing context in body

### Adaptation Strategies

1. **Start Small**: Install pre-commit hook
2. **Learn Gradually**: Review recommendations weekly
3. **Measure Impact**: Track quality scores over time
4. **Share Knowledge**: Discuss patterns with team

## 🔄 Continuous Learning

The system automatically:
- Analyzes commits daily
- Updates patterns and recommendations
- Tracks effectiveness over time
- Adapts to repository evolution

**Manual triggers:**
```bash
# Force re-analysis
python tools/commit-strategy-learner.py --analyze --since 90

# Update recommendations
python tools/commit-strategy-learner.py --recommend --context all
```

## 🆘 Troubleshooting

### Hook Not Working

```bash
# Check hook is installed
ls -la .git/hooks/commit-msg

# Reinstall
bash tools/install-commit-hooks.sh

# Test manually
python tools/commit-strategy-learner.py --validate "test message"
```

### No Patterns Found

```bash
# Ensure enough history
python tools/commit-strategy-learner.py --analyze --since 60

# Check data files
ls -la learnings/commit_strategies.json
ls -la analysis/commit_patterns.json
```

### Dashboard Won't Start

```bash
# Export to HTML instead (cross-platform)
python tools/commit-strategy-dashboard.py --export-html ~/dashboard.html
# Or specify your preferred location
python tools/commit-strategy-dashboard.py --export-html dashboard.html

# Then open in your browser
open ~/dashboard.html  # macOS
xdg-open ~/dashboard.html  # Linux
start dashboard.html  # Windows
```

## 🎨 Customization

### Adjust Thresholds

Edit `tools/commit-strategy-learner.py`:

```python
# Commit quality thresholds
MIN_MESSAGE_LENGTH = 10  # Minimum characters
MAX_MESSAGE_LENGTH = 72  # First line max
IDEAL_FILES_PER_COMMIT = 5
MAX_FILES_PER_COMMIT = 15
IDEAL_LINES_CHANGED = 100
MAX_LINES_CHANGED = 500
```

### Custom Recommendations

Add to the `_pattern_to_recommendation` method:

```python
elif pattern.pattern_name == "your_pattern":
    return StrategyRecommendation(
        recommendation_id=f"rec_{pattern.pattern_name}",
        title="Your Custom Recommendation",
        description="Your description",
        # ... other fields
    )
```

## 📚 Additional Resources

- **Conventional Commits**: https://www.conventionalcommits.org/
- **Git Best Practices**: https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project
- **Code Review Guidelines**: https://github.com/google/eng-practices

## 🤝 Contributing

To improve the system:

1. Run analysis and identify gaps
2. Add new patterns or metrics
3. Enhance visualizations
4. Improve recommendations
5. Submit PRs with your improvements

## ✨ Philosophy

This system embodies @create-botter's vision:

- **Visionary**: See patterns others miss
- **Elegant**: Simple interfaces, powerful insights
- **Autonomous**: Continuous learning and improvement
- **Empowering**: Amplify human potential through automation

---

*Powered by autonomous learning infrastructure*
*Created by **@create-botter** - Innovation that illuminates*
