# Tutorial: Setting Up Your First Chained Instance

Welcome! In this tutorial, you'll set up your own Chained perpetual motion machine from scratch. By the end, you'll have a fully autonomous AI development system running in your own GitHub repository.

## What You'll Learn

- How to fork and configure the Chained repository
- Setting up GitHub secrets and permissions
- Enabling GitHub Pages for visualization
- Configuring branch protection for auto-merge
- Triggering the initial kickoff
- Verifying your setup is working

## Prerequisites

- A GitHub account
- Basic familiarity with GitHub (repositories, issues, pull requests)
- 30 minutes of uninterrupted time
- **Optional**: GitHub CLI for local validation

## Time Required

⏱️ **30-45 minutes** (including waiting for first workflows)

---

## Step 1: Fork the Repository

First, create your own copy of the Chained repository.

### Using GitHub Web UI

1. Go to https://github.com/enufacas/Chained
2. Click the **Fork** button in the top right
3. Choose your account as the destination
4. Keep the repository name as "Chained" (or customize it)
5. ✅ **Important**: Check "Copy the main branch only"
6. Click **Create fork**

**Wait for the fork to complete** - this may take 30-60 seconds.

### What Just Happened?

You now have your own copy of Chained with:
- ✅ All workflow files
- ✅ All documentation
- ✅ Agent definitions
- ✅ GitHub Pages setup
- ✅ Learning system configuration

---

## Step 2: Enable GitHub Actions

Actions need to be enabled in your fork.

1. Go to your forked repository
2. Click the **Actions** tab
3. If you see "Workflows aren't being run on this forked repository":
   - Click **I understand my workflows, go ahead and enable them**

**Why this matters**: Without Actions enabled, none of the autonomous workflows will run!

---

## Step 3: Configure Workflow Permissions

This is **critical** for the autonomous system to work.

1. Go to **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select:
   - ☑️ **Read and write permissions**
4. Check:
   - ☑️ **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

### Why This Is Important

The autonomous system needs these permissions to:
- Create issues automatically (idea generator)
- Open pull requests (Copilot)
- Approve and merge PRs (auto-merge)
- Update files (timeline, learnings)
- Manage labels and assignments

**Without these permissions, the system cannot be autonomous!**

---

## Step 4: Set Up Copilot PAT (Personal Access Token)

For full autonomy, you need a PAT for Copilot assignments.

### Generate a PAT

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Name it: "Chained Copilot Assignment"
4. Set expiration: **90 days** (or longer)
5. Select scopes:
   - ☑️ **repo** (Full control of private repositories)
   - This includes `repo:status`, `repo:deployment`, `public_repo`, `repo:invite`
6. Scroll down and click **Generate token**
7. **⚠️ CRITICAL**: Copy the token immediately - you can't see it again!

### Add PAT as Repository Secret

1. In your Chained repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `COPILOT_PAT` (exact name, case-sensitive!)
4. Value: Paste your PAT
5. Click **Add secret**

### Why This Matters

The default `GITHUB_TOKEN` cannot assign issues to GitHub Copilot due to licensing restrictions. Without the PAT:
- ❌ Copilot assignment workflow will fail
- ❌ Issues won't be automatically implemented
- ❌ The perpetual motion stops!

With the PAT:
- ✅ Issues are automatically assigned to Copilot
- ✅ Copilot creates PRs with implementations
- ✅ Full autonomy achieved!

**See [COPILOT_SETUP.md](../../COPILOT_SETUP.md) for detailed troubleshooting.**

---

## Step 5: Enable GitHub Pages

GitHub Pages displays your autonomous system's activity.

1. Go to **Settings** → **Pages**
2. Under **Build and deployment**:
   - **Source**: Deploy from a branch
   - **Branch**: `main` (or your default branch)
   - **Folder**: `/docs`
3. Click **Save**

### What You'll See

After a few minutes, your site will be live at:
```
https://<your-username>.github.io/Chained/
```

The site includes:
- 📊 Real-time statistics
- ⏱️ Timeline of autonomous actions
- 🤖 Agent leaderboard
- 🧠 AI knowledge graph
- 💬 AI friend conversations

**Note**: The first deploy takes 2-5 minutes. Check the Actions tab for "pages-build-deployment" workflow.

---

## Step 6: Configure Branch Protection

