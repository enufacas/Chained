# Dynamic Workflow Orchestration System

The Dynamic Workflow Orchestration System automatically adjusts GitHub Actions workflow schedules based on API usage, enabling the Chained autonomous system to maximize productivity while staying within quota limits.

## Overview

This system consists of three main components:

1. **Copilot Usage Tracker** - Monitors API usage and calculates burn rate
2. **Workflow Orchestrator** - Dynamically updates workflow schedules
3. **Orchestrator Workflow** - Automates daily schedule adjustments

## How It Works

### 1. Usage Monitoring

The system tracks:
- **Total monthly quota** (default: 1500 for Pro+)
- **Requests used** (tracked via environment variables or history)
- **Burn rate** (requests per day)
- **Projected usage** (estimated usage until reset)

### 2. Mode Determination

Based on usage patterns, the system operates in three modes:

| Mode | When | Learning | Ideas | Agents |
|------|------|----------|-------|--------|
| **🚀 Aggressive** | Under-utilizing quota (< 70%) | Every 2-3 hours | Every 3-4 hours | Every 2 hours |
| **🎯 Normal** | On track (70-130% of expected) | 2-3x daily | Daily + 4-hourly | Every 3 hours |
| **🛡️ Conservative** | Over-utilizing or unsafe (> 130%) | Daily | Weekly | Every 6 hours |

### 3. Schedule Updates

When the orchestrator runs (daily at midnight UTC):
1. Checks current API usage
2. Calculates optimal scheduling mode
3. Updates workflow cron schedules if needed
4. Creates a PR with changes
5. Alerts if approaching quota limits

## Components

### copilot-usage-tracker.py

**Purpose**: Track API usage and provide recommendations

**Usage**:
```bash
# Check current status
python3 tools/copilot-usage-tracker.py

# With custom values
python3 tools/copilot-usage-tracker.py --quota 1500 --used 300 --reset-day 1

# JSON output for automation
python3 tools/copilot-usage-tracker.py --json
```

**Features**:
- Calculates burn rate from usage history
- Projects future usage
- Recommends scheduling mode
- Provides workflow frequency recommendations
- Saves usage history for trend analysis

### workflow-orchestrator.py

**Purpose**: Dynamically update workflow schedules

**Usage**:
```bash
# Show current status (no changes)
python3 tools/workflow-orchestrator.py --status

# Dry run (show what would change)
python3 tools/workflow-orchestrator.py --dry-run

# Update workflows (default: auto-detect mode)
python3 tools/workflow-orchestrator.py

# Force specific mode
python3 tools/workflow-orchestrator.py --mode aggressive
```

**Features**:
- Reads current workflow schedules
- Backs up workflows before modification
- Updates cron expressions
- Validates changes
- Supports dry-run mode

### dynamic-orchestrator.yml

**Purpose**: Automate daily schedule adjustments

**Triggers**:
- **Scheduled**: Daily at midnight UTC
- **Manual**: Via Actions UI or CLI

**Workflow**:
1. Check current API usage
2. Determine recommended mode
3. Update workflow schedules
4. Create PR if changes needed
5. Alert if usage is unsafe

## Setup

### 1. Configure Variables

Set these in your repository:

**Go to**: Settings → Secrets and variables → Actions → Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `COPILOT_MONTHLY_QUOTA` | `1500` | Your monthly quota (Pro+ = 1500) |
| `COPILOT_REQUESTS_USED` | `300` | Current usage (update as needed) |
| `COPILOT_RESET_DAY` | `1` | Day of month when quota resets |

### 2. Add PAT Token (Optional but Recommended)

For enhanced API access:

**Go to**: Settings → Secrets and variables → Actions → Secrets

Add secret named `COPILOT_PAT` with your Personal Access Token.

See [PAT_PERMISSIONS_GUIDE.md](PAT_PERMISSIONS_GUIDE.md) for detailed instructions.

### 3. Enable Workflow

