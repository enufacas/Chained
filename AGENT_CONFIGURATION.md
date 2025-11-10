# ⚙️ Agent System Configuration Guide

## 📋 Summary: What You Need to Configure

**Good news!** The agent system is designed to work **out of the box** with minimal configuration. However, there are a few optional settings you may want to configure based on your needs.

## ✅ What's Already Configured (No Action Needed)

The following are automatically set up by this PR:

- ✅ **Workflows**: All 3 agent workflows are ready to run
- ✅ **Permissions**: Workflows have necessary permissions (contents, issues, PRs)
- ✅ **Schedules**: Agent spawner runs every 3 hours, evaluator runs daily
- ✅ **Directory Structure**: All required directories created
- ✅ **Registry**: Initial agent database initialized
- ✅ **GitHub Pages**: Agent visualization ready (once Pages is enabled)

## 🔔 Issue Notifications & Subscriptions

### Current Behavior

**Agent Announcements**:
- When an agent spawns, it creates an issue with label `agent-system,announcement`
- When evaluation completes, it creates an issue with label `agent-system,evaluation`
- Everyone who watches the repository gets notifications

### Who Gets Notified?

By default, GitHub notifies:
- **Repository watchers**: Anyone watching the repo gets all issue notifications
- **Issue participants**: Anyone who comments on an agent issue
- **Mentioned users**: Anyone @mentioned in issue/PR descriptions

### Notification Configuration Options

#### Option 1: Watch Repository (Recommended for Active Users)

**To get ALL agent notifications**:
1. Go to repository main page
2. Click "Watch" (top right)
3. Select "All Activity"

**Result**: You'll be notified of:
- Every agent spawn
- Every evaluation
- Every PR from agents
- All issue updates

#### Option 2: Watch Specific Labels

**To filter agent notifications**:
1. Go to repository main page
2. Click "Watch" → "Custom"
3. Enable "Issues" and "Pull requests"
4. Use GitHub notification filters to filter by labels:
   - `agent-system` - All agent activity
   - `agent-system,announcement` - Just new agent spawns
   - `agent-system,evaluation` - Just evaluations

#### Option 3: Unsubscribe (For Less Active Users)

**If you want minimal noise**:
1. Click "Watch" → "Ignore"
2. You can still manually check the agents page
3. Visit: https://enufacas.github.io/Chained/agents.html anytime

### Customize Labels (Optional)

If you want different labels for agent issues, edit the workflows:

**File**: `.github/workflows/agent-spawner.yml`

Find this line (appears twice - in PR creation and issue creation):
```yaml
--label "agent-system,announcement"
```

Change to your preferred labels:
```yaml
--label "ai-agent,bot-spawn"
```

**File**: `.github/workflows/agent-evaluator.yml`

Find this line:
```yaml
--label "agent-system,evaluation"
```

Change to your preferred label.

## 🎛️ Agent System Parameters

### Default Configuration

Located in `agents/registry.json`:

```json
{
  "config": {
    "spawn_interval_hours": 3,        // How often agents spawn
    "max_active_agents": 10,          // Max concurrent agents
    "elimination_threshold": 0.3,     // Score to avoid elimination (30%)
    "promotion_threshold": 0.85,      // Score for Hall of Fame (85%)
    "metrics_weight": {
      "code_quality": 0.3,            // 30% weight
      "issue_resolution": 0.25,       // 25% weight
      "pr_success": 0.25,             // 25% weight
      "peer_review": 0.2              // 20% weight
    }
  }
}
```

### To Change Parameters

**Option A: Edit JSON Directly**
```bash
# Edit the registry file
vi agents/registry.json

# Commit changes
git add agents/registry.json
git commit -m "Adjust agent parameters"
git push
```

**Option B: Via PR**
1. Edit `agents/registry.json` in GitHub UI
2. Create PR with changes
3. Merge when ready

### Common Adjustments

**More Frequent Spawning**:
```json
"spawn_interval_hours": 1,  // Spawn every hour instead of 3
```

**Fewer Active Agents**:
```json
"max_active_agents": 5,  // Reduce from 10 to 5
```

**Easier Survival**:
```json
"elimination_threshold": 0.2,  // Lower threshold (20% instead of 30%)
```

