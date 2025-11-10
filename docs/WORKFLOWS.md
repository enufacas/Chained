# 🔄 Workflows Documentation

This page documents all GitHub Actions workflows that power the Chained autonomous system.

## Core Workflows

### 1. AI Idea Generator (`idea-generator.yml`)
- **Schedule**: Daily at 9 AM UTC
- **Purpose**: Generates creative AI-focused feature ideas
- **Actions**: Creates GitHub issues automatically
- **Trigger**: Can be triggered manually

### 2. Copilot Assignment Workflow (`copilot-graphql-assign.yml`)
- **Triggers**: When any new issue is created or labeled
- **Purpose**: Automatically assigns unassigned issues to Copilot
- **Actions**: 
  - Discovers and processes ALL open issues
  - Adds tracking labels and comments
  - Assigns to Copilot via API
- **Requirements**: COPILOT_PAT secret for full automation
- **Manual**: Can be manually triggered with optional issue number

### 3. Auto Label Copilot PRs (`auto-label-copilot-prs.yml`)
- **Triggers**: 
  - Immediately when PRs are opened/updated (via events)
  - Every 10 minutes on scheduled timer
- **Purpose**: Labels PRs created by Copilot with the "copilot" label
- **Actions**: Performs round-up of all open Copilot PRs each run
- **Manual**: Can be triggered via workflow_dispatch
- **Notes**: Hybrid approach ensures immediate response + regular cleanup

### 4. Auto Review and Merge (`auto-review-merge.yml`)
- **Schedule**: Every 15 minutes
- **Purpose**: Reviews and merges PRs created by Copilot
- **Actions**: 
  - AI reviews AI code
  - Automatically approves and merges PRs
  - Closes associated issues when PRs are merged
- **Notes**: No human approval required

### 5. Timeline Updater (`timeline-updater.yml`)
- **Schedule**: Every 6 hours
- **Purpose**: Updates timeline data for GitHub Pages
- **Actions**: 
  - Fetches all repository activity
  - Documents autonomous actions
  - Updates GitHub Pages data files

### 6. Progress Tracker (`progress-tracker.yml`)
- **Schedule**: Every 12 hours
- **Purpose**: Analyzes repository progress and statistics
- **Actions**: 
  - Generates progress reports
  - Tracks autonomous success rates
  - Creates progress report issues

## Learning Workflows

### 7. Learning from TLDR Tech (`learn-from-tldr.yml`)
- **Schedule**: Twice daily (8 AM, 8 PM UTC)
- **Purpose**: Fetches latest tech news and trends
- **Actions**: 
  - Extracts insights about AI, DevOps, and programming
  - Saves learnings to `learnings/` directory
  - Influences future idea generation

### 8. Learning from Hacker News (`learn-from-hackernews.yml`)
- **Schedule**: Three times daily (7 AM, 1 PM, 7 PM UTC)
- **Purpose**: Analyzes trending technical discussions
- **Actions**: 
  - Categorizes topics (AI/ML, Security, Performance, etc.)
  - Generates ideas based on community trends
  - Saves learnings for future reference

### 9. AI Friend Daily (`ai-friend-daily.yml`)
- **Schedule**: Daily at 9 AM UTC (after learning, before idea generation)
- **Purpose**: Talks to different AI models about the project
- **Actions**: 
  - Uses free AI APIs (Puter.js) requiring no authentication
  - Shares project information and recent learnings
  - Asks for advice and suggestions
  - Saves conversations to `ai-conversations/` directory
  - Creates GitHub issues documenting conversations
  - Updates AI Friends page on GitHub Pages
