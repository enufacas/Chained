# 🤖 Chained: The Perpetual AI Motion Machine

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://enufacas.github.io/Chained/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blue)](https://github.com/enufacas/Chained)
[![Auto Generated](https://img.shields.io/badge/Auto-Generated-orange)](https://github.com/enufacas/Chained)

**Chained** is an experimental "perpetual AI motion machine" - a self-evolving repository that generates ideas, creates issues, assigns work to AI agents, and documents its own progress with minimal human intervention.

## 🚀 Quick Start

**Want to get started immediately?** See [QUICKSTART.md](./QUICKSTART.md) for 5-minute setup guide!

**New to autonomous AI development?** Read [COPILOT_VISION.md](./COPILOT_VISION.md) to understand what AI wants to build.

## 🎯 Vision

The goal of Chained is to create an entertaining and educational demonstration of **fully autonomous AI-driven development** by building a system that:

- 🧠 **Generates creative ideas** automatically through scheduled workflows
- 📋 **Creates GitHub issues** from those ideas
- 🛠️ **Converts issues to pull requests** automatically
- 🤖 **Reviews its own work** - AI reviews AI code
- ✅ **Merges code autonomously** - no human approval needed
- 📊 **Tracks progress** and documents learnings
- 🌐 **Publishes a timeline** via GitHub Pages showing all autonomous actions

**No human intervention required** - the repository advances itself completely autonomously, creating a true perpetual motion machine of software development.

## 🏗️ Architecture

### Automated Workflows

Chained uses GitHub Actions to maintain its fully autonomous perpetual motion:

1. **AI Idea Generator** (`idea-generator.yml`)
   - Runs daily at 9 AM UTC
   - Generates creative AI-focused feature ideas
   - Creates GitHub issues automatically
   - Can be triggered manually

2. **Copilot Auto-Assign** (`copilot-assign.yml`)
   - Triggers when AI-generated issues are created
   - Automatically tags issues for Copilot
   - Adds tracking labels and comments
   - Can be manually triggered for specific issues

3. **Issue to PR Automator** (`issue-to-pr.yml`)
   - Runs every 3 hours
   - Converts open issues into pull requests
   - Creates branches and implementation files
   - Links PRs back to original issues

4. **Auto Review and Merge** (`auto-review-merge.yml`)
   - Runs every 2 hours
   - AI reviews its own pull requests
   - Automatically approves and merges PRs
   - No human approval required

5. **Auto Close Issues** (`auto-close-issues.yml`)
   - Runs every 4 hours
   - Closes issues when their PRs are merged
   - Tracks completion status
   - Maintains issue lifecycle

6. **Timeline Updater** (`timeline-updater.yml`)
   - Runs every 6 hours
   - Fetches all repository activity
   - Updates timeline data for GitHub Pages
   - Documents autonomous actions

7. **Progress Tracker** (`progress-tracker.yml`)
   - Runs every 12 hours
   - Analyzes repository progress and statistics
   - Generates progress reports
   - Tracks autonomous success rates

### GitHub Pages

The project includes a beautiful, responsive GitHub Pages site at [`docs/`](./docs/) that displays:

- 📈 **Live statistics** from the repository
- ⏱️ **Timeline of events** showing all AI-generated ideas and their progress
- 🧠 **Key learnings** documented throughout the project's evolution
- 📊 **Interactive visualizations** of the perpetual motion machine in action

Visit the live site: **[https://enufacas.github.io/Chained/](https://enufacas.github.io/Chained/)**

## 🚀 Getting Started

### Enabling GitHub Pages

1. Go to your repository **Settings** → **Pages**
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main** (or your default branch)
   - Folder: **/docs**
3. Click **Save**
4. Your site will be live at `https://<username>.github.io/<repo-name>/`

### Customizing Workflows

All workflows are in `.github/workflows/` and can be customized:

- **Adjust scheduling**: Modify the `cron` expressions in each workflow
- **Add more ideas**: Edit the `ideas` array in `idea-generator.yml`
- **Change labels**: Update label names in the workflow files
- **Modify permissions**: Adjust the `permissions` section as needed

### Manual Triggers

All workflows support manual triggering via GitHub's Actions tab:

1. Go to **Actions** in your repository
2. Select the workflow you want to run
3. Click **Run workflow**
4. Fill in any required inputs

## 📚 How It Works

### The Perpetual Motion Cycle

```
┌─────────────────────┐
│  Idea Generator     │ ──► Generates creative ideas (Daily)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Create Issue       │ ──► Creates GitHub issue
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Copilot Assign     │ ──► Tags for Copilot (Instant)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Issue to PR        │ ──► Creates pull request (Every 3h)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Auto Review        │ ──► AI reviews AI code (Every 2h)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Auto Merge         │ ──► Merges to main (No human needed!)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Auto Close Issue   │ ──► Completes lifecycle (Every 4h)
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
```

**This is fully autonomous** - no human in the loop!

### Human Intervention

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
- **HTML/CSS/JavaScript**: Frontend for the timeline
- **Bash scripting**: Workflow logic

## 📊 Monitoring Progress

### Via GitHub Pages
Visit the live site to see real-time statistics, timeline, and learnings.

### Via Issues
- Issues tagged with `ai-generated` are created by the Idea Generator
- Issues tagged with `copilot-assigned` are assigned to Copilot
- Issues tagged with `learning` appear in the learnings section
- Issues tagged with `progress-report` contain progress reports

### Via Actions
Check the Actions tab to see workflow runs and their logs.

## 🤝 Contributing

While Chained is designed to be autonomous, contributions are welcome!

- **Suggest new ideas**: Add to the ideas array in `idea-generator.yml`
- **Improve workflows**: Enhance the automation logic
- **Enhance the timeline**: Improve the GitHub Pages site
- **Fix issues**: Help resolve issues that AI might struggle with
- **Document learnings**: Create issues tagged with `learning`

## 📝 License

This project is open source and available for educational and entertainment purposes.

## 🎉 Acknowledgments

- GitHub Actions for providing the automation platform
- GitHub Copilot for AI-powered development
- GitHub Pages for hosting the timeline
- The open-source community for inspiration

---

**Watch this repository to see the perpetual AI motion machine in action!** ⚡