**Harder to Reach Hall of Fame**:
```json
"promotion_threshold": 0.9,  // Raise threshold (90% instead of 85%)
```

## 🔐 Required Secrets

### GITHUB_TOKEN (Already Available)

The workflows use `secrets.GITHUB_TOKEN` which is **automatically provided** by GitHub Actions. No configuration needed!

This token has permissions for:
- ✅ Creating issues
- ✅ Creating PRs
- ✅ Committing to branches
- ✅ Reading repository data

### COPILOT_PAT (Required for Agent Tasks)

For agents to automatically receive work assignments via GitHub Copilot:

1. Create Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Create token with `repo` scope
   
2. Add as repository secret:
   - Go to repository Settings → Secrets → Actions
   - Click "New repository secret"
   - Name: `COPILOT_PAT`
   - Value: Your token

**⚠️ Important**: The agent system now uses this to automatically assign work to Copilot when agents spawn. Without this:
- Agents will still spawn
- Work issues will be created
- But issues won't be automatically assigned to Copilot
- You'll need to manually assign Copilot or a developer to complete agent tasks

**With COPILOT_PAT configured:**
- ✅ Each agent automatically gets a work issue
- ✅ Issue is assigned to GitHub Copilot
- ✅ Copilot implements the solution
- ✅ Agent receives credit for the work
- ✅ Fully autonomous operation

## 🌐 GitHub Pages Configuration

### Enable GitHub Pages (If Not Already)

1. Go to repository **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/docs**
3. Click **Save**

**Result**: Agent dashboard will be live at:
```
https://enufacas.github.io/Chained/agents.html
```

### First-Time Setup

After merging this PR:
1. Wait for GitHub Pages to deploy (2-5 minutes)
2. Visit the agents page
3. You'll see "Agent System Initializing..." until first agent spawns

## 🏷️ Labels Configuration

### Required Labels

The agent system uses these labels (auto-created by workflows):
- `agent-system` - General agent activity
- `agent-work` - Work assigned to agents (NEW)
- `announcement` - Agent spawn announcements
- `evaluation` - Daily evaluation reports
- `automated` - Auto-generated content
- `copilot` - For auto-merge compatibility

**Note**: The workflows automatically create these labels if they don't exist, so no manual action is required.

### Creating Labels Manually (Optional)

If you want to pre-create labels:

```bash
# Using GitHub CLI
gh label create "agent-system" --color "7057ff" --description "Agent ecosystem activity"
gh label create "agent-work" --color "0e8a16" --description "Work assigned to agents"
gh label create "announcement" --color "0075ca" --description "Agent announcements"
gh label create "evaluation" --color "e4e669" --description "Agent evaluations"
```

Or via GitHub UI:
1. Go to Issues → Labels
2. Click "New label"
3. Add the labels above

**Note**: Workflows will auto-create labels if they don't exist, so this is optional.

## ⏰ Schedule Configuration

### Current Schedules

**Agent Spawner**:
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

**Agent Evaluator**:
```yaml
schedule:
  - cron: '0 0 * * *'    # Daily at midnight UTC
```

### To Change Schedules

Edit the workflow files:

**File**: `.github/workflows/agent-spawner.yml`

Change cron expression:
```yaml
# Examples:
- cron: '0 */1 * * *'   # Every hour
- cron: '0 */6 * * *'   # Every 6 hours
- cron: '0 9,15,21 * * *'  # 3 times per day (9am, 3pm, 9pm UTC)
```

**File**: `.github/workflows/agent-evaluator.yml`

Change evaluation frequency:
```yaml
# Examples:
- cron: '0 */12 * * *'  # Every 12 hours
- cron: '0 0 * * 1'     # Weekly on Monday
```

**Cron Format Reference**:
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

## 🚦 Workflow Permissions

### Current Permissions

All agent workflows have:
```yaml
permissions:
  contents: write      # Create files, commit changes
  issues: write        # Create issues, add labels
  pull-requests: write # Create PRs
```

### If You Have Branch Protection

If your `main` branch has protection rules:

1. **Allow GitHub Actions to bypass**:
   - Settings → Branches → Branch protection rules
   - Edit rule for `main`
   - Enable "Allow force pushes" → "Specify who can force push"
   - Add "github-actions[bot]"

