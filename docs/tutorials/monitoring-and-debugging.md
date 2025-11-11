# Tutorial: Monitoring and Debugging Your Chained System

Welcome! In this tutorial, you'll learn how to effectively monitor and debug your Chained autonomous system. By the end, you'll know how to track system health, diagnose issues, and optimize performance.

## What You'll Learn

- Essential monitoring tools and techniques
- How to read and interpret workflow logs
- Debugging common issues
- Understanding system metrics
- Using built-in health checks
- Optimizing workflow performance

## Prerequisites

- A running Chained instance
- Basic familiarity with GitHub Actions
- Understanding of the autonomous workflow (see [Understanding the Autonomous Workflow](./understanding-autonomous-workflow.md))

## Time Required

⏱️ **25-30 minutes**

---

## The Monitoring Philosophy

**Key Principle**: An autonomous system must be self-healing and observable.

Chained includes:
- 🔍 **Built-in monitoring** - System Monitor workflow
- 📊 **Metrics visualization** - GitHub Pages dashboard
- 🚨 **Automatic alerts** - Issues created for problems
- 📝 **Comprehensive logging** - All workflows log their actions
- 🛠️ **Diagnostic tools** - Shell scripts for quick checks

---

## Part 1: Essential Monitoring Tools

### Tool 1: Status Check Script

The fastest way to check system health.

**Run it**:
```bash
cd /path/to/Chained
./check-status.sh
```

**What it shows**:
```
=== Chained System Status ===

Recent Workflow Runs:
✓ System Monitor - Success (5 minutes ago)
✓ Auto Review Merge - Success (12 minutes ago)
✓ Copilot Assignment - Success (1 hour ago)
✗ Learn from TLDR - Failed (2 hours ago)

Issues:
- Open: 8
- Closed: 156
- AI Generated: 142
- With copilot label: 3

Pull Requests:
- Open: 2
- Merged: 98
- Success rate: 98%

Learning Files:
- TLDR: 47 files
- Hacker News: 62 files
- AI Conversations: 15 files

=== System Health: GOOD ===
```

**Interpreting results**:
- ✓ Green checks = workflows running smoothly
- ✗ Red crosses = need investigation
- High success rate = healthy system
- Growing learning files = system is learning

### Tool 2: Workflow Evaluation Script

More comprehensive analysis of all workflows.

**Run it**:
```bash
./evaluate-workflows.sh
```

**What it checks**:
- ✅ All workflow files exist
- ✅ Triggers are configured correctly
- ✅ Schedules are valid
- ✅ Permissions are set properly
- ✅ Dependencies are met
- ✅ Execution chain is complete

**Sample output**:
```
=== Workflow Evaluation ===

✓ Core Workflows (4/4)
  ✓ idea-generator.yml
  ✓ copilot-graphql-assign.yml
  ✓ auto-label-copilot-prs.yml
  ✓ auto-review-merge.yml

✓ Learning Workflows (3/3)
  ✓ learn-from-tldr.yml
  ✓ learn-from-hackernews.yml
  ✓ ai-friend-daily.yml

⚠ Schedule Warnings:
  - agent-spawner.yml: Runs every 3 hours (high frequency)
  
✓ Execution Chain: Complete
  Ideas → Assignment → Implementation → Review → Merge
  
=== Overall: HEALTHY ===
```

### Tool 3: GitHub Actions Dashboard

Real-time view of all workflow runs.

**Access it**:
1. Go to your repository
2. Click **Actions** tab
3. See all workflows in the left sidebar

**What to look for**:
- 🟢 **Green checks**: Successful runs
- 🔴 **Red X's**: Failed runs
- 🟡 **Yellow dots**: In progress
- ⚪ **Gray circles**: Queued

**Pro tip**: Click on any workflow to see:
- Run history
- Success/failure rate
- Execution times
- Recent runs

### Tool 4: GitHub Pages Dashboard

Visual representation of system activity.

**Access it**: `https://<your-username>.github.io/Chained/`

**Sections**:

1. **Statistics Panel**:
   - Total commits
   - Issues created
   - PRs merged
   - Success rate
   - Agent count

2. **Timeline**:
   - Chronological view of all autonomous actions
   - Filter by type (issues, PRs, merges)
   - See learning activities

3. **Agent Ecosystem**:
   - Agent performance scores
   - Active vs eliminated agents
   - Hall of Fame members
   - System Lead

