# Git Commit Strategy Learning System

## Overview

A visionary, self-improving infrastructure that autonomously learns optimal git commit strategies from repository history. Originally implemented by **@workflows-tech-lead** and enhanced by **@create-botter** with advanced trend analysis, continuous learning, and automated strategy application.

This system embodies Tesla's principle of elegant, powerful automation—learning from the past to illuminate the future.

## How It Works

### 1. Automated Learning Cycle

The system implements a continuous learning loop with two workflows:

**Learning Workflow** (`learn-commit-strategies.yml`):
- Runs daily at 02:00 UTC
- Analyzes complete repository history
- Extracts patterns from commit messages, sizes, and timing
- Generates actionable recommendations with confidence scores
- Stores learnings in `learnings/commit_strategies.json`
- Tracks learning history for trend analysis

**Application Workflow** (`apply-commit-strategies.yml`):
- Runs weekly on Monday at 03:00 UTC
- Generates strategy recommendations for different contexts
- Analyzes trends in commit quality over time
- Creates strategy guides with top recommendations
- Automatically applies learned strategies to documentation

### 2. Data Collection & Analysis

The system examines multiple dimensions:

- **Message Patterns**: Conventional commit prefixes (feat:, fix:, docs:, etc.)
- **Size Patterns**: Number of files and lines changed per commit
- **Timing Patterns**: Hour of day and day of week for commits
- **Directory Patterns**: Most frequently modified areas
- **Quality Metrics**: Successful commits vs. reverts
- **Trend Analysis**: How patterns evolve over time
- **Success Correlation**: Which patterns lead to faster merges

### 3. Learning Output & Storage

Results are stored in multiple locations:

- `learnings/commit_strategies.json` - Structured learning data with history
- `analysis/commit_patterns.json` - Detailed analysis metrics
- `docs/guides/commit-strategy-guide.md` - Human-readable strategy guide

### 4. Continuous Improvement

The system implements feedback loops:

- **Learning History**: Tracks up to 30 historical analysis runs
- **Trend Detection**: Identifies improving or declining patterns
- **Adaptive Recommendations**: Adjusts based on effectiveness
- **Automated Updates**: Strategy guides update automatically

### 5. Visibility & Transparency

The system creates:

- **Issues**: Summary of insights with key findings
- **Pull Requests**: Updates to learning data and strategy guides
- **Reports**: Comprehensive analysis with trends and recommendations

## Using the Enhanced System

### For Agents

Agents can leverage the learning system to:

1. **Choose commit prefixes**: Use proven conventional commit types
2. **Size commits optimally**: Target successful commit sizes
3. **Time complex changes**: Schedule based on productivity patterns
4. **Focus testing**: Prioritize frequently modified directories
5. **Track improvements**: Monitor trend data for continuous improvement
6. **Apply strategies**: Reference the generated strategy guide

### For Developers

**Manual Triggers:**

1. **Learning Analysis**: Go to Actions → "Learning: Git Commit Strategies"
2. **Strategy Application**: Go to Actions → "Apply Learned Commit Strategies"
3. Click "Run workflow"
3. Optionally specify:
   - Days to analyze (default: 30)
   - Branch to analyze (default: main)

## Learning Data Structure

### commit_strategies.json

```json
{
  "learning_type": "commit_patterns",
  "metadata": {
    "generated_at": "ISO timestamp",
    "branch_analyzed": "main",
    "commits_analyzed": 1000,
    "days_of_history": 30
  },
  "insights": [
    {
      "type": "message_pattern",
      "pattern": "feat: ...",
      "frequency": 45,
      "confidence": 0.92,
      "recommendation": "Use 'feat:' prefix for new features"
    },
    // ... more insights
  ],
  "patterns": {
    "conventional_commits": {
      "feat": 250,
      "fix": 180,
      "docs": 95,
      // ... other types
    },
    "commit_sizes": {
      "avg_files": 3.2,
      "avg_lines_added": 85,
      "avg_lines_removed": 42
    },
    "timing": {
      "peak_hour": 14,
      "peak_day": "Tuesday",
      "commits_by_hour": {...},
      "commits_by_day": {...}
    }
  },
  "learning_history": [
    {
      "timestamp": "2025-11-26T03:00:00+00:00",
      "commits_analyzed": 100,
      "successful": 85,
      "failed": 5,
      "patterns_count": 4
    }
    // ... up to 30 historical entries
  ]
}
```

## Tools & Infrastructure

### commit-strategy-learner.py

Enhanced by **@create-botter**, located in `tools/commit-strategy-learner.py`:

**Core Features:**
- Analyzes git history using subprocess (no dependencies)
- Identifies conventional commit patterns
- Calculates optimal commit sizes
- Detects productivity patterns
- Generates structured insights with confidence scores

**New Features (v1.1):**
- **Trend Analysis**: Tracks pattern evolution over time
- **Learning History**: Records up to 30 analysis runs
- **Predictive Insights**: Calculates trend velocity and confidence
- **Context-Aware Recommendations**: Different strategies for different work types
- **Automated Reporting**: Comprehensive reports with trends

**Usage:**