2. **Or use a different branch**:
   Edit workflows to use a different target branch:
   ```yaml
   --base develop  # Instead of main
   ```

## 🎮 Manual Testing

### Test Agent Spawning

```bash
# Trigger manually
gh workflow run agent-spawner.yml

# Watch the run
gh run watch

# Check if agent was created
cat agents/registry.json | jq '.agents'
```

### Test Evaluation

```bash
# Spawn a couple agents first
gh workflow run agent-spawner.yml
sleep 10
gh workflow run agent-spawner.yml

# Then run evaluation
gh workflow run agent-evaluator.yml
```

### Test Data Sync

```bash
# After spawning agents
gh workflow run agent-data-sync.yml

# Check if data was synced
ls -la docs/data/agent-registry.json
```

## 📊 Monitoring

### Check Workflow Status

```bash
# List recent workflow runs
gh run list --workflow=agent-spawner.yml --limit 5
gh run list --workflow=agent-evaluator.yml --limit 5

# View specific run details
gh run view <run-id>
```

### View Agent Status

```bash
# Count active agents
cat agents/registry.json | jq '.agents | length'

# View all agents
cat agents/registry.json | jq '.agents[] | {id: .id, name: .name, status: .status}'

# View Hall of Fame
cat agents/registry.json | jq '.hall_of_fame'

# Check System Lead
cat agents/registry.json | jq '.system_lead'
```

## 🔧 Troubleshooting

### Workflows Not Running

**Check**:
1. Actions are enabled: Settings → Actions → General
2. Workflow files are on main branch
3. No syntax errors in YAML

**Fix**:
```bash
# Validate YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/agent-spawner.yml'))"
```

### Agents Not Showing on GitHub Pages

**Check**:
1. GitHub Pages is enabled
2. Data sync workflow has run
3. File `docs/data/agent-registry.json` exists

**Fix**:
```bash
# Manually trigger data sync
gh workflow run agent-data-sync.yml
```

### Too Many Notifications

**Solutions**:
1. Change watch level to "Custom"
2. Use email filters for `[enufacas/Chained]` and `agent-system`
3. Adjust notification settings in GitHub preferences

## 📝 Summary Checklist

Before first agent spawn, verify:

- [ ] Repository has Actions enabled
- [ ] GitHub Pages is configured (optional, for visualization)
- [ ] Notification preferences set (watch level)
- [ ] Agent parameters reviewed (in registry.json)
- [ ] Schedules are acceptable (every 3h spawn, daily eval)
- [ ] All 3 workflows are present in .github/workflows/
- [ ] Test suite passes (`python3 test_agent_system.py`)

## 🎯 Quick Start Commands

```bash
# 1. Merge this PR
# 2. Wait for first scheduled spawn (next 3-hour mark)
# Or manually trigger:
gh workflow run agent-spawner.yml

# 3. View agents
# Visit: https://enufacas.github.io/Chained/agents.html
# Or check:
cat agents/registry.json

# 4. Monitor
gh run list --workflow=agent-spawner.yml
```

## 🆘 Getting Help

If something doesn't work:
1. Check Actions tab for error messages
2. Review workflow logs
3. Run test suite: `python3 test_agent_system.py`
4. Open issue with label `agent-system`
5. Consult [AGENT_QUICKSTART.md](./AGENT_QUICKSTART.md)

---

## TL;DR - Do You Need Configuration?

**NO CONFIGURATION REQUIRED** for basic operation! 🎉

The system works out of the box:
- ✅ Workflows are ready
- ✅ Permissions are set
- ✅ Schedules are configured
- ✅ Everything auto-creates as needed

**OPTIONAL Configuration**:
- 🔔 Adjust notification preferences (watch level)
- ⚙️ Tune agent parameters (spawn rate, thresholds)
- 🌐 Enable GitHub Pages for visualization
- ⏰ Change schedules if desired

**For Issue Notifications**:
- **Want all agent updates?** → Watch repository (All Activity)
- **Want to filter?** → Watch with custom filters
- **Want minimal noise?** → Ignore repository, check agents page manually

That's it! The agent ecosystem is ready to go! 🚀
