# 🎛️ Quick Start: Dynamic Orchestration

Get your autonomous AI system running at maximum efficiency in 5 minutes!

## What This Does

Automatically adjusts workflow schedules based on your API usage:
- 🚀 **Aggressive Mode**: 7x more learning and ideas when quota allows
- 🎯 **Normal Mode**: Balanced frequency when on track
- 🛡️ **Conservative Mode**: Reduced frequency when approaching limits

**Result**: Maximum productivity while staying within your 1500 request/month quota!

## Setup (One-Time, 2 minutes)

### 1. Set Repository Variables

Go to: **Settings → Secrets and variables → Actions → Variables**

Click "New repository variable" for each:

| Name | Value | Description |
|------|-------|-------------|
| `COPILOT_MONTHLY_QUOTA` | `1500` | Your Pro+ monthly quota |
| `COPILOT_REQUESTS_USED` | `300` | Current usage (update periodically) |
| `COPILOT_RESET_DAY` | `1` | Day quota resets (1 = first of month) |

### 2. Add PAT Token (Optional but Recommended)

Go to: **Settings → Secrets and variables → Actions → Secrets**

1. Create a PAT at https://github.com/settings/tokens
2. Give it `repo` and `workflow` permissions
3. Add as secret named `COPILOT_PAT`

See [PAT_PERMISSIONS_GUIDE.md](docs/PAT_PERMISSIONS_GUIDE.md) for details.

### 3. Merge the PR

That's it! The system will automatically:
- ✅ Run daily at midnight UTC
- ✅ Check your API usage
- ✅ Adjust workflow schedules
- ✅ Create PRs for changes
- ✅ Alert if approaching limits

## What Happens After Merge

With your current usage (300/1500, 20%), the system will operate in **AGGRESSIVE MODE** 🚀

### Before (Static Schedules)
```
Learning (TLDR):      2x/day   ━━░░░░░░░░░░░░░░░░░░  10%
Learning (HN):        3x/day   ━━━░░░░░░░░░░░░░░░░░  15%
Ideas (General):      1x/day   ━░░░░░░░░░░░░░░░░░░░   5%
Ideas (AI-focused):   None     ░░░░░░░░░░░░░░░░░░░░   0%
Agent Spawner:        8x/day   ━━━━░░░░░░░░░░░░░░░░  20%

Total Activity: ~14x/day
```

### After (Aggressive Mode)
```
Learning (TLDR):      8x/day   ━━━━━━━━░░░░░░░░░░░░  40%
Learning (HN):       12x/day   ━━━━━━━━━━━━░░░░░░░░  60%
Ideas (General):      6x/day   ━━━━━━░░░░░░░░░░░░░░  30%
Ideas (AI-focused):   8x/day   ━━━━━━━━░░░░░░░░░░░░  40% 🆕
Agent Spawner:       12x/day   ━━━━━━━━━━━━░░░░░░░░  60%

Total Activity: ~46x/day (+229%!) 🚀
```

**AI/Autonomy Focus**: 8 ideas per day specifically about autonomy, ML, and intelligent agents!

## Checking Status

### See Current Mode
```bash
cd tools
python3 copilot-usage-tracker.py
```

### View Schedules
```bash
python3 workflow-orchestrator.py --status --repo-root=..
```

### Run Tests
```bash
cd ..
python3 test_dynamic_orchestration.py
```

## Updating Usage

When you want to update your usage count:

```bash
# Via tool
python3 tools/copilot-usage-tracker.py --used 450

# Or via workflow
gh workflow run dynamic-orchestrator.yml -f update_usage=450
```

## Manual Control

### Force a Specific Mode

```bash
# Dry run first (shows what would change)
python3 tools/workflow-orchestrator.py --mode aggressive --dry-run

# Apply changes
python3 tools/workflow-orchestrator.py --mode aggressive

# Or via GitHub Actions
gh workflow run dynamic-orchestrator.yml -f mode=aggressive
```

### Trigger Orchestrator Manually

```bash
gh workflow run dynamic-orchestrator.yml
```

Or via GitHub UI: **Actions → "Orchestrator: Dynamic Scheduling" → Run workflow**

## Understanding the Modes

### 🚀 Aggressive (Under-utilizing)
**When**: Using < 70% of expected quota  
**Frequency**: Every 2-4 hours  
**Best for**: Plenty of quota remaining, want maximum learning/ideas

### 🎯 Normal (On Track)
**When**: Using 70-130% of expected quota  
**Frequency**: 2-3 times daily  
**Best for**: Steady state, balanced usage

### 🛡️ Conservative (Over-utilizing)
**When**: Using > 130% of expected or approaching limit  
**Frequency**: Daily to weekly  
**Best for**: Preserving remaining quota until reset

## Monitoring

### Via GitHub Actions
1. Go to **Actions** tab
2. Select "Orchestrator: Dynamic Scheduling"
3. View recent runs

### Via Issues
Look for issues with label `orchestrator`:
- 🎛️ Schedule update PRs
- ⚠️ Usage warnings

### Via Usage History
```bash
cat tools/analysis/copilot_usage_history.json | jq .
```

## What Gets Managed

These 6 workflows are automatically adjusted:

1. **learn-from-tldr.yml** - TLDR Tech learning
2. **learn-from-hackernews.yml** - Hacker News learning
3. **idea-generator.yml** - General idea generation
4. **ai-idea-spawner.yml** - AI/autonomy ideas (NEW!)
5. **ai-friend-daily.yml** - AI conversations
6. **agent-spawner.yml** - Agent creation

## Safety Features

✅ **Backups**: Workflows backed up before modification  
✅ **Dry-run**: Test changes before applying  
✅ **Validation**: YAML syntax checked  
✅ **Warnings**: Alerts before quota exceeded  
✅ **Conservative**: Automatic fallback if usage high  

## Troubleshooting

### "Workflows not updating"
- Check PAT has `workflow` permission
- Verify secret is named `COPILOT_PAT`
- See [PAT_PERMISSIONS_GUIDE.md](docs/PAT_PERMISSIONS_GUIDE.md)

### "Mode not changing as expected"
- Update usage count: `--used <actual_count>`
- Check time until reset (may affect calculation)
- Force mode if needed: `--mode <mode>`

### "Usage tracking inaccurate"
```bash
# Manually set correct values
python3 tools/copilot-usage-tracker.py \
  --quota 1500 \
  --used <actual_used> \
  --reset-day 1
```

## Next Steps

1. ✅ Merge this PR
2. ✅ Set repository variables
3. ✅ Add PAT token (optional)
4. ✅ Watch the first orchestrator run
5. ✅ Review and merge schedule update PRs
6. ✅ Enjoy 7x more learning and ideas! 🎉

## Resources

- [DYNAMIC_ORCHESTRATION.md](docs/DYNAMIC_ORCHESTRATION.md) - Complete documentation
- [PAT_PERMISSIONS_GUIDE.md](docs/PAT_PERMISSIONS_GUIDE.md) - Token setup
- [IMPLEMENTATION_DYNAMIC_ORCHESTRATION.md](IMPLEMENTATION_DYNAMIC_ORCHESTRATION.md) - Technical details
- [SECURITY_SUMMARY_DYNAMIC_ORCHESTRATION.md](SECURITY_SUMMARY_DYNAMIC_ORCHESTRATION.md) - Security info

## Questions?

Open an issue with label `orchestrator` or check the FAQ sections in the documentation.

---

**Ready to supercharge your autonomous AI?** Merge and watch the magic happen! 🚀
