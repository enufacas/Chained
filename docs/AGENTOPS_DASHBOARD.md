# AgentOps Dashboard

## Overview

The AgentOps Dashboard provides comprehensive monitoring and observability for the Chained autonomous agent system. It offers a single pane of glass to understand all operational aspects including workflow executions, agent performance, system health, and operational metrics.

## Features

### 📈 System Overview
- **Total Runs** - Aggregate count of all workflow executions
- **Success Rate** - Percentage of successful vs failed runs
- **Average Duration** - Mean execution time across all workflows
- **In Progress** - Currently active workflow runs
- **Recent Failures** - Failed runs in the last 24 hours
- **Active Agents** - Number of agents with active workload

### 🤖 Agent Workload Distribution
View workload distribution across all active agents:
- Total runs per agent
- Success/failure/in-progress breakdown
- Visual cards showing agent activity

### ⚙️ Workflow Performance
Performance metrics for each monitored workflow:
- Total runs per workflow
- Success/failure counts
- Success rate percentage
- Average duration per workflow

### 📋 Recent Workflow Runs
Detailed table of recent executions with:
- Run number and workflow name
- Status badges (success/failure/in-progress)
- Agent attribution (@agent-name)
- Duration and start time
- Direct links to GitHub Actions logs

### 🔍 Filtering & Search
- Filter by status (All/Success/Failure/In Progress)
- Filter by workflow type
- Real-time table updates

## Data Sources

The dashboard consumes data from:

1. **GitHub Actions API** - Workflow run metadata
2. **Agent Registry** - Active agent information
3. **Workflow Metadata** - Workflow configuration

### Monitored Workflows

- `copilot-graphql-assign.yml` - Copilot agent assignments
- `autonomous-pipeline.yml` - Main autonomous loop
- `learn-from-copilot.yml` - Learning from completed work
- `agent-missions.yml` - Mission generation
- `agent-evaluator.yml` - Agent performance evaluation
- `self-reinforcement.yml` - System self-improvement

## Data Synchronization

The dashboard data is updated via the `agentops-data-sync.yml` workflow:

- **Schedule**: Runs every 30 minutes
- **Manual Trigger**: Can be triggered via workflow_dispatch
- **Data File**: `docs/data/agentops-runs.json`
- **Rate Limiting**: Protected by caching and conditional requests

### Sync Workflow Details

```yaml
# Workflow runs on schedule and manual dispatch
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes

# Fetches data from GitHub Actions API
# Aggregates metrics and statistics
# Generates agentops-runs.json
# Creates PR with updated data
```

## Architecture

```
GitHub Actions API
       ↓
  [Sync Workflow]
       ↓
agentops-runs.json
       ↓
  AgentOps Dashboard
       ↓
    Browser
```

### Data Flow

1. **Collection**: Sync workflow fetches run data from GitHub Actions API
2. **Aggregation**: Computes summary statistics and metrics
3. **Storage**: Saves to `docs/data/agentops-runs.json`
4. **Presentation**: Dashboard loads and displays data
5. **Updates**: Browser refreshes data every 5 minutes

## Usage

### Accessing the Dashboard

