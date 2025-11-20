# 🤖 Autonomous Code Reviewer System

## Overview

The Autonomous Code Reviewer is a self-improving code review system that learns from PR outcomes to continuously refine its evaluation criteria. Built by **@workflows-tech-lead**, it combines automated code analysis with machine learning to provide increasingly accurate quality assessments.

## 🎯 Key Features

### 1. **Automated PR Review**
- Evaluates pull requests against multiple quality dimensions
- Provides detailed feedback with issue identification
- Suggests quality labels based on overall score
- Posts comprehensive review comments automatically

### 2. **Self-Improving Criteria**
- Learns from PR outcomes (merged vs rejected)
- Adjusts criteria weights based on effectiveness
- Tracks correlation between scores and success
- Maintains transparency through evolution history

### 3. **Multi-Dimensional Analysis**
Categories evaluated:
- **Correctness**: Error handling, null checks, logic bugs
- **Clarity**: Naming, comments, code readability
- **Security**: Input validation, sensitive data, authentication
- **Maintainability**: Code complexity, duplication, documentation
- **Workflow Specific**: Branch protection, agent attribution

### 4. **Comprehensive Monitoring**
- Real-time effectiveness dashboard
- Historical performance tracking
- Category-level analytics
- Transparent learning reports

## 📁 System Architecture

```
.github/review-system/
├── autonomous_reviewer.py       # Core review engine
├── learn_from_outcomes.py      # Learning algorithm
├── generate_dashboard.py       # Dashboard generator
├── criteria.json               # Review criteria (evolving)
└── reviews/                    # Stored review results
    └── pr-{number}-{timestamp}.json
```

## 🚀 How It Works

### Review Cycle

```
1. PR Created/Updated
   ↓
2. Workflow Triggered (autonomous-code-reviewer.yml)
   ↓
3. Fetch Changed Files
   ↓
4. Run Autonomous Reviewer
   - Load current criteria
   - Analyze each file
   - Calculate category scores
   - Generate overall score
   ↓
5. Post Review Comment
   - Overall score & label suggestion
   - Category breakdown
   - Issue details
   ↓
6. Store Review Results
   - Save to reviews/ directory
   - Track for future learning
```

### Learning Cycle

```
1. Daily Schedule / Manual Trigger
   ↓
2. Workflow Triggered (review-criteria-learning.yml)
   ↓
3. Fetch Closed PRs (last 30 days)
   ↓
4. Load Review Results
   ↓
5. Match Reviews with Outcomes
   - Merged PRs = success
   - Rejected PRs = failure
   ↓
6. Calculate Effectiveness
   - Per-category correlation
   - Overall score correlation
   - Success rate analysis
   ↓
7. Evolve Criteria
   - Adjust weights based on effectiveness
   - Update metadata
   - Record in history
   ↓
8. Create PR with Changes
   - Automated PR with learning report
   - Human oversight
   - Merge to apply evolution
```

## 📊 Effectiveness Metrics

### Category Effectiveness
Measures how well a category's score predicts PR success:

```
Effectiveness = Avg(Merged Scores) - Avg(Rejected Scores)

> 0.1   = Effective (increase weight)
< -0.1  = Ineffective (decrease weight)
-0.1 to 0.1 = Neutral (no change)
```

### Overall Correlation
Measures if higher scores correlate with merged PRs:

```
Correlation = Avg(All Merged Scores) - Avg(All Rejected Scores)

Positive = Review scores predict success
Negative = Review scores inversely predict success
```

### Weight Adjustment
Criteria weights evolve based on effectiveness:

```
New Weight = Current Weight + (Learning Rate × Effectiveness)

Min Weight: 0.1
Max Weight: 2.0
Default Learning Rate: 0.1
```

## 🛠️ Usage

### Manual Review
```bash
# Review a PR
python3 .github/review-system/autonomous_reviewer.py review \
  --pr-number 123 \
  --output review_result.json

# Review specific files
python3 .github/review-system/autonomous_reviewer.py review \
  --files '["file1.py", "file2.js"]' \
  --output review_result.json

# Check current criteria status
python3 .github/review-system/autonomous_reviewer.py status
```

### Manual Learning
```bash
# Run learning analysis
python3 .github/review-system/learn_from_outcomes.py \
  --repo enufacas/Chained \
  --days 30 \
  --learning-rate 0.1 \
  --output-report learning_report.md
```

### Generate Dashboard
```bash
# Generate effectiveness dashboard
python3 .github/review-system/generate_dashboard.py \
  --criteria .github/review-system/criteria.json \
  --output docs/reviewer-dashboard.html
```

## 📈 Dashboard

View the live effectiveness dashboard:
- **Local**: `docs/reviewer-dashboard.html`
- **GitHub Pages**: https://enufacas.github.io/Chained/reviewer-dashboard.html

The dashboard displays:
- Overall performance metrics
- Category effectiveness scores
- Weight evolution over time
- Historical learning data

## ⚙️ Configuration

### Criteria File Structure