This enables auto-merge for autonomous operation.

1. Go to **Settings** → **Branches**
2. Click **Add branch protection rule**
3. **Branch name pattern**: `main`
4. Configure these settings:

   **Required settings for autonomy**:
   - ☑️ **Require a pull request before merging**
   - Under that:
     - ⚠️ **UNCHECK** "Require approvals"
     - Set required approvals to: **0**
   - ☑️ **Allow auto-merge**
   - ☑️ **Automatically delete head branches**

   **Optional but recommended**:
   - ☑️ **Require status checks to pass before merging**
     - Add check: `CodeQL` (if you want code scanning)
   - ☑️ **Require branches to be up to date before merging**

5. Scroll down and click **Create** or **Save changes**

### Why These Settings?

- **No approval required**: Allows AI to merge its own work
- **Auto-merge enabled**: PRs can merge automatically when checks pass
- **Auto-delete branches**: Keeps the repo clean
- **Status checks**: Ensures code quality before merge

**⚠️ Security Note**: Only PRs from the repository owner with the `copilot` label will auto-merge. External contributions require manual review (via CODEOWNERS).

---

## Step 7: Create Initial Labels

The system uses labels to track autonomous work.

### Option A: Automatic via Kickoff Workflow

The system-kickoff workflow will create labels automatically (see Step 8).

### Option B: Manual Creation

If you prefer to create labels manually:

1. Go to **Issues** → **Labels**
2. Create these labels:

| Label | Color | Description |
|-------|-------|-------------|
| `ai-generated` | `#FF6B6B` | Issues created by AI |
| `copilot-assigned` | `#4ECDC4` | Assigned to GitHub Copilot |
| `copilot` | `#95E1D3` | PRs created by Copilot |
| `learning` | `#F3A683` | Learning and insights |
| `ai-goal` | `#FD79A8` | Daily AI goals |
| `workflow-monitor` | `#FDA7DF` | Workflow issues |
| `agent-performance` | `#A29BFE` | Agent evaluation |

**Tip**: You can import labels by creating a `.github/labels.yml` file (see existing repos for examples).

---

## Step 8: Initialize the System

Now we'll start the autonomous system!

### Option A: Automatic Kickoff (Recommended)

The easiest way is to let the system initialize itself:

1. Make a small change to trigger the auto-kickoff:
   ```bash
   git clone https://github.com/<your-username>/Chained.git
   cd Chained
   echo "# Initializing Chained" >> README.md
   git add README.md
   git commit -m "Initialize Chained system"
   git push origin main
   ```

2. The `auto-kickoff.yml` workflow will automatically:
   - ✅ Detect this is the first merge
   - ✅ Validate system configuration
   - ✅ Create required labels
   - ✅ Initialize directories
   - ✅ Trigger initial workflows
   - ✅ Create a success issue

3. Check the **Actions** tab to watch it happen!

### Option B: Manual Kickoff via GitHub UI

1. Go to **Actions** → **System Kickoff**
2. Click **Run workflow**
3. Select the main branch
4. Choose options:
   - Create labels: **Yes**
   - Trigger workflows: **Yes**
5. Click **Run workflow**
6. Watch the workflow run in real-time

### Option C: Local Kickoff with Scripts

If you have GitHub CLI installed:

1. Clone your repository:
   ```bash
   git clone https://github.com/<your-username>/Chained.git
   cd Chained
   ```

2. Authenticate GitHub CLI:
   ```bash
   gh auth login
   ```

3. Validate your setup:
   ```bash
   ./validate-system.sh
   ```

4. Start the system:
   ```bash
   ./kickoff-system.sh
   ```

5. Check status anytime:
   ```bash
   ./check-status.sh
   ```

---

## Step 9: Verify Everything Is Working

Let's confirm the autonomous system is alive!

### Check 1: Workflow Runs

1. Go to **Actions** tab
2. You should see workflows running:
   - ✅ System Kickoff (if you triggered it)
   - ✅ System Monitor (hourly)
   - ✅ Copilot Assignment (hourly)
   - ✅ Auto Label Copilot PRs (every 10 min)

**Expected**: Green checkmarks ✓ or in-progress yellow dots ●

### Check 2: Issues Created

1. Go to **Issues** tab
2. Within a few hours, you should see:
   - 📋 Daily AI goal issue (created at 6 AM UTC)
   - 💡 Ideas from idea generator (10 AM UTC)
   - 🤖 AI friend conversation issue (9 AM UTC)

