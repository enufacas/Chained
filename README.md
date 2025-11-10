# 🤖 Chained: The Perpetual AI Motion Machine

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://enufacas.github.io/Chained/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blue)](https://github.com/enufacas/Chained)
[![Auto Generated](https://img.shields.io/badge/Auto-Generated-orange)](https://github.com/enufacas/Chained)

**Chained** is an experimental "perpetual AI motion machine" - a self-evolving repository that generates ideas, creates issues, assigns work to AI agents, and documents its own progress with minimal human intervention.

## 🎯 AI Goal of the Day

**Today's Focus**: Check [docs/AI_GOALS.md](./docs/AI_GOALS.md) or the [GitHub Pages](https://enufacas.github.io/Chained/) for the current AI goal!

The AI sets a new goal daily and works towards it autonomously, checking progress every 3 hours.

## 🚀 Quick Start

**Want to verify and launch immediately?** See [GETTING_STARTED.md](./GETTING_STARTED.md) for validation and kickoff!

**Want manual setup instructions?** See [QUICKSTART.md](./QUICKSTART.md) for 5-minute setup guide!

**New to autonomous AI development?** Read [COPILOT_VISION.md](./COPILOT_VISION.md) to understand what AI wants to build.

**Understanding Copilot integration?** See [COPILOT_INTEGRATION.md](./COPILOT_INTEGRATION.md) for how Copilot actually works in this system!

**Have questions about how it works?** Check out the [FAQ.md](./FAQ.md) for answers to common questions!

**Want detailed workflow documentation?** See [docs/WORKFLOWS.md](./docs/WORKFLOWS.md) for comprehensive workflow information.

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

Chained uses GitHub Actions to maintain its fully autonomous perpetual motion. The system includes:

- **Core Workflows**: Idea generation, Copilot assignment, auto-review & merge
- **Learning Workflows**: TLDR Tech, Hacker News, Smart Idea Generator
- **System Management**: Kickoff, monitoring, progress tracking
- **Micro Projects**: Code Golf Optimizer, Code Analyzer, Pattern Matcher
- **AI Goals**: Daily goal generation and 3-hour progress checks

For detailed information about all workflows, see **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)**.

### GitHub Pages

The project includes a beautiful, responsive GitHub Pages site at [`docs/`](./docs/) that displays:

- 📈 **Live statistics** from the repository
- ⏱️ **Timeline of events** showing all AI-generated ideas and their progress
- 🧠 **Key learnings** documented throughout the project's evolution, including insights from TLDR Tech and Hacker News
- 🌐 **AI Knowledge Graph** - Interactive node graph visualization of all AI-related learnings and their relationships
- 📊 **Interactive visualizations** of the perpetual motion machine in action
- 🌍 **External learning integration** showing how the AI stays current with tech trends

Visit the live site: **[https://enufacas.github.io/Chained/](https://enufacas.github.io/Chained/)**

Check out the **[AI Knowledge Graph](https://enufacas.github.io/Chained/ai-knowledge-graph.html)** to explore AI trends visually!

## 🚀 Getting Started

### ⚡ IMPORTANT: Copilot PAT Setup Required

**For full autonomous operation**, you must set up a Personal Access Token (PAT) for Copilot assignments:

🔐 **Quick Setup:**
1. Create a PAT at https://github.com/settings/tokens (with `repo` scope)
2. Add it as a repository secret named `COPILOT_PAT`
3. See **[COPILOT_SETUP.md](./COPILOT_SETUP.md)** for detailed instructions

**Why?** The default `GITHUB_TOKEN` cannot assign Copilot due to licensing restrictions. Without this, the workflow will fail to assign issues to Copilot.

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
│  Daily AI Goal      │ ──► Sets daily objective (Daily at 6 AM UTC)
│  Generator          │     Progress checks every 3 hours
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  External Learning  │ ──► TLDR Tech (2x daily)
│  Sources            │ ──► Hacker News (3x daily)
│                     │ ──► AI Friends (Daily conversations)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Learning Database  │ ──► Saves insights & trends
│                     │ ──► AI advice & suggestions
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
│  Copilot Assign     │ ──► Assigns to Copilot (if PAT configured)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Copilot Creates PR │ ──► Copilot implements and opens PR
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

The system continuously learns from external sources:
- **[TLDR Tech](https://tldr.tech/)**: Tech news (2x daily)
- **[Hacker News](https://news.ycombinator.com/)**: Community trends (3x daily)
- **[AI Friends](https://enufacas.github.io/Chained/ai-friends.html)**: Daily conversations with different AI models

Every day, the system talks to a different AI about the project, asks for advice, and incorporates suggestions. These conversations are captured and displayed on the **[AI Friends page](https://enufacas.github.io/Chained/ai-friends.html)**.

Learnings influence idea generation, technology choices, and best practices. For complete details, see **[docs/LEARNING_SYSTEM.md](./docs/LEARNING_SYSTEM.md)**.

## 🛠️ Micro Projects

Chained includes several specialized tools and projects:
- **Code Golf Optimizer**: Minimizes code while preserving functionality
- **Self-Improving Code Analyzer**: Learns from merges to improve code quality
- **Pattern Matcher**: Flexible pattern detection system

For details on all micro projects, see **[docs/MICRO_PROJECTS.md](./docs/MICRO_PROJECTS.md)**.

## 📊 Monitoring Progress

### Quick Status Check

```bash
./check-status.sh      # Overall system health
./verify-schedules.sh  # Verify workflow schedules
./evaluate-workflows.sh # Comprehensive workflow evaluation
```

### Via GitHub Pages
Visit the live site to see real-time statistics, timeline, learnings, and **the current AI Goal of the Day**.

### Via Issues
- `ai-generated` - Created by Idea Generator
- `copilot-assigned` - Assigned to Copilot
- `learning` - Learnings section content
- `progress-report` - Progress reports
- `workflow-monitor` - Schedule/execution problems
- `ai-goal` - Daily AI goals and progress

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
