# 🏗️ Architecture

## Automated Workflows

Chained uses GitHub Actions to maintain its fully autonomous perpetual motion:

1. **AI Idea Generator** (`idea-generator.yml`) ✨
   - Runs daily at 10 AM UTC (after learning workflows)
   - Generates creative AI-focused feature ideas with learning context
   - Adapts to trending technologies from HN and TLDR
   - Creates GitHub issues automatically
   - Can be triggered manually

2. **Copilot Assignment Workflow** (`copilot-graphql-assign.yml`)
   - Triggers when any new issue is created or labeled
   - Discovers and processes ALL open issues
   - Automatically assigns unassigned issues to Copilot via API
   - Adds tracking labels and comments
   - Requires COPILOT_PAT secret for full automation
   - Can be manually triggered with optional issue number (or process all issues)

3. **Auto Review and Merge** (`auto-review-merge.yml`) ✨
   - Runs every 15 minutes
   - Labels PRs created by Copilot with the "copilot" label
   - Reviews PRs created by Copilot (AI reviews AI code)
   - Automatically approves and merges PRs
   - Closes associated issues when PRs are merged
   - No human approval required

4. **System Monitor** (`system-monitor.yml`) 🆕
   - Timeline updates every 6 hours + on events
   - Progress tracking every 12 hours
   - Workflow health monitoring every 12 hours
   - Fetches all repository activity
   - Updates timeline data for GitHub Pages
   - Analyzes repository progress and statistics
   - Generates progress reports and health alerts

5. **Learning from TLDR Tech** (`learn-from-tldr.yml`)
   - Runs twice daily (8 AM, 8 PM UTC)
   - Fetches latest tech news and trends
   - Extracts insights about AI, DevOps, and programming
   - Saves learnings to influence future ideas

6. **Learning from Hacker News** (`learn-from-hackernews.yml`)
   - Runs three times daily (7 AM, 1 PM, 7 PM UTC)
   - Analyzes trending technical discussions
   - Categorizes topics (AI/ML, Security, Performance, etc.)
   - Generates ideas based on community trends

7. **System Kickoff** (`system-kickoff.yml`) ✨
   - Triggers automatically on first push to main
   - Can also be triggered manually
   - Validates system configuration
   - Creates required labels
   - Initializes directories
   - Triggers initial workflows
   - Creates kickoff success issue

8. **Code Analyzer** (`code-analyzer.yml`)
   - Runs on push to main and PR merges
   - Analyzes code patterns and quality
   - Learns from successful/failed merges
   - Tracks code quality trends

9. **Pattern Matcher** (`pattern-matcher.yml`)
   - Runs weekly on Mondays at 10 AM UTC
   - Scans repository for code patterns
   - Identifies anti-patterns and best practices
   - Generates pattern analysis reports

10. **Code Golf Optimizer** (`code-golf-optimizer.yml`)
    - Runs weekly on Mondays at 10 AM UTC
    - Optimizes code for minimal size
    - Generates optimization reports
    - Demonstrates code golf techniques

> **Note**: Workflows marked with ✨ have been enhanced through consolidation.
> Workflow marked with 🆕 is newly consolidated from multiple workflows.
> See [WORKFLOW_CONSOLIDATION.md](../WORKFLOW_CONSOLIDATION.md) for details.

11. **Auto Kickoff on First Run** (`auto-kickoff.yml`)
    - Runs automatically on merge to main
    - Detects if system already kicked off
    - Triggers kickoff workflow if needed
    - Ensures one-time initialization

12. **Code Golf Optimizer** (`code-golf-optimizer.yml`)
    - Runs weekly on Mondays at 10 AM UTC
    - Optimizes code for minimal character count
    - Supports Python, JavaScript, and Bash
    - Generates optimization reports with metrics
    - Can be triggered manually for specific files

13. **Self-Improving Code Analyzer** (`code-analyzer.yml`)
    - Runs automatically on every merge to main
    - Analyzes code for quality patterns and issues
    - Learns from merge outcomes (success vs. issues)
    - Tracks pattern correlations over time
    - Posts analysis reports on PRs
    - Creates issues for significant quality problems
    - Can be triggered manually for any directory

## GitHub Pages

The project includes a beautiful, responsive GitHub Pages site at [`docs/`](../docs/) that displays:

- 📈 **Live statistics** from the repository
- ⏱️ **Timeline of events** showing all AI-generated ideas and their progress
- 🧠 **Key learnings** documented throughout the project's evolution, including insights from TLDR Tech and Hacker News
- 📊 **Interactive visualizations** of the perpetual motion machine in action
- 🌐 **External learning integration** showing how the AI stays current with tech trends

Visit the live site: **[https://enufacas.github.io/Chained/](https://enufacas.github.io/Chained/)**

## The Perpetual Motion Cycle

```
┌─────────────────────┐
│  External Learning  │ ──► TLDR Tech (2x daily)
│  Sources            │ ──► Hacker News (3x daily)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Learning Database  │ ──► Saves insights & trends
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Smart Idea Gen     │ ──► Generates trend-aware ideas (Daily)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Create Issue       │ ──► Creates GitHub issue
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Copilot Assign     │ ──► Assigns to Copilot (if PAT configured)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Copilot Creates PR │ ──► Copilot implements and opens PR
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Auto Review        │ ──► AI reviews AI code (Every 15min)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Auto Merge         │ ──► Merges to main (No human needed!)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Auto Close Issue   │ ──► Completes lifecycle (Every 30min)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Timeline Update    │ ──► Documents all actions (Every 6h)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Progress Report    │ ──► Analyzes success (Every 12h)
└──────────┬──────────┘
           │
           └──────────────► Cycle continues forever...
                           Getting smarter with each iteration!
```

**This is fully autonomous AND continuously learning** - no human in the loop!

## Human Intervention

The system is **fully autonomous** and requires zero human intervention. However, humans can still:

- **Observe the magic** via GitHub Pages timeline
- **Steer the direction** by creating custom issues with specific ideas
- **Adjust parameters** by modifying workflow schedules
- **Document learnings** by creating issues with the `learning` label
- **Manually trigger** workflows when desired
- **Celebrate** the autonomous achievements!

The beauty is that you can walk away and come back later to see what the AI has built!

## 🛠️ Technologies Used

- **GitHub Actions**: Workflow automation
- **GitHub API**: Fetching repository data
- **GitHub Pages**: Hosting the timeline website
- **GitHub Copilot**: AI-powered development
- **Python**: Learning scripts, data processing, code optimization, and code analysis
- **AST (Abstract Syntax Tree)**: Code pattern analysis and detection
- **HTML/CSS/JavaScript**: Frontend for the timeline
- **Bash scripting**: Workflow logic
- **TLDR Tech API**: Tech news aggregation
- **Hacker News API**: Community trend analysis

---

[← Back to README](../README.md) | [Learning System →](LEARNING.md)
