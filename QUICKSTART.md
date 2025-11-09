# 🚀 Quick Start Guide

Get your perpetual AI motion machine running in 5 minutes!

## Prerequisites

- A GitHub repository (this one!)
- Admin access to repository settings

## Setup Steps

### 1. Enable Workflow Permissions (Required)

Go to **Settings** → **Actions** → **General** → **Workflow permissions**:

- ✅ Select "Read and write permissions"
- ✅ Check "Allow GitHub Actions to create and approve pull requests"
- Click **Save**

### 2. Configure Branch Protection (Required for Auto-Merge)

Go to **Settings** → **Branches** → **Add branch protection rule**:

**Branch name pattern:** `main`

Configure these settings:
- ✅ **Require a pull request before merging**
  - ⚠️ **UNCHECK** "Require approvals" (critical for autonomous operation!)
  - Number of required approvals: 0
- ✅ **Allow auto-merge**
- ✅ **Automatically delete head branches**
- Optional: Require status checks if you have CI/CD

Click **Create** or **Save changes**

### 3. Enable GitHub Pages (Required)

Go to **Settings** → **Pages**:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/docs`
- Click **Save**

Your site will be live at: `https://<username>.github.io/<repo-name>/`

### 4. Create Initial Labels (Optional but Recommended)

Run this script or create labels manually:

```bash
gh label create "ai-generated" --color "7057ff" --description "Created by AI Idea Generator"
gh label create "copilot-assigned" --color "0366d6" --description "Assigned to Copilot"
gh label create "copilot" --color "0366d6" --description "Created by Copilot"
gh label create "automated" --color "fbca04" --description "Automated process"
gh label create "in-progress" --color "fbca04" --description "Work in progress"
gh label create "completed" --color "0e8a16" --description "Completed task"
gh label create "learning" --color "d93f0b" --description "Learning or insight"
gh label create "progress-report" --color "c5def5" --description "Progress tracking"
```

Or manually create them in **Issues** → **Labels** → **New label**

### 5. Test the System

#### Option A: Wait for Scheduled Runs
The workflows will start automatically:
- First idea: Next day at 9 AM UTC
- First PR: Within 3 hours after an issue is created
- First merge: Within 2 hours after a PR is created

#### Option B: Trigger Manually (Recommended for Testing)
1. Go to **Actions** tab
2. Select "AI Idea Generator"
3. Click "Run workflow" → "Run workflow"
4. Wait ~30 seconds, then refresh
5. Go to **Issues** - you should see a new AI-generated issue!
6. Repeat for other workflows in this order:
   - Copilot Auto-Assign
   - Issue to PR Automator
   - Auto Review and Merge
   - Timeline Updater

### 6. Watch the Magic!

- 📊 Check your GitHub Pages site to see the timeline
- 👀 Watch Issues and PRs appear automatically
- 🎉 See the autonomous cycle complete end-to-end

## Verification Checklist

After setup, verify these permissions:

```bash
# Check if Actions can create PRs
gh api repos/:owner/:repo/actions/permissions

# Check branch protection
gh api repos/:owner/:repo/branches/main/protection

# Check Pages status
gh api repos/:owner/:repo/pages
```

## Troubleshooting

### Workflows not creating issues/PRs?
- ✅ Check workflow permissions are "Read and write"
- ✅ Check "Allow GitHub Actions to create and approve pull requests" is enabled

### PRs not auto-merging?
- ✅ Check branch protection has 0 required approvals
- ✅ Check "Allow auto-merge" is enabled
- ✅ Check the PR has the "copilot" label

### GitHub Pages not loading?
- ✅ Wait 2-3 minutes after enabling
- ✅ Check the Pages build workflow succeeded
- ✅ Verify the docs/ folder exists in main branch

### Labels not working?
- ✅ Create missing labels manually
- ✅ Check exact spelling matches workflow files

## What to Expect

### First Hour
- Setup complete
- First workflow runs
- First AI-generated issue created

### First Day
- Multiple issues created
- First PR created and merged
- Timeline starts populating
- GitHub Pages shows activity

### First Week
- Full autonomous cycle operational
- Multiple ideas implemented
- Rich timeline history
- Self-sustaining operation

### First Month
- Dozens of autonomous contributions
- Clear patterns emerging
- Growing implementation library
- Fully autonomous evolution

## Next Steps

1. **Watch the Timeline**: Visit your GitHub Pages site daily
2. **Review Progress**: Check the Actions tab for workflow history
3. **Steer Occasionally**: Create custom issues with specific ideas
4. **Celebrate**: Share your autonomous repository with others!
5. **Document Learnings**: Create issues tagged with "learning"

## Advanced Configuration

See [CONFIGURATION.md](./CONFIGURATION.md) for:
- Adjusting workflow schedules
- Adding more idea templates
- Custom domains for GitHub Pages
- Security considerations

## Need Help?

- 📖 Read [README.md](./README.md) for full documentation
- 🤖 Check [COPILOT_VISION.md](./COPILOT_VISION.md) for AI's perspective
- 💡 Create an issue and let the AI help you!

---

**You're all set! Welcome to the future of autonomous development.** 🎉

The machine is now in perpetual motion. Come back anytime to see what it has built!
