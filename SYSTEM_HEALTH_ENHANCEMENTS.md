# System Health Enhancements

## Overview

This document describes the enhancements made to the system health monitoring workflow to provide comprehensive health checks and automated issue resolution.

## Implementation Date

November 11, 2025

## New Features

### 1. Merge Conflict Resolution (Every 3 Hours)

**Purpose**: Automatically detect and resolve merge conflicts in open PRs from trusted sources.

**How it works**:
- Sweeps all open PRs every 3 hours
- Identifies PRs with merge conflicts (mergeable: CONFLICTING or merge state: DIRTY)
- For trusted sources (bots, repo owner with copilot label):
  - Attempts intelligent resolution using 'ours' strategy first (prefers PR changes)
  - Falls back to 'theirs' strategy if 'ours' fails (prefers base branch changes)
  - Comments on PRs with resolution status
- For untrusted sources:
  - Comments on PR requesting manual resolution
  - Does not attempt auto-resolution for security

**Safety measures**:
- Only resolves conflicts for trusted sources
- Always comments on PRs to explain what was done
- Uses git strategies (ours/theirs) to handle conflicts predictably
- Falls back to manual resolution request if both strategies fail

**Schedule**: `0 */3 * * *` (every 3 hours, on the hour)

### 2. Custom Agent Health Check (Every 3 Hours)

**Purpose**: Monitor the end-to-end health of the custom agent system.

**Health checks performed**:
1. **Agent Spawner Workflow**: Verifies agent-spawner.yml exists and is enabled
2. **Agent Data Files**: Checks for agent JSON files in docs/data/agents/
3. **Recent Agent Activity**: Looks for recent agent-created issues
4. **Agent Assignment**: Verifies agent assignment is working (copilot-assigned issues)
5. **Agent Evaluator**: Confirms agent-evaluator.yml workflow exists

**Health scoring**:
- **Healthy**: 80-100% of checks pass
- **Warning**: 60-79% of checks pass
- **Critical**: Below 60% of checks pass

**Actions taken**:
- Creates or updates health issue if status is critical
- Provides diagnostics and recommendations
- Checks workflow run history for failures
- Reports health score and status

**Schedule**: `0 */3 * * *` (every 3 hours, on the hour)

### 3. GitHub Pages Health Check (Every 3 Hours)

**Purpose**: Validate GitHub Pages is healthy and accessible.

**Health checks performed**:
1. **Essential HTML Files**: Verifies index.html, ai-knowledge-graph.html, ai-friends.html, agents.html exist
2. **Data Files**: Checks for stats.json, issues.json, pulls.json, workflows.json
3. **Data Freshness**: Validates data is less than 12 hours old
4. **Accessibility**: Tests that GitHub Pages site is accessible (HTTP 200 response)

**Actions taken**:
- Creates or updates health issue if problems found
- Reports specific files missing or stale
- Provides recommendations for fixing issues

**Schedule**: `0 */3 * * *` (every 3 hours, on the hour)

## Manual Triggering

All three new jobs support manual triggering via workflow_dispatch with skip options:
- `skip_merge_conflicts`: Skip merge conflict resolution
- `skip_agent_health`: Skip custom agent health check
- `skip_pages_health`: Skip GitHub Pages health check

## Configuration

### Location
`.github/workflows/system-monitor.yml`

### Schedule
All three new jobs run on the same schedule: every 3 hours at the top of the hour (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 UTC).

### Permissions Required
- `contents: write` - For merge conflict resolution
- `pull-requests: write` - For PR comments and updates
- `issues: write` - For creating health check issues
- `actions: read` - For checking workflow status

## Benefits

1. **Automated Issue Resolution**: Merge conflicts are resolved automatically for trusted sources, reducing manual intervention
2. **Proactive Monitoring**: Health checks catch issues before they become critical
3. **Comprehensive Coverage**: Monitors all aspects of the agent system and GitHub Pages
4. **Actionable Feedback**: Creates issues with specific recommendations when problems are found
5. **Audit Trail**: All actions are logged and commented on PRs/issues

## Metrics & Reporting

### Merge Conflict Resolution
- Number of PRs with conflicts detected
- Number of PRs successfully resolved
- Number of PRs requiring manual resolution

### Agent Health Check
- Overall health score (percentage)
- Individual check pass/fail status
- Workflow run statistics

### Pages Health Check
- Number of issues found
- Health status (healthy/warning/critical)
- Specific problems identified

## Troubleshooting

### Merge Conflict Resolution Not Working
- Check that PRs have the `copilot` label
- Verify PR author is a trusted source
- Check workflow permissions
- Review workflow logs for errors

### Agent Health Check Failing
- Review agent-spawner.yml workflow status
- Check for agent data files in docs/data/agents/
- Verify agent-evaluator.yml exists
- Check for recent agent-created issues

### Pages Health Check Failing
- Verify HTML files exist in docs/
- Check data files are being updated by timeline job
- Ensure GitHub Pages is enabled in repository settings
- Test site accessibility manually

## Future Enhancements

Potential future improvements:
- Smarter merge conflict resolution using AI
- More granular agent health metrics
- Performance monitoring for GitHub Pages
- Integration with external monitoring services
- Automated recovery actions for common failures

## Security Considerations

- Merge conflict resolution only works with trusted sources
- All actions are logged and auditable
- No secrets or sensitive data are exposed in logs
- Health checks are read-only except for issue creation
- Git operations use secure GITHUB_TOKEN

## Related Documentation

- [System Monitor Workflow](../.github/workflows/system-monitor.yml)
- [Agent System Documentation](./docs/AGENT_SYSTEM.md)
- [GitHub Pages Documentation](./docs/GITHUB_PAGES.md)
- [Workflow Documentation](./docs/WORKFLOWS.md)