```bash
# Analyze recent commits
python3 tools/commit-strategy-learner.py --analyze --since 30

# Generate context-specific recommendations
python3 tools/commit-strategy-learner.py --recommend --context feature

# Analyze trends over time (NEW!)
python3 tools/commit-strategy-learner.py --trends --period 30

# Generate comprehensive report
python3 tools/commit-strategy-learner.py --report --output analysis/commit_report.md
```

### create_commit_learning_pr_body.py

Located in `.github/scripts/create_commit_learning_pr_body.py`, this helper:

- Generates formatted PR descriptions
- Includes analysis summaries
- Provides proper agent attribution

## Workflow Configuration

### Learning Workflow

**File:** `.github/workflows/learn-commit-strategies.yml`

**Triggers:**
- **Schedule**: Daily at 02:00 UTC (`0 2 * * *`)
- **Manual**: Via workflow_dispatch with optional parameters

**Permissions:**
- `contents: write` - To create PRs and update files
- `issues: write` - To create learning issues
- `pull-requests: write` - To create learning PRs

**Concurrency:**
- Group: `learning-commits-${{ github.ref }}`
- Cancel in progress: `false` (complete all runs)

### Application Workflow (NEW!)

**File:** `.github/workflows/apply-commit-strategies.yml`

**Triggers:**
- **Schedule**: Weekly on Monday at 03:00 UTC (`0 3 * * 1`)
- **Manual**: Via workflow_dispatch with strategy type selection

**Features:**
- Generates context-specific recommendations
- Analyzes trends in commit quality
- Creates strategy guides automatically
- Tracks effectiveness of applied strategies

## Integration Points

### Autonomous Learning Pipeline

This system is a core component of the autonomous learning infrastructure:

- **Data Storage**: `learnings/` directory for long-term knowledge
- **Analysis Storage**: `analysis/` directory for detailed metrics
- **Guide Storage**: `docs/guides/` for strategy documentation
- **Issue Tracking**: Creates visibility into learning activities
- **PR Workflow**: Maintains code review for automated changes
- **Feedback Loops**: Tracks strategy effectiveness over time

### Agent System Integration

Agents leverage the learning system to:

- Standardize commit message formats
- Optimize commit granularity
- Time changes strategically
- Prioritize testing efforts
- Track personal improvement trends
- Apply best practices automatically

## Maintenance & Monitoring

### Workflow Health

Check the workflow runs at:
- Actions → Learning: Git Commit Strategies (Daily)
- Actions → Apply Learned Commit Strategies (Weekly)

Review generated artifacts:
- Issues labeled with `learning`, `automated`, `analysis`, `create-botter`
- PRs labeled with `automated`, `learning`, `infrastructure`, `create-botter`
- Strategy guides in `docs/guides/commit-strategy-guide.md`

### Troubleshooting

**If the learning workflow fails:**

1. Check workflow logs in Actions tab
2. Ensure git history is available (fetch-depth: 0)
3. Review commit-strategy-learner.py output
4. Check permissions for file writes

**If no insights are generated:**

1. Check if there are commits in the analyzed period
2. Verify sufficient commit history (need at least 2 commits)
3. Review tool output for errors
4. Check that learning history is being saved

**If trends show "insufficient data":**

1. Run `--analyze` multiple times to build history
2. Wait for automated runs to accumulate data
3. Check that learning_history array exists in commit_strategies.json

## Vision & Future Enhancements

### Current State (v1.1)

✅ **Implemented:**
- Autonomous learning from commit history
- Pattern identification with confidence scores
- Context-aware recommendations
- Trend analysis and velocity tracking
- Learning history with 30-entry buffer
- Automated strategy guide generation
- Weekly application of learned strategies
- Feedback loops for continuous improvement

### Future Vision (v2.0+)

Inspired by Tesla's vision of transformative automation:

- [ ] **Predictive Commit Assistance**: AI-powered commit message suggestions
- [ ] **Real-time Strategy Application**: Pre-commit hooks with learned strategies
- [ ] **Cross-Repository Learning**: Learn from patterns across multiple repos
- [ ] **Personalized Strategies**: Agent-specific commit patterns and recommendations
- [ ] **Visual Analytics**: Interactive dashboards showing commit quality trends
- [ ] **Automated Template Generation**: Create commit message templates from patterns
- [ ] **Integration with Code Review**: Suggest commit improvements during review
- [ ] **Quality Scoring**: Real-time commit quality metrics
- [ ] **Comparative Analysis**: Compare patterns across branches and teams
- [ ] **Reinforcement Learning**: Adjust strategies based on merge success feedback

### Design Philosophy

Following **@create-botter**'s Tesla-inspired approach:

- **Self-Improving**: The system gets better over time automatically
- **Elegant**: Simple, powerful infrastructure with minimal complexity
- **Scalable**: Grows gracefully as the repository evolves
- **Autonomous**: Requires minimal human intervention
- **Transparent**: All learning is visible and understandable
- **Actionable**: Insights translate directly to practice

## Credits

**Original Implementation:** @workflows-tech-lead (Systematic workflow engineering)
**Enhanced Infrastructure:** @create-botter (Visionary automation and continuous learning)
**Philosophy:** Inspired by Nikola Tesla's approach to elegant, powerful systems

---

**Last Updated**: 2025-11-26
**Version**: 1.1 (Enhanced with trend analysis and automated application)
**Status**: ✅ Active, continuously learning and improving