4. **AI Knowledge Graph**:
   - Visual network of learnings
   - Topic connections
   - Trend analysis

### Tool 5: System Monitor Workflow

Automatic health monitoring.

**Schedule**: Every hour  
**Purpose**: Detect and report issues automatically

**What it monitors**:
- Workflow execution status
- API rate limits
- File system health
- Configuration validity
- Critical errors

**When problems detected**:
- Creates issue with `workflow-monitor` label
- Includes diagnostic information
- Suggests fixes
- Tags for priority

**Check recent runs**:
```bash
gh run list --workflow=system-monitor.yml --limit 5
```

---

## Part 2: Reading Workflow Logs

Understanding logs is crucial for debugging.

### Accessing Logs

**Via GitHub Web UI**:
1. Actions tab → Select workflow
2. Click on a run
3. Click on a job name
4. Expand steps to see logs

**Via GitHub CLI**:
```bash
# List recent runs
gh run list --limit 10

# View specific run
gh run view 1234567890

# Download logs
gh run download 1234567890
```

### Understanding Log Structure

Workflow logs are organized hierarchically:

```
Workflow Run
├── Job: build
│   ├── Step: Checkout code
│   ├── Step: Setup Python
│   ├── Step: Run script
│   └── Step: Upload results
└── Job: test
    ├── Step: Checkout code
    └── Step: Run tests
```

### Key Log Indicators

**Success indicators**:
```
✓ Step completed successfully
✓ All checks passed
✓ Issue created: #123
✓ PR merged successfully
```

**Warning indicators**:
```
⚠ Rate limit approaching (4500/5000)
⚠ No issues to process
⚠ Workflow skipped - not scheduled
```

**Error indicators**:
```
✗ Failed to fetch data
✗ API call returned 404
✗ Permission denied
✗ Workflow failed
```

### Example: Debugging Failed Copilot Assignment

**Symptoms**: Issues aren't being assigned to Copilot

**Step 1**: Check workflow logs
```bash
gh run list --workflow=copilot-graphql-assign.yml --limit 1
gh run view <run-id>
```

**Step 2**: Look for error messages
```
Error: GraphQL query failed
{
  "message": "Bad credentials",
  "documentation_url": "https://docs.github.com/..."
}
```

**Step 3**: Identify the problem
- "Bad credentials" = PAT issue
- Missing or expired COPILOT_PAT secret

**Step 4**: Fix it
1. Verify secret exists: Settings → Secrets → Actions
2. If missing: Add COPILOT_PAT secret
3. If expired: Generate new PAT and update secret

**Step 5**: Test
```bash
gh workflow run copilot-graphql-assign.yml
```

---

## Part 3: Common Issues and Solutions

### Issue 1: Workflows Not Running

**Symptoms**:
- No recent workflow runs
- Actions tab shows no activity
- System seems frozen

**Diagnostic steps**:
```bash
# Check if workflows are enabled
gh workflow list

# Check recent runs
gh run list --limit 10
```

**Common causes**:

1. **Actions disabled in fork**
   - Solution: Actions tab → Enable workflows

2. **Workflow permissions**
   - Check: Settings → Actions → General → Workflow permissions
   - Should be: "Read and write permissions"

3. **Rate limit exceeded**
   - Check logs for: "API rate limit exceeded"
   - Solution: Wait 1 hour or upgrade to GitHub Pro

4. **Scheduled workflows**
   - Remember: Workflows run on schedule (UTC times)
   - Use manual trigger to test immediately

### Issue 2: Copilot Not Creating PRs

**Symptoms**:
- Issues assigned to Copilot
- No PRs appear
- Label `copilot-assigned` present

**Diagnostic steps**:

1. **Check issue assignment**:
   - Is @copilot actually assigned?
   - Check issue page assignees section

2. **Verify PAT**:
   ```bash
   # This will show if secret exists (not the value)
   gh secret list
   ```

3. **Check Copilot subscription**:
   - Settings → Copilot → Verify active subscription

4. **Review issue quality**:
   - Is the issue description clear?
   - Does it have enough context?
   - Copilot needs well-defined requirements

**Solutions**:

- **Missing PAT**: Add COPILOT_PAT secret (see [COPILOT_SETUP.md](../../COPILOT_SETUP.md))
- **Expired PAT**: Generate new token and update secret
- **Vague issue**: Edit issue with clearer requirements
- **Wrong scope**: PAT needs `repo` scope

### Issue 3: Auto-Merge Not Working