- **Models**: GPT-4, Claude, Gemini, Llama (400+ models via Puter.js)
- **View**: [AI Friends Page](https://enufacas.github.io/Chained/ai-friends.html)

### 10. Smart Idea Generator (`smart-idea-generator.yml`)
- **Schedule**: Daily at 10 AM UTC (after learning workflows)
- **Purpose**: Generates ideas informed by external learnings
- **Actions**: 
  - Adapts to trending technologies and patterns
  - Creates enhanced issues with learning context
  - Uses learnings from TLDR, Hacker News, and AI Friends

## System Management Workflows

### 11. System Kickoff (`system-kickoff.yml`)
- **Triggers**: Manual or automatic
- **Purpose**: Initialize and validate the autonomous system
- **Actions**: 
  - Validates system configuration
  - Creates required labels
  - Initializes directories
  - Triggers initial workflows
  - Creates kickoff success issue

### 12. Auto Kickoff on First Run (`auto-kickoff.yml`)
- **Triggers**: Automatically on merge to main
- **Purpose**: Ensures one-time system initialization
- **Actions**: 
  - Detects if system already kicked off
  - Triggers kickoff workflow if needed
  - Runs only once per repository

### 13. Workflow Monitor (`workflow-monitor.yml`)
- **Schedule**: Periodically checks workflow health
- **Purpose**: Monitors workflow execution and schedules
- **Actions**: 
  - Verifies workflows are running on schedule
  - Creates issues for failed or late workflows
  - Provides system health reports

## Micro Project Workflows

### 14. Code Golf Optimizer (`code-golf-optimizer.yml`)
- **Schedule**: Weekly on Mondays at 10 AM UTC
- **Purpose**: Optimizes code for minimal character count
- **Actions**: 
  - Supports Python, JavaScript, and Bash
  - Generates optimization reports with metrics
  - Can be triggered manually for specific files

### 15. Self-Improving Code Analyzer (`code-analyzer.yml`)
- **Triggers**: Automatically on every merge to main
- **Purpose**: Analyzes code quality and learns from outcomes
- **Actions**: 
  - Identifies code patterns (good and bad)
  - Tracks pattern correlations over time
  - Posts analysis reports on PRs
  - Creates issues for quality problems
  - Updates learning database

### 16. Pattern Matcher (`pattern-matcher.yml`)
- **Triggers**: As needed by other workflows
- **Purpose**: Flexible pattern matching for code analysis
- **Actions**: 
  - Detects code patterns
  - Supports documentation generation
  - Extensible pattern library

## Workflow Chain

The workflows form an autonomous cycle:

```
External Learning (TLDR, HN, AI Friends)
    ↓
Learning Database
    ↓
Smart Idea Generator
    ↓
Create Issue
    ↓
Copilot Assignment
    ↓
Copilot Creates PR
    ↓
Auto Label PR
    ↓
Auto Review & Merge
    ↓
Code Analyzer (on merge)
    ↓
Close Issue
    ↓
Timeline Update
    ↓
Progress Report
    ↓
Cycle continues...
```

## Customizing Workflows

All workflows are in `.github/workflows/` and can be customized:

- **Adjust scheduling**: Modify the `cron` expressions in each workflow
- **Add more ideas**: Edit the `ideas` array in idea generators
- **Change labels**: Update label names in workflow files
- **Modify permissions**: Adjust the `permissions` section as needed

## Manual Triggers

All workflows support manual triggering via GitHub's Actions tab:

1. Go to **Actions** in your repository
2. Select the workflow you want to run
3. Click **Run workflow**
4. Fill in any required inputs

## Monitoring Workflows

### Via Scripts

```bash
# Check workflow schedules
./verify-schedules.sh

# Evaluate workflow state
./evaluate-workflows.sh

# Check system status
./check-status.sh
```

### Via GitHub

- Check the **Actions** tab for recent runs
- Look for **workflow-monitor** issues for problems
- Review workflow run logs for details

## Troubleshooting

### Workflow Not Running

1. Check if repository has been inactive for 60 days (workflows auto-disable)
2. Verify cron syntax is correct
3. Check workflow permissions
4. Review recent workflow runs for errors

### Workflow Failing

1. Check workflow run logs in Actions tab
2. Verify all required secrets are set (e.g., COPILOT_PAT)
3. Check for API rate limits
4. Review recent changes to workflow files

### Issues Not Being Processed

1. Verify COPILOT_PAT secret is configured
2. Check Copilot Assignment workflow status
3. Verify issue has correct labels
4. Check workflow permissions

---

**Back to [Main README](../README.md) | [Micro Projects](./MICRO_PROJECTS.md) | [Learning System](./LEARNING_SYSTEM.md)**