**If you don't see issues yet**: Check the Actions tab to ensure workflows are scheduled correctly.

### Check 3: Learning Files

1. Browse your repository
2. Check these directories:
   - `learnings/tldr/` - TLDR Tech insights
   - `learnings/hackernews/` - Hacker News trends
   - `docs/ai-conversations/` - AI friend chats

**These populate based on scheduled workflows** (TLDR at 8 AM/8 PM, HN at 7 AM/1 PM/7 PM UTC).

### Check 4: GitHub Pages

1. Visit: `https://<your-username>.github.io/Chained/`
2. You should see:
   - 📊 Repository statistics
   - ⏱️ Timeline of events
   - 🤖 Agent ecosystem
   - 🧠 Knowledge graph

**If the page isn't live**: Check Actions → "pages-build-deployment" workflow status.

### Check 5: Copilot Assignment

Create a test issue:

1. Go to **Issues** → **New issue**
2. Title: "Test: Add hello world function"
3. Body: "Create a simple hello world function in Python"
4. Labels: Add `ai-generated`
5. Click **Create issue**

**Within an hour**, the copilot-assign workflow should:
- ✅ Add comment confirming assignment
- ✅ Add label `copilot-assigned`
- ✅ Assign the issue to @copilot

**If Copilot creates a PR**, congratulations! 🎉 Full autonomy achieved!

---

## Step 10: Monitor the First 24 Hours

Now sit back and watch the magic happen!

### What to Expect

**Hour 1-6**:
- System monitor runs every hour
- Labels are managed
- Learning workflows may run (if within schedule)

**Hour 6** (6 AM UTC):
- 🎯 Daily goal is generated
- Goal progress tracking begins

**Hour 7** (7 AM UTC):
- 📰 Hacker News learning runs
- Trends are analyzed and saved

**Hour 8** (8 AM UTC):
- 📬 TLDR Tech learning runs
- Tech news is processed

**Hour 9** (9 AM UTC):
- 🤖 AI friend conversation
- Advice is gathered and saved

**Hour 10** (10 AM UTC):
- 💡 Smart idea generation
- Issues are created based on learnings
- Copilot assignment begins

**Hour 11+**:
- 🔄 Copilot may create PRs
- 🤖 Auto-review runs every 15 minutes
- ✅ Successful PRs auto-merge
- 📊 Timeline updates every 6 hours

### Monitoring Tools

**Check status locally**:
```bash
./check-status.sh
```

Shows:
- Recent workflow runs
- Issue/PR statistics
- Learning file count
- Success rate

**View live timeline**:
Visit your GitHub Pages site to see autonomous actions in real-time!

**Watch workflows**:
Actions tab shows all workflow runs with logs.

---

## Common Issues and Solutions

### Issue: Workflows aren't running

**Possible causes**:
- Actions not enabled in fork
- Workflow permissions not set
- Workflows still queued (check Actions tab)

**Solution**:
1. Verify Actions are enabled
2. Check Settings → Actions → General → Workflow permissions
3. Wait 5-10 minutes for scheduled workflows

### Issue: Copilot assignment fails

**Error message**: "Failed to assign issue to Copilot"

**Solution**:
1. Verify `COPILOT_PAT` secret exists
2. Check PAT has `repo` scope
3. Ensure PAT hasn't expired
4. See [COPILOT_SETUP.md](../../COPILOT_SETUP.md)

### Issue: PRs aren't auto-merging

**Possible causes**:
- Branch protection not configured
- Auto-merge not enabled
- PR missing `copilot` label
- Status checks failing

**Solution**:
1. Verify branch protection settings (Step 6)
2. Check PR has `copilot` label
3. Review PR status checks
4. See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

### Issue: GitHub Pages not deploying

**Solution**:
1. Check Settings → Pages is configured
2. Wait 5 minutes after configuration
3. Check Actions → "pages-build-deployment"
4. Verify `/docs` directory exists in `main` branch

### Issue: No issues are being created

**If you're testing outside scheduled times**:

The idea generator runs at **10 AM UTC**. To test immediately:
1. Go to Actions → "Smart Idea Generator"
2. Click "Run workflow"
3. Wait 1-2 minutes
4. Check Issues tab

