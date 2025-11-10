# 📊 Monitoring Progress

## Quick Status Check

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

## Verify Scheduled Workflows

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

See **[WORKFLOW_TRIGGERS.md](../WORKFLOW_TRIGGERS.md)** for complete details about how workflows are triggered and scheduled.

## Via GitHub Pages
Visit the live site to see real-time statistics, timeline, and learnings.

## Via Issues
- Issues tagged with `ai-generated` are created by the Idea Generator
- Issues tagged with `copilot-assigned` are assigned to Copilot
- Issues tagged with `learning` appear in the learnings section
- Issues tagged with `progress-report` contain progress reports
- Issues tagged with `workflow-monitor` indicate schedule or execution problems

## Via Actions
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

---

[← Tools](TOOLS.md) | [Back to README](../README.md) | [Contributing →](CONTRIBUTING.md)
