# 🤖 Chained: The Perpetual AI Motion Machine

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://enufacas.github.io/Chained/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blue)](https://github.com/enufacas/Chained)
[![Auto Generated](https://img.shields.io/badge/Auto-Generated-orange)](https://github.com/enufacas/Chained)

**Chained** is an experimental "perpetual AI motion machine" - a self-evolving repository that generates ideas, creates issues, assigns work to AI agents, and documents its own progress with minimal human intervention.

## 🚀 Quick Start

**Want to verify and launch immediately?** See [GETTING_STARTED.md](./GETTING_STARTED.md) for validation and kickoff!

**Want manual setup instructions?** See [QUICKSTART.md](./QUICKSTART.md) for 5-minute setup guide!

**New to autonomous AI development?** Read [COPILOT_VISION.md](./COPILOT_VISION.md) to understand what AI wants to build.

**Understanding Copilot integration?** See [COPILOT_INTEGRATION.md](./COPILOT_INTEGRATION.md) for how Copilot actually works in this system!

**Have questions about how it works?** Check out the [FAQ.md](./FAQ.md) for answers to common questions!

**Curious about workflow triggers?** Read [WORKFLOW_TRIGGERS.md](./WORKFLOW_TRIGGERS.md) to understand the automation.

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

2. **Copilot Issue Assignment** (`copilot-graphql-assign.yml`)
   - Triggers when any new issue is created
   - Automatically assigns issues to Copilot via API
   - Adds tracking labels and comments
   - Requires COPILOT_PAT secret for full automation
   - Can be manually triggered for specific issues

3. **Issue to PR Automator** (`issue-to-pr.yml`)
   - Runs every 30 minutes
   - Converts open issues into pull requests
   - Creates branches and implementation files
   - Links PRs back to original issues

4. **Auto Review and Merge** (`auto-review-merge.yml`)
   - Runs every 15 minutes
   - AI reviews its own pull requests
   - Automatically approves and merges PRs
   - No human approval required

5. **Auto Close Issues** (`auto-close-issues.yml`)
   - Runs every 30 minutes
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

8. **Learning from TLDR Tech** (`learn-from-tldr.yml`)
   - Runs twice daily (8 AM, 8 PM UTC)
   - Fetches latest tech news and trends
   - Extracts insights about AI, DevOps, and programming
   - Saves learnings to influence future ideas

9. **Learning from Hacker News** (`learn-from-hackernews.yml`)
   - Runs three times daily (7 AM, 1 PM, 7 PM UTC)
   - Analyzes trending technical discussions
   - Categorizes topics (AI/ML, Security, Performance, etc.)
   - Generates ideas based on community trends

10. **Smart Idea Generator** (`smart-idea-generator.yml`)
    - Runs daily at 10 AM UTC (after learning workflows)
    - Generates ideas informed by external learnings
    - Adapts to trending technologies and patterns
    - Creates enhanced issues with learning context

11. **System Kickoff** (`system-kickoff.yml`)
    - Can be triggered manually or automatically
    - Validates system configuration
    - Creates required labels
    - Initializes directories
    - Triggers initial workflows
    - Creates kickoff success issue

12. **Auto Kickoff on First Run** (`auto-kickoff.yml`)
    - Runs automatically on merge to main
    - Detects if system already kicked off
    - Triggers kickoff workflow if needed
    - Ensures one-time initialization

### GitHub Pages

The project includes a beautiful, responsive GitHub Pages site at [`docs/`](./docs/) that displays:

- 📈 **Live statistics** from the repository
- ⏱️ **Timeline of events** showing all AI-generated ideas and their progress
- 🧠 **Key learnings** documented throughout the project's evolution, including insights from TLDR Tech and Hacker News
- 📊 **Interactive visualizations** of the perpetual motion machine in action
- 🌐 **External learning integration** showing how the AI stays current with tech trends

Visit the live site: **[https://enufacas.github.io/Chained/](https://enufacas.github.io/Chained/)**

## 🚀 Getting Started

### Automatic Kickoff (Easiest!) 🎯

**The system automatically starts when you merge to main!** 

A GitHub Actions workflow will:
- ✅ Validate the system
- ✅ Create required labels
- ✅ Initialize directories  
- ✅ Trigger initial workflows
- ✅ Create a kickoff success issue

**Just merge and watch the Actions tab!**

### Alternative: Manual Start

**Local Scripts:** If you have the repository locally:

```bash
# 1. Validate your system is ready
./validate-system.sh

# 2. Initialize and start the autonomous system
./kickoff-system.sh

# 3. Check the status anytime
./check-status.sh
```

**GitHub Actions:** Go to Actions → "System Kickoff" → Run workflow

These methods will:
- ✅ Verify all workflows and documentation exist
- ✅ Create necessary labels
- ✅ Validate system configuration
- ✅ Trigger initial workflows
- ✅ Provide status updates

**See [GETTING_STARTED.md](./GETTING_STARTED.md) for detailed instructions.**

**See [QUICKSTART.md](./QUICKSTART.md) for the 5-minute manual setup guide.**

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
│  Copilot Assign     │ ──► Tags for Copilot (Instant)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Issue to PR        │ ──► Creates pull request (Every 30min)
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

### Human Intervention

The system is **fully autonomous** and requires zero human intervention. However, humans can still:

- **Observe the magic** via GitHub Pages timeline
- **Steer the direction** by creating custom issues with specific ideas
- **Adjust parameters** by modifying workflow schedules
- **Document learnings** by creating issues with the `learning` label
- **Manually trigger** workflows when desired
- **Celebrate** the autonomous achievements!

The beauty is that you can walk away and come back later to see what the AI has built!

## 🧠 Continuous Learning

One of the most powerful features of Chained is its ability to **continuously learn** from external sources:

### Learning Sources

- **[TLDR Tech](https://tldr.tech/)**: Twice daily scraping of tech news summaries
- **[Hacker News](https://news.ycombinator.com/)**: Three times daily analysis of trending discussions

### What It Learns

The system automatically:
- 📰 Fetches latest tech news and articles
- 🎯 Identifies trending topics (AI/ML, Security, Performance, etc.)
- 💡 Extracts insights from community discussions
- 📊 Categorizes and prioritizes learnings
- 🔄 Feeds learnings back into idea generation

### Impact on Development

Learnings influence:
- **Idea Generation**: New ideas based on trending technologies
- **Technology Choices**: Adopting what's hot, avoiding what's deprecated
- **Best Practices**: Learning from the global tech community
- **Security**: Staying aware of vulnerabilities and fixes

See [`learnings/`](./learnings/) directory for all collected insights.

### Learning Workflow

```
Morning    → TLDR scraper runs     → Saves tech news
           → HN scraper runs        → Analyzes trending discussions
           → Smart Idea Generator   → Creates trend-aware ideas
Afternoon  → HN scraper runs again → Updates with new trends
Evening    → TLDR scraper runs     → Evening news update
           → HN scraper runs        → Final daily update
```

**The AI never stops learning from the world around it!** 🌍

## 🛠️ Technologies Used

- **GitHub Actions**: Workflow automation
- **GitHub API**: Fetching repository data
- **GitHub Pages**: Hosting the timeline website
- **GitHub Copilot**: AI-powered development
- **Python**: Learning scripts and data processing
- **HTML/CSS/JavaScript**: Frontend for the timeline
- **Bash scripting**: Workflow logic
- **TLDR Tech API**: Tech news aggregation
- **Hacker News API**: Community trend analysis

## 📊 Monitoring Progress

### Quick Status Check

Run the status checker script anytime:

```bash
./check-status.sh
```

This will show:
- Recent workflow runs and their status
- Issue and PR statistics
- Learning files count
- GitHub Pages status
- Next scheduled workflow runs
- Autonomous success rate

### Verify Scheduled Workflows

**New!** To verify that your cron schedules are actually running:

```bash
./verify-schedules.sh
```

This tool checks:
- When each scheduled workflow last ran
- Whether workflows are running on time
- Detection of overdue or late workflows
- Analysis of recent failures
- Repository activity status (60-day deactivation warning)

See **[WORKFLOW_TRIGGERS.md](./WORKFLOW_TRIGGERS.md)** for complete details about how workflows are triggered and scheduled.

### Via GitHub Pages
Visit the live site to see real-time statistics, timeline, and learnings.

### Via Issues
- Issues tagged with `ai-generated` are created by the Idea Generator
- Issues tagged with `copilot-assigned` are assigned to Copilot
- Issues tagged with `learning` appear in the learnings section
- Issues tagged with `progress-report` contain progress reports
- Issues tagged with `workflow-monitor` indicate schedule or execution problems

### Via Actions
Check the Actions tab to see workflow runs and their logs.

## 🔧 System Utilities

The repository includes helper scripts to manage the autonomous system:

### verify-schedules.sh
**NEW!** Verify that scheduled workflows are running properly:
- Checks when each workflow last ran
- Compares against expected schedule intervals
- Detects overdue or late workflow runs
- Analyzes recent failures
- Warns about 60-day inactivity deactivation
- Provides actionable recommendations

```bash
./verify-schedules.sh
```

**Use this when:** You want to verify your cron schedules are actually executing.

### evaluate-workflows.sh
Comprehensive workflow state evaluation:
- Checks all workflows are present
- Validates workflow triggers and schedules
- Verifies workflow permissions
- Checks workflow dependencies
- Validates workflow chain execution
- YAML syntax validation

```bash
./evaluate-workflows.sh
```

### validate-system.sh
Pre-flight validation script that checks:
- Repository structure and files
- All workflow files exist (including auto-kickoff and system-kickoff)
- Documentation completeness
- GitHub Pages configuration
- Git and GitHub CLI setup
- YAML syntax validation (if yamllint available)

```bash
./validate-system.sh
```

### kickoff-system.sh
Initialize and start the perpetual motion machine:
- Runs pre-flight validation
- Verifies GitHub configuration
- Creates required labels
- Initializes directories
- Optionally triggers initial workflows

```bash
./kickoff-system.sh
```

### check-status.sh
Monitor the system's health and progress:
- Recent workflow runs
- Issue and PR statistics
- Learning files count
- GitHub Pages status
- Next scheduled runs
- Success metrics

```bash
./check-status.sh
```

## 🤝 Contributing

While Chained is designed to be autonomous, **external contributions are welcome and require manual review** for security!

### How External Contributions Work

- **Submit PRs**: External contributors can submit pull requests
- **Manual Review**: All external PRs require repository owner review (via CODEOWNERS)
- **Security**: Auto-merge only works for owner and trusted bot PRs with `copilot` label
- **Transparency**: PRs that don't meet auto-merge criteria receive clear feedback

See [docs/SECURITY_IMPLEMENTATION.md](./docs/SECURITY_IMPLEMENTATION.md) for details on how the security model works.

### Ways to Contribute

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