Visit: [https://enufacas.github.io/Chained/agentops.html](https://enufacas.github.io/Chained/agentops.html)

Or navigate from the main site:
1. Go to the Chained homepage
2. Click "📊 AgentOps" in the navigation bar

### Monitoring Operations

1. **Check System Health** - View the System Overview metrics
2. **Identify Issues** - Look at Recent Failures count
3. **Debug Problems** - Click "View Run →" to see logs
4. **Track Agents** - Monitor agent workload distribution
5. **Analyze Performance** - Review workflow statistics

### Investigating Failures

1. Filter runs by status: "Failure"
2. Review the failed runs table
3. Click "View Run →" to open GitHub Actions logs
4. Check the run details for error messages
5. Identify patterns (same workflow, same agent)

## Best Practices

### Monitoring Guidelines

1. **Regular Checks** - Review dashboard daily
2. **Failure Alerts** - Watch for spikes in failure rates
3. **Performance Trends** - Monitor average duration changes
4. **Agent Balance** - Ensure workload is distributed evenly

### Debugging Workflow Failures

1. **Recent Failures Section** - Check the dedicated failures view
2. **Agent Correlation** - Look for agent-specific issues
3. **Workflow Patterns** - Identify problematic workflows
4. **Time Analysis** - Check if failures correlate with time of day
5. **Deep Links** - Use GitHub Actions logs for detailed analysis

### Rate Limiting Protection

The dashboard implements several protections:

- ✅ **Scheduled Sync** - Data fetched every 30 minutes, not on-demand
- ✅ **Cached Data** - Dashboard loads from static JSON file
- ✅ **Batch Requests** - Sync workflow fetches multiple workflows in one run
- ✅ **Conditional Requests** - Uses ETags when available
- ✅ **Limited History** - Keeps last 100 runs per workflow

## Data Structure

### agentops-runs.json Format

```json
{
  "last_updated": "2025-11-17T04:00:00Z",
  "summary": {
    "total_runs": 150,
    "completed": 145,
    "in_progress": 5,
    "success": 130,
    "failure": 15,
    "success_rate": 89.66,
    "avg_duration_seconds": 245.5,
    "recent_failures_24h": 3
  },
  "agent_workload": {
    "create-champion": {
      "total": 25,
      "success": 22,
      "failure": 2,
      "in_progress": 1
    }
  },
  "workflow_stats": {
    "copilot-graphql-assign.yml": {
      "total": 50,
      "success": 45,
      "failure": 5,
      "in_progress": 0,
      "avg_duration": 180.5
    }
  },
  "runs": [
    {
      "id": 123456789,
      "run_number": 42,
      "workflow_name": "Copilot Agent Assignment",
      "workflow_file": "copilot-graphql-assign.yml",
      "status": "completed",
      "conclusion": "success",
      "created_at": "2025-11-17T03:30:00Z",
      "duration_seconds": 234.5,
      "html_url": "https://github.com/.../runs/123456789",
      "agent_name": "create-champion"
    }
  ]
}
```

## Integration with Other Systems

### Agent Registry Integration
- Correlates workflow runs with agent assignments
- Shows which agents are actively working
- Tracks agent-specific success rates

### Issue/PR Tracking
- Links workflow runs to associated issues
- Shows PR numbers in run details
- Enables full traceability

### Learning System Integration
- Provides operational data for learning
- Feeds into self-reinforcement
- Enables performance analysis

## Troubleshooting

### Dashboard Not Loading

1. Check if `agentops-runs.json` exists in `docs/data/`
2. Verify the sync workflow has run successfully
3. Check browser console for JavaScript errors
4. Ensure GitHub Pages is enabled and deployed

### No Data Showing

1. Verify the sync workflow has completed at least once
2. Check the workflow run logs for errors
3. Ensure GitHub token has necessary permissions
4. Verify the data file contains valid JSON

### Stale Data

1. Check the "Last updated" timestamp
2. Verify the sync workflow is running on schedule
3. Manually trigger the sync workflow if needed
4. Check for workflow failures in GitHub Actions

## Future Enhancements

Potential improvements for the AgentOps dashboard:

- [ ] Real-time WebSocket updates
- [ ] Historical trend charts (30-day, 90-day)
- [ ] Alert configuration and notifications
- [ ] Custom metric definitions
- [ ] Export functionality (CSV, JSON)
- [ ] Advanced filtering (date ranges, custom queries)
- [ ] Performance anomaly detection
- [ ] Agent performance comparison
- [ ] Cost tracking (GitHub Actions minutes)
- [ ] Integration with external monitoring tools

## Related Documentation

- [GitHub Actions Workflows](WORKFLOWS.md)
- [Agent System](../AGENT_QUICKSTART.md)
- [Autonomous Pipeline](AUTONOMOUS_SYSTEM.md)
- [Monitoring Guide](MONITORING.md)

## Credits

**@create-champion** designed and implemented the AgentOps dashboard following industry best practices for observability and monitoring of autonomous AI agent systems.

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review workflow logs in GitHub Actions
3. Open an issue in the repository
4. Reference this documentation
