# Git Commit Strategy Learning System

## Overview

**@workflows-tech-lead** has implemented an autonomous learning system that analyzes git commit patterns from the repository to extract optimal commit strategies. This system runs automatically and provides insights to help all agents improve their commit practices.

## How It Works

### 1. Automated Analysis

The system runs daily at 02:00 UTC via the `learn-commit-strategies.yml` workflow:

- Analyzes the complete repository history
- Extracts patterns from commit messages, sizes, and timing
- Generates actionable recommendations
- Stores learnings in `learnings/commit_strategies.json`

### 2. Data Collection

The analysis examines:

- **Message Patterns**: Conventional commit prefixes (feat:, fix:, docs:, etc.)
- **Size Patterns**: Number of files and lines changed per commit
- **Timing Patterns**: Hour of day and day of week for commits
- **Directory Patterns**: Most frequently modified areas
- **Quality Metrics**: Successful commits vs. reverts

### 3. Learning Output

Results are stored in two locations:

- `learnings/commit_strategies.json` - Structured learning data
- `analysis/commit_patterns.json` - Detailed analysis metrics

### 4. Visibility

The system creates:

- **Issues**: Summary of insights with key findings
- **Pull Requests**: Updates to learning data for review

## Using the Insights

### For Agents

Agents can reference `learnings/commit_strategies.json` to:

1. **Choose commit prefixes**: Use the most common conventional commit types
2. **Size commits optimally**: Target the average files/lines per commit
3. **Time complex changes**: Schedule based on productivity patterns
4. **Focus testing**: Prioritize frequently modified directories

### For Developers

Developers can manually trigger the workflow:

1. Go to Actions → "Learning: Git Commit Strategies"
2. Click "Run workflow"
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
  }
}
```

## Tools

### commit-strategy-learner.py

Located in `tools/commit-strategy-learner.py`, this tool:

- Analyzes git history using GitPython
- Identifies conventional commit patterns
- Calculates optimal commit sizes
- Detects productivity patterns
- Generates structured insights

**Usage:**

```bash
python3 tools/commit-strategy-learner.py \
  --branch main \
  --days 30 \
  --output learnings/commit_strategies.json
```

### create_commit_learning_pr_body.py

Located in `.github/scripts/create_commit_learning_pr_body.py`, this helper:

- Generates formatted PR descriptions
- Includes analysis summaries
- Provides proper @workflows-tech-lead attribution

## Workflow Configuration

### Triggers

- **Schedule**: Daily at 02:00 UTC (`0 2 * * *`)
- **Manual**: Via workflow_dispatch with optional parameters

### Permissions

- `contents: write` - To create PRs and update files
- `issues: write` - To create learning issues
- `pull-requests: write` - To create learning PRs

### Concurrency

- Group: `learning-commits-${{ github.ref }}`
- Cancel in progress: `false` (complete all runs)

## Integration Points

### Learning Pipeline

This system integrates with:

- **Data Storage**: `learnings/` directory for long-term knowledge
- **Analysis Storage**: `analysis/` directory for detailed metrics
- **Issue Tracking**: Creates visibility into learning activities
- **PR Workflow**: Maintains code review for automated changes

### Agent System

Agents can consume these learnings to:

- Standardize commit message formats
- Optimize commit granularity
- Time changes strategically
- Prioritize testing efforts

## Maintenance

### Monitoring

Check the workflow runs at:
- Actions → Learning: Git Commit Strategies

Review generated:
- Issues labeled with `learning`, `automated`, `analysis`
- PRs labeled with `automated`, `learning`, `workflows-tech-lead`

### Troubleshooting

**If the workflow fails:**

1. Check workflow logs in Actions tab
2. Verify GitPython is installed correctly
3. Ensure git history is available (fetch-depth: 0)
4. Review commit-strategy-learner.py output

**If no insights are generated:**

1. Check if there are commits in the analyzed period
2. Verify branch name is correct
3. Review tool output for errors
4. Check permissions for file writes

## Future Enhancements

Potential improvements:

- [ ] Compare patterns across branches
- [ ] Track learning trends over time
- [ ] Generate visualizations of patterns
- [ ] Integrate with code review workflows
- [ ] Create commit templates from patterns

## Credits

System designed and implemented by **@workflows-tech-lead** following systematic workflow engineering principles.

---

**Last Updated**: 2025-11-19
**Maintainer**: @workflows-tech-lead
**Status**: ✅ Active and operational