### Issue: "Rate limit exceeded" errors

**Solution**:
- This is normal for free tier
- GitHub Actions has rate limits for API calls
- System will retry automatically
- Consider upgrading to GitHub Pro for higher limits

---

## Testing Your Setup

Want to test without waiting for schedules? Trigger workflows manually!

### Test Idea Generation

```bash
# Via GitHub CLI
gh workflow run idea-generator.yml

# Or via GitHub web UI:
# Actions → Idea Generator → Run workflow
```

### Test Copilot Assignment

```bash
gh workflow run copilot-graphql-assign.yml
```

### Test Learning Systems

```bash
gh workflow run learn-from-tldr.yml
gh workflow run learn-from-hackernews.yml
gh workflow run ai-friend-daily.yml
```

### Full System Check

```bash
gh workflow run system-monitor.yml
```

---

## Customizing Your Instance

### Adjust Workflow Schedules

Edit `.github/workflows/*.yml` files to change schedules.

**Example**: Change idea generation to every 6 hours:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

**Standard cron expressions**:
- `0 9 * * *` - Daily at 9 AM UTC
- `*/15 * * * *` - Every 15 minutes
- `0 */6 * * *` - Every 6 hours
- `0 9,21 * * *` - At 9 AM and 9 PM UTC

### Add Custom Ideas

Edit `.github/workflows/idea-generator.yml`:

```yaml
ideas:
  - "Implement dark mode for GitHub Pages"
  - "Add metrics dashboard for agent performance"
  - "Create VS Code extension for Chained"
  # Add your ideas here!
```

### Create Custom Agents

Follow the [Creating Your First Custom Agent](./creating-custom-agent.md) tutorial!

---

## Understanding the Costs

Chained runs on GitHub's free tier with minimal costs.

### GitHub Actions Minutes

- **Free tier**: 2,000 minutes/month for public repos
- **Chained usage**: ~200-400 minutes/month with default schedules
- **Cost**: $0 for most users!

### API Rate Limits

- **Free tier**: 5,000 requests/hour
- **Chained usage**: ~100-200 requests/day
- **Cost**: Free

### GitHub Copilot

- **Cost**: $10/month for individuals, $19/month for business
- **Note**: You need an active Copilot subscription for autonomous implementation
- **Benefit**: You use Copilot for this AND your normal work!

### Total Monthly Cost

- **Minimum**: $10/month (just Copilot)
- **Recommended**: $10/month (Copilot) + GitHub free tier
- **Optional**: $4/month for GitHub Pro (higher rate limits)

**Bottom line**: Under $15/month for a fully autonomous AI development system!

---

## Next Steps

Congratulations! Your Chained instance is now running autonomously! 🎉

### Explore Further

1. **Understand the workflow**: Read [Understanding the Autonomous Workflow](./understanding-autonomous-workflow.md)
2. **Create an agent**: Follow [Creating Your First Custom Agent](./creating-custom-agent.md)
3. **Monitor actively**: Learn [Monitoring and Debugging](./monitoring-and-debugging.md)
4. **Dive deeper**: Check out [docs/ARCHITECTURE.md](../ARCHITECTURE.md)

### Join the Community

- ⭐ Star the original repo
- 🔄 Submit improvements via PR
- 💬 Share your experiences
- 🤖 Contribute new agent types

### Share Your Success

Post your GitHub Pages URL:
```
https://<your-username>.github.io/Chained/
```

Watch your autonomous AI ecosystem evolve!

---

## Troubleshooting Resources

If you encounter issues:

1. **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Comprehensive problem-solving guide
2. **[COPILOT_SETUP.md](../../COPILOT_SETUP.md)** - Copilot PAT setup help
3. **[FAQ.md](../../FAQ.md)** - Frequently asked questions
4. **[MONITORING.md](../MONITORING.md)** - System monitoring guide

---

## Conclusion

You now have a fully autonomous AI development system that:
- ✅ Learns from tech trends
- ✅ Generates its own work
- ✅ Implements solutions via AI
- ✅ Reviews and merges code automatically
- ✅ Documents its progress
- ✅ Manages competing AI agents
- ✅ Improves continuously

**Welcome to the future of autonomous software development!** 🚀

---

**Questions or stuck?** Create an issue in the Chained repository with the label `tutorial-help` and the community will assist!
