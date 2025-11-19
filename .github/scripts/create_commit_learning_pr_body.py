#!/usr/bin/env python3
"""
Create PR body for commit strategy learning workflow.
This script creates a formatted PR body from environment variables.
"""

import os
import sys

def main():
    sample = os.environ.get('SAMPLE_INSIGHT', 'Multiple insights generated')
    commits = os.environ.get('TOTAL_COMMITS', '0')
    count = os.environ.get('LEARNING_COUNT', '0')
    branch = os.environ.get('ANALYZED_BRANCH', 'main')
    learning_file = os.environ.get('LEARNING_FILE', 'learnings/commit_strategies.json')
    workflow_url = os.environ.get('WORKFLOW_URL', '#')

    body = f"""## 📊 Git Commit Strategy Analysis (@workflows-tech-lead)

**Branch Analyzed:** `{branch}`
**Commits Analyzed:** {commits}
**Insights Extracted:** {count}

### 🔍 What's Included

This PR adds systematic analysis of git commit patterns to the learning database:

- Message Patterns: Conventional commit usage and formats
- Size Patterns: Optimal commit sizes for maintainability
- Timing Patterns: Peak productivity insights
- Success Metrics: Quality indicators and trends

### 💡 Sample Insight

{sample}

### 📊 Files Updated

- `{learning_file}` - Detailed learning data
- `analysis/commit_patterns.json` - Pattern analysis database

### 🤖 Agent Integration

@workflows-tech-lead has implemented this learning system to help all agents:
- Use proven commit conventions consistently
- Optimize commit sizes for better reviews
- Time complex changes strategically
- Track and improve commit quality

---

*🤖 Created by workflow: {workflow_url} - @workflows-tech-lead*
"""

    output_file = os.environ.get('OUTPUT_FILE', '/tmp/pr_body.txt')
    with open(output_file, 'w') as f:
        f.write(body)

    print(f"PR body written to {output_file}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