**Symptoms**:
- PRs approved but not merging
- Status: "Auto-merge enabled" but nothing happens
- PRs stuck in "open" state

**Diagnostic steps**:

1. **Check PR labels**:
   - Must have `copilot` label
   - Check: Labels section on PR

2. **Check status checks**:
   - All checks must pass
   - Look for: Red X's next to checks

3. **Check branch protection**:
   - Settings → Branches → main
   - Verify: "Allow auto-merge" enabled
   - Verify: Required approvals = 0

4. **Check PR author**:
   - Auto-merge only works for repository owner PRs
   - Security feature to prevent malicious merges

**Solutions**:

- **Missing label**: Run auto-label workflow manually
- **Failing checks**: Fix code issues, push updates
- **Branch protection**: Adjust settings (see [Setup Tutorial](./setting-up-your-first-instance.md#step-6-configure-branch-protection))
- **External PR**: Requires manual review (security by design)

### Issue 4: Learning Workflows Failing

**Symptoms**:
- No learning files in `learnings/` directory
- TLDR or Hacker News workflows show errors
- AI friend conversations not appearing

**Diagnostic steps**:

1. **Check workflow logs**:
   ```bash
   gh run list --workflow=learn-from-tldr.yml
   gh run view <run-id>
   ```

2. **Look for API errors**:
   - "Failed to fetch": Network issue
   - "404 Not Found": Endpoint changed
   - "Rate limit": Too many requests

3. **Check file permissions**:
   ```bash
   # Verify directories exist and are writable
   ls -la learnings/
   ls -la docs/ai-conversations/
   ```

**Solutions**:

- **Network issues**: Temporary, will retry next run
- **API changes**: Update workflow to use new endpoint
- **Rate limits**: Space out workflow schedules
- **Permission errors**: Check workflow permissions in repo settings

### Issue 5: GitHub Pages Not Updating

**Symptoms**:
- Timeline not showing recent events
- Statistics seem outdated
- Agent data not refreshing

**Diagnostic steps**:

1. **Check Pages deployment**:
   - Actions → "pages-build-deployment"
   - Should see successful runs

2. **Check timeline updater**:
   ```bash
   gh run list --workflow=timeline-updater.yml
   ```

3. **Verify data files**:
   ```bash
   ls -la docs/data/
   ```

4. **Check Pages configuration**:
   - Settings → Pages
   - Should be: Branch `main`, Folder `/docs`

**Solutions**:

- **No deployments**: Enable GitHub Pages (Settings → Pages)
- **Data not updating**: Run timeline-updater manually
- **Stale cache**: Hard refresh browser (Ctrl+Shift+R)
- **File errors**: Check workflow logs for write failures

---

## Part 4: Performance Optimization

### Optimizing Workflow Schedules

**Current schedules** (see [WORKFLOWS.md](../WORKFLOWS.md)):

```yaml
# High frequency (every 10-15 min)
- auto-label-copilot-prs.yml: */10 * * * *
- auto-review-merge.yml: */15 * * * *

# Medium frequency (every 1-3 hours)
- copilot-graphql-assign.yml: 0 * * * *
- agent-spawner.yml: 0 */3 * * *
- goal-progress-checker.yml: 0 */3 * * *

# Daily
- daily-goal-generator.yml: 0 6 * * *
- learn-from-tldr.yml: 0 8,20 * * *
- smart-idea-generator.yml: 0 10 * * *
```

**Optimization tips**:

1. **Reduce high-frequency workflows** if hitting rate limits:
   ```yaml
   # Before
   schedule:
     - cron: '*/10 * * * *'  # Every 10 minutes
   
   # After
   schedule:
     - cron: '*/20 * * * *'  # Every 20 minutes
   ```

2. **Batch operations** to reduce API calls:
   - Process multiple items per run
   - Use GraphQL instead of REST when possible

3. **Add workflow conditions**:
   ```yaml
   if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
   ```

4. **Cache dependencies**:
   ```yaml
   - uses: actions/cache@v3
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
   ```

### Monitoring API Rate Limits

**Check current usage**:
```bash
# Via API
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit

# Via workflow (add to system-monitor.yml)
- name: Check rate limit
  run: |
    RATE_LIMIT=$(gh api rate_limit --jq '.rate.remaining')
    echo "Remaining API calls: $RATE_LIMIT"
    if [ $RATE_LIMIT -lt 1000 ]; then
      echo "::warning::Rate limit low: $RATE_LIMIT remaining"
    fi
```

**Rate limit tiers**:
- **Free tier**: 5,000 requests/hour
- **GitHub Pro**: 5,000 requests/hour (same, but better actions minutes)
- **Authenticated**: 5,000/hour per PAT

**Strategies to avoid limits**:
1. Space out workflows
2. Use conditional execution
3. Batch operations
4. Cache results
5. Use GraphQL (counts as 1 call vs multiple REST calls)

### Reducing Workflow Minutes

**GitHub Actions free tier**: 2,000 minutes/month for public repos

**Current usage** (approximate):
```
Per day:
- Core workflows: ~20 minutes
- Learning workflows: ~15 minutes
- Agent system: ~30 minutes
- Monitoring: ~10 minutes
Total: ~75 minutes/day = ~2,250 minutes/month
```

**Optimization strategies**:

1. **Optimize Python setup** (saves ~30 seconds per run):
   ```yaml
   - uses: actions/setup-python@v4
     with:
       python-version: '3.11'
       cache: 'pip'  # Cache dependencies
   ```

2. **Use matrix strategies** for parallel execution:
   ```yaml
   strategy:
     matrix:
       task: [tldr, hackernews, ai-friend]
   ```

3. **Skip unnecessary steps**:
   ```yaml
   - name: Process data
     if: steps.check.outputs.has_data == 'true'
     run: ./process.sh
   ```

4. **Reduce checkout depth**:
   ```yaml
   - uses: actions/checkout@v4
     with:
       fetch-depth: 1  # Only latest commit
   ```

---

## Part 5: Advanced Debugging Techniques

### Technique 1: Dry Run Testing

Test workflows without side effects.

**Add dry-run mode**:
```yaml
name: Copilot Assignment (Dry Run)
on:
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run mode (no actual assignment)'
        required: false
        default: 'true'

jobs:
  assign:
    runs-on: ubuntu-latest
    steps:
      - name: Process assignments
        run: |
          if [ "${{ inputs.dry_run }}" == "true" ]; then
            echo "DRY RUN: Would assign issue #123"
          else
            # Actual assignment code
          fi
```

### Technique 2: Verbose Logging

Add detailed logging to workflows.

```yaml
- name: Debug - Show environment
  run: |
    echo "::group::Environment Variables"
    env | sort
    echo "::endgroup::"
    
- name: Debug - Show GitHub context
  run: |
    echo "::group::GitHub Context"
    echo '${{ toJSON(github) }}'
    echo "::endgroup::"
```

### Technique 3: Step Outputs

Capture and display step outputs.

```yaml
- name: Process data
  id: process
  run: |
    RESULT=$(./process.sh)
    echo "result=$RESULT" >> $GITHUB_OUTPUT
    
- name: Display result
  run: |
    echo "Processing result: ${{ steps.process.outputs.result }}"
```

### Technique 4: Conditional Notifications

Get notified only for failures.

```yaml
- name: Notify on failure
  if: failure()
  run: |
    gh issue create \
      --title "Workflow Failed: ${{ github.workflow }}" \
      --body "Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" \
      --label "workflow-monitor"
```

### Technique 5: Local Testing

Test workflow scripts locally before committing.

```bash
# Extract workflow logic to separate script
cat > .github/scripts/assign-copilot.sh << 'EOF'
#!/bin/bash
set -e

# Your workflow logic here
echo "Processing assignments..."
EOF

chmod +x .github/scripts/assign-copilot.sh

# Test locally
./.github/scripts/assign-copilot.sh

# Then use in workflow
# - name: Assign Copilot
#   run: ./.github/scripts/assign-copilot.sh
```

---

## Part 6: Monitoring Best Practices

### Practice 1: Regular Health Checks

**Daily routine**:
```bash
# Morning check
./check-status.sh

# Check for failures
gh run list --limit 20 | grep -i failed

# Review new issues
gh issue list --label workflow-monitor
```

### Practice 2: Set Up Alerts

**Create monitoring issue template**:
```markdown
---
name: Monitoring Alert
about: System health alert
labels: workflow-monitor
---

## Alert Details
- Workflow: [name]
- Status: [failed/warning]
- Time: [timestamp]
- Run: [link]

## Error Message
```
[error]
```

## Investigation Steps
- [ ] Check workflow logs
- [ ] Review recent changes
- [ ] Test manually
- [ ] Fix and verify
```

### Practice 3: Track Key Metrics

**Monitor these metrics weekly**:

1. **Success Rate**: % of PRs merged successfully
   - Target: > 90%
   - Calculate: merged / (merged + closed without merge)

2. **Cycle Time**: Time from issue creation to PR merge
   - Target: < 24 hours
   - Measure: timestamp(merge) - timestamp(issue)

3. **Learning Growth**: New learning files per week
   - Target: > 20 files/week
   - Count: `ls learnings/*/* | wc -l`

4. **Agent Performance**: Average agent score
   - Target: > 60%
   - Check: GitHub Pages agent dashboard

5. **Workflow Reliability**: % of successful workflow runs
   - Target: > 95%
   - Check: Actions tab statistics

### Practice 4: Document Issues

When you encounter and fix an issue:

1. **Create issue with solution**:
   ```bash
   gh issue create \
     --title "Issue: [problem]" \
     --body "**Problem**: [description]
   
   **Solution**: [fix]
   
   **Prevention**: [how to avoid]" \
     --label "learning"
   ```

2. **Add to troubleshooting guide**:
   Edit `docs/TROUBLESHOOTING.md` with new entry

3. **Update documentation**:
   If setup issue, update relevant tutorial

### Practice 5: Periodic Reviews

**Monthly review checklist**:
- [ ] Review all workflow logs for recurring warnings
- [ ] Check API rate limit patterns
- [ ] Analyze workflow execution times
- [ ] Review agent performance trends
- [ ] Update workflow schedules if needed
- [ ] Clean up old branches and data
- [ ] Update dependencies
- [ ] Review and close stale issues

---

## Part 7: Diagnostic Commands Reference

Quick reference for common diagnostic commands.

### GitHub CLI Commands

```bash
# Workflow status
gh run list --limit 10
gh run list --workflow=copilot-graphql-assign.yml
gh run view <run-id>
gh run watch <run-id>

# Issue management
gh issue list --label ai-generated
gh issue list --state open
gh issue view <issue-number>

# PR management
gh pr list
gh pr list --label copilot
gh pr view <pr-number>
gh pr checks <pr-number>

# Repository info
gh repo view
gh api repos/:owner/:repo
gh api rate_limit

# Workflow management
gh workflow list
gh workflow view <workflow-file>
gh workflow run <workflow-file>
gh workflow enable <workflow-file>
```

### Git Commands

```bash
# Repository status
git status
git log --oneline --graph --all --decorate -20
git branch -a
git remote -v

# Check recent activity
git log --since="1 day ago" --oneline
git log --author="copilot" --oneline
git log --grep="auto-merge" --oneline

# File history
git log --follow -- docs/data/timeline.json
git blame docs/INDEX.md
```

### Shell Commands

```bash
# Check structure
tree -L 2 -d

# Count files
find learnings -type f | wc -l
find docs/ai-conversations -type f | wc -l

# Check file sizes
du -sh learnings/*
du -sh docs/data/*

# Search for patterns
grep -r "ERROR" .github/workflows/
grep -r "TODO" docs/

# Check timestamps
ls -lt docs/data/ | head
stat docs/data/timeline.json
```

---

## Conclusion

You now have a comprehensive toolkit for monitoring and debugging your Chained system:

✅ **Monitoring tools** - Scripts, dashboards, and workflows  
✅ **Log interpretation** - Understanding workflow outputs  
✅ **Issue debugging** - Common problems and solutions  
✅ **Performance optimization** - Improving efficiency  
✅ **Advanced techniques** - Dry runs, verbose logging, local testing  
✅ **Best practices** - Regular checks and documentation  
✅ **Command reference** - Quick diagnostic commands  

**Remember**: An autonomous system should be largely self-managing, but human oversight ensures it runs smoothly and learns from issues.

---

## Next Steps

- **Optimize your setup**: Apply performance tips from Part 4
- **Set up monitoring routine**: Implement best practices from Part 6
- **Contribute improvements**: Share your monitoring insights
- **Explore advanced features**: Check [ARCHITECTURE.md](../ARCHITECTURE.md)

---

## Additional Resources

- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Comprehensive problem-solving guide
- [MONITORING.md](../MONITORING.md) - Detailed monitoring documentation
- [WORKFLOWS.md](../WORKFLOWS.md) - Complete workflow reference
- [GitHub Actions Documentation](https://docs.github.com/en/actions) - Official GitHub docs

**Happy monitoring!** 📊🔍