The `dynamic-orchestrator.yml` workflow is already configured and will run automatically daily at midnight UTC.

**Manual trigger**:
```bash
gh workflow run dynamic-orchestrator.yml
```

Or via Actions UI: Actions → "Orchestrator: Dynamic Scheduling" → Run workflow

## Usage Examples

### Check Current Status

```bash
cd tools
python3 copilot-usage-tracker.py
```

Output:
```
======================================================================
🤖 GitHub Copilot Usage Tracker
======================================================================

📊 Usage: [██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20.0%

Total Quota:       1,500 requests
Used:              300 requests
Remaining:         1,200 requests

📅 Reset Date:      2025-12-01
Days Until Reset:  18.9 days

🔥 Burn Rate:       27.0 requests/day
Projected Usage:   808 requests

✅ Status: SAFE - On track or under budget

🚀 Recommended Mode: AGGRESSIVE

📋 Recommended Workflow Frequencies:
  • learn-tldr: 0 */3 * * *
  • learn-hn: 0 */2 * * *
  • idea-generator: 0 */4 * * *
  • ai-idea-spawner: 0 */3 * * *
  • ai-friend: 0 */6 * * *
  • agent-spawner: 0 */2 * * *

======================================================================
```

### View Current Schedules

```bash
cd tools
python3 workflow-orchestrator.py --status --repo-root=..
```

### Update Usage Manually

When you know you've used more requests:

```bash
# Update to 450 used
python3 tools/copilot-usage-tracker.py --used 450

# Or update via workflow
gh workflow run dynamic-orchestrator.yml -f update_usage=450
```

### Force Specific Mode

```bash
# Force aggressive mode (more frequent workflows)
python3 tools/workflow-orchestrator.py --mode aggressive

# Or via workflow
gh workflow run dynamic-orchestrator.yml -f mode=aggressive
```

### Dry Run Before Applying

```bash
# See what would change without making changes
python3 tools/workflow-orchestrator.py --mode aggressive --dry-run
```

## Managed Workflows

The orchestrator manages these workflows:

| Workflow | Purpose | Aggressive | Normal | Conservative |
|----------|---------|------------|--------|--------------|
| `learn-from-tldr.yml` | Learn from TLDR Tech | Every 3h | 2x daily | Daily |
| `learn-from-hackernews.yml` | Learn from Hacker News | Every 2h | 3x daily | 2x daily |
| `idea-generator.yml` | Generate diverse ideas | Every 4h | Daily | 2x weekly |
| `ai-idea-spawner.yml` | Generate AI/autonomy ideas | Every 3h | Every 4h | Daily |
| `ai-friend-daily.yml` | AI conversations | Every 6h | Daily | Weekly |
| `agent-spawner.yml` | Spawn new agents | Every 2h | Every 3h | Every 6h |

## Monitoring

### Via GitHub Actions

1. Go to **Actions** tab
2. Select "Orchestrator: Dynamic Scheduling"
3. View recent runs and summaries

### Via Issues

The orchestrator creates issues for:
- **Schedule updates** - When workflows are adjusted
- **Warning alerts** - When approaching quota limits

Look for label `orchestrator` to find all related issues.

### Via Usage History

```bash
# View usage history
cat tools/analysis/copilot_usage_history.json | jq .
```

The history file tracks:
- Current usage
- Last check timestamp
- Timeline of usage over time

## Advanced Configuration

### Custom Frequencies

Edit `tools/copilot-usage-tracker.py` to customize mode frequencies:

```python
frequencies = {
    'aggressive': {
        'learn-tldr': '0 */3 * * *',      # Customize as needed
        # ...
    },
    # ...
}
```

### Custom Mode Thresholds

Edit `tools/copilot-usage-tracker.py` to adjust mode selection:

```python
# Current logic (can be customized):
if usage_efficiency < 0.7:
    recommended_mode = 'aggressive'
elif usage_efficiency < 1.3:
    recommended_mode = 'normal'
else:
    recommended_mode = 'conservative'
```

