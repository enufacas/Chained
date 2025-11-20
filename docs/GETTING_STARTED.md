# How to Verify and Start the Chained System

This guide answers: **"How do we know it's going to work? Can we kick things off now?"**

## Quick Answer: Yes! Three Ways to Start

### Option 1: Automatic (Easiest) 🎯

**The system automatically kicks off when you merge to main!**

A GitHub Actions workflow detects the first merge and:
- ✅ Validates the system
- ✅ Creates required labels
- ✅ Initializes directories
- ✅ Triggers initial workflows
- ✅ Creates a kickoff success issue

**Just merge this PR and watch the Actions tab!**

### Option 2: Manual via GitHub Actions

Go to the **Actions** tab and run the "System Kickoff" workflow:

1. Click on "System Kickoff" workflow
2. Click "Run workflow"
3. Choose options:
   - Create labels: Yes
   - Trigger workflows: Yes
4. Click "Run workflow"

The automated workflow will handle everything!

### Option 3: Local Script (If GitHub CLI is set up)

If you have the repository locally and GitHub CLI authenticated:

#### Step 1: Validate Everything Works

Run the validation script to check your system:

```bash
./scripts/validate-system.sh
```

This checks:
- ✅ All workflow files exist (including auto-kickoff and system-kickoff)
- ✅ Documentation is complete  
- ✅ GitHub Pages is configured
- ✅ Git is set up properly
- ✅ Required tools are available

For a more comprehensive workflow evaluation:

```bash
./evaluate-workflows.sh
```

This additionally validates:
- ✅ All 12 workflows are present
- ✅ Workflow triggers and schedules
- ✅ Workflow permissions and dependencies
- ✅ Complete workflow execution chain

**If validation passes with only warnings**, you're ready to go!

#### Step 2: Kick Things Off

Start the autonomous system:

```bash
./scripts/kickoff-system.sh
```

This will:
- ✅ Run pre-flight validation
- ✅ Verify GitHub configuration
- ✅ Create required labels
- ✅ Initialize directories
- ✅ Optionally trigger initial workflows

---

## Monitor Progress (All Options)

Check the status anytime:

```bash
./scripts/check-status.sh
```

This shows:
- 📊 Recent workflow runs
- 📋 Issue and PR statistics
- 🧠 Learning files count
- 📈 Success metrics

## What Happens After Kickoff?

Once started, the system runs autonomously:

1. **Ideas Generated** - Daily at 10:00 UTC
2. **Learning Happens** - Multiple times daily from TLDR Tech and Hacker News
3. **Issues Created** - Automatically from ideas
4. **PRs Opened** - Every 30 minutes from open issues
5. **Code Reviewed** - Every 15 minutes by AI
6. **PRs Merged** - Automatically after approval
7. **Issues Closed** - Every 30 minutes after PR merge
8. **Timeline Updated** - Every 6 hours on GitHub Pages

## How to Know It's Working

### Good Signs:
- ✅ Validation script shows all green checkmarks
- ✅ Kickoff completes without errors
- ✅ Status script shows workflow runs
- ✅ Issues appear with `ai-generated` label
- ✅ PRs are created automatically
- ✅ GitHub Pages updates

### If Something's Wrong:
- Run `./scripts/validate-system.sh` to identify issues
- Check [QUICKSTART.md](./QUICKSTART.md) for manual setup steps
- Review [README.md](./README.md) for detailed documentation
- Ensure GitHub repository settings are configured correctly

## Confidence Check ✓

Before starting, ensure:

- [ ] You have admin access to the repository
- [ ] GitHub Actions are enabled
- [ ] Workflow permissions set to "Read and write"
- [ ] "Allow GitHub Actions to create and approve pull requests" is enabled
- [ ] Branch protection allows auto-merge with 0 required approvals
- [ ] GitHub Pages is enabled (Settings → Pages → Source: main, Folder: /docs)

Once these are checked, **you can confidently kick things off!**

## Summary

**Question:** How do we know it's going to work?
**Answer:** Run `./scripts/validate-system.sh` - if it passes, it will work!

**Question:** Can we kick things off now?
**Answer:** Yes! Run `./scripts/kickoff-system.sh` to start the perpetual motion machine!

Then sit back and watch the AI build itself. 🤖✨