```json
{
  "version": "1.0",
  "last_updated": "2025-01-01T00:00:00Z",
  "metadata": {
    "total_reviews": 50,
    "success_rate": 0.72
  },
  "evolution_config": {
    "learning_rate": 0.1,
    "min_reviews_before_adjustment": 10,
    "max_weight": 2.0,
    "min_weight": 0.1
  },
  "criteria": {
    "correctness": {
      "weight": 1.2,
      "threshold": 0.6,
      "checks": [...]
    }
  },
  "effectiveness_history": [...]
}
```

### Adjustable Parameters

**In criteria.json:**
- `learning_rate`: How quickly to adapt (0.1 = 10% adjustment)
- `min_reviews_before_adjustment`: Minimum data before evolving
- `max_weight`: Maximum category weight
- `min_weight`: Minimum category weight

**Per Category:**
- `weight`: Importance multiplier (0.1 - 2.0)
- `threshold`: Minimum score to pass (0.0 - 1.0)

## 🔄 Workflows

### 1. `autonomous-code-reviewer.yml`
**Trigger**: PR opened, synchronized, reopened
**Purpose**: Review PRs automatically
**Actions**:
- Fetch changed files
- Run autonomous review
- Post review comment
- Add quality label
- Store results

### 2. `review-criteria-learning.yml`
**Trigger**: Daily schedule + manual
**Purpose**: Learn from outcomes and evolve criteria
**Actions**:
- Fetch closed PRs
- Load review results
- Calculate effectiveness
- Adjust criteria weights
- Create evolution PR

### 3. `generate-reviewer-dashboard.yml`
**Trigger**: Criteria changes, daily schedule
**Purpose**: Update effectiveness dashboard
**Actions**:
- Generate HTML dashboard
- Commit to docs/
- Create PR if changed

## 📖 Review Comment Format

```markdown
## 🤖 Autonomous Code Review

✅ **Code Quality Good** / ⚠️ **Code Needs Improvement**

**Overall Score:** 72.5% ✅

### Category Scores

- **Correctness**: 80% `████████░░`
- **Clarity**: 70% `███████░░░`
- **Security**: 65% `██████░░░░`
- **Maintainability**: 75% `███████░░░`
- **Workflow Specific**: 73% `███████░░░`

### ⚠️ Issues Found

- **Issue Type** (category)
  - Details about the issue
  - Impact and recommendation

### 💡 Recommendations

- Specific suggestions for improvement
- Best practices to follow

### 📊 Review Metadata

- Score: 72.5%
- Suggested Label: `quality:approved`
- Review ID: `pr-123-20250120-120000`
```

## 🎓 Learning Examples

### Example 1: Effective Security Category

**Scenario**: Security checks consistently score higher in merged PRs

**Data**:
- Merged PRs: Avg security score = 78%
- Rejected PRs: Avg security score = 45%
- Effectiveness = +0.33

**Result**: Security weight increased from 1.0 → 1.03

### Example 2: Ineffective Clarity Category

**Scenario**: Clarity scores don't correlate with outcomes

**Data**:
- Merged PRs: Avg clarity score = 65%
- Rejected PRs: Avg clarity score = 63%
- Effectiveness = +0.02 (neutral)

**Result**: Clarity weight unchanged at 1.0

### Example 3: Strong Overall Correlation

**Data**:
- Merged PRs: Avg overall score = 72%
- Rejected PRs: Avg overall score = 48%
- Correlation = +0.24

**Interpretation**: Review scores effectively predict success

## 🔬 Technical Details

### Review Algorithm

1. **File Analysis**: Parse each changed file
2. **Check Execution**: Run category-specific checks
3. **Score Calculation**: Weighted average of categories
4. **Threshold Evaluation**: Compare against category thresholds
5. **Label Suggestion**: Map score to quality label

### Learning Algorithm

1. **Data Collection**: Match reviews with PR outcomes
2. **Correlation Analysis**: Calculate per-category effectiveness
3. **Weight Adjustment**: Apply learning rate to effective categories
4. **History Tracking**: Record evolution for transparency
5. **PR Generation**: Automated PR with learning report

### Scoring Formula

```
Category Score = (Positive Matches / Total Checks)

Overall Score = Σ(Category Score × Category Weight) / Σ(Category Weights)

Label Mapping:
  > 70% → quality:approved
  50-70% → quality:review-needed
  < 50% → quality:needs-work
```

## 🚧 Future Enhancements

Potential improvements:
- [ ] ML model for check weighting
- [ ] Custom checks per language
- [ ] Integration with static analysis tools
- [ ] A/B testing different criteria
- [ ] Team-specific criteria profiles
- [ ] Real-time learning dashboard
- [ ] Predictive PR success scoring
- [ ] Natural language check descriptions

## 🤝 Contributing

To add new review checks:

1. Edit `.github/review-system/criteria.json`
2. Add check to appropriate category:
```json
{
  "name": "Check Name",
  "description": "What this checks for",
  "positive_patterns": ["regex1", "regex2"],
  "negative_patterns": ["anti-pattern"],
  "weight": 1.0,
  "effectiveness": 0.0
}
```
3. Let the system learn its effectiveness over time

## 📝 License

Part of the Chained autonomous AI ecosystem.
Created by **@workflows-tech-lead**.

## 🙏 Acknowledgments

Built on principles of:
- Continuous improvement
- Data-driven decision making
- Transparent automation
- Human-in-the-loop validation

---

*🤖 Self-improving since 2025 - Powered by @workflows-tech-lead*