### Additional Workflows

To add a workflow to orchestration:

1. Edit `tools/workflow-orchestrator.py`:
```python
MANAGED_WORKFLOWS = {
    # ... existing workflows ...
    'my-workflow': '.github/workflows/my-workflow.yml',
}
```

2. Edit `tools/copilot-usage-tracker.py`:
```python
frequencies = {
    'aggressive': {
        # ... existing frequencies ...
        'my-workflow': '0 */2 * * *',
    },
    # ... other modes ...
}
```

## Troubleshooting

### Issue: Workflows Not Updating

**Cause**: Token lacks permissions

**Solution**: 
1. Check PAT has `workflow` write permission
2. See [PAT_PERMISSIONS_GUIDE.md](PAT_PERMISSIONS_GUIDE.md)

### Issue: Usage Tracking Inaccurate

**Cause**: Manual updates needed

**Solution**:
```bash
# Update usage count
python3 tools/copilot-usage-tracker.py --used <actual_count>
```

### Issue: Mode Not Changing

**Cause**: May be stuck in conservative mode due to projected overage

**Solution**:
1. Wait for quota reset
2. Reduce manual workflow triggers
3. Force different mode if confident:
```bash
python3 tools/workflow-orchestrator.py --mode normal
```

### Issue: Backups Filling Up

**Cause**: Daily backups accumulate

**Solution**:
```bash
# Clean old backups (keep last 10)
cd .github/workflow-backups
ls -t | tail -n +11 | xargs rm -f
```

## Best Practices

### 1. Monitor Regularly

- Check usage weekly: `python3 tools/copilot-usage-tracker.py`
- Review orchestrator PRs before merging
- Watch for warning issues

### 2. Update Usage Counts

If you manually trigger many workflows:
```bash
# Estimate and update
python3 tools/copilot-usage-tracker.py --used <new_count>
```

### 3. Plan for Reset

- Usage resets on day 1 of month (configurable)
- System automatically becomes aggressive after reset
- Consider scheduling intensive work after reset

### 4. Conservative When Needed

If approaching limits:
```bash
# Force conservative mode
gh workflow run dynamic-orchestrator.yml -f mode=conservative
```

### 5. Test Changes

Always dry-run first:
```bash
python3 tools/workflow-orchestrator.py --mode aggressive --dry-run
```

## Integration with AI Idea Spawner

The new `ai-idea-spawner.yml` workflow focuses specifically on AI and autonomy:

- **Aggressive mode**: Spawns AI-focused ideas every 3 hours
- **Normal mode**: Every 4 hours
- **Conservative mode**: Once daily

This ensures the system generates more autonomy-related ideas when quota allows.

## Security Considerations

- Workflows are backed up before modification
- Dry-run mode available for testing
- Conservative mode prevents quota exhaustion
- PAT token stored securely in secrets
- See [PAT_PERMISSIONS_GUIDE.md](PAT_PERMISSIONS_GUIDE.md) for security best practices

## Related Documentation

- [PAT_PERMISSIONS_GUIDE.md](PAT_PERMISSIONS_GUIDE.md) - Token setup and permissions
- [WORKFLOWS.md](WORKFLOWS.md) - All workflow documentation
- [FAQ.md](../FAQ.md) - Common questions
- [COPILOT_SETUP.md](../COPILOT_SETUP.md) - Copilot configuration

## Support

For issues or questions:
1. Check this README
2. Review [PAT_PERMISSIONS_GUIDE.md](PAT_PERMISSIONS_GUIDE.md)
3. Open an issue with label `orchestrator`

## Future Enhancements

Potential improvements:
- Real-time usage tracking via GitHub API
- Machine learning for optimal schedule prediction
- Cost-benefit analysis of workflow execution
- Automatic workflow priority adjustment
- Integration with repository metrics
- Visualization dashboard for usage trends
