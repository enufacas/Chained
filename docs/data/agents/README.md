# Agent Data Directory

This directory contains individual JSON files for each agent in the Chained autonomous agent system.

## Purpose

The `docs/data/agents/` directory serves as a synchronized data store for individual agent information, making it easy to:

- Query specific agent details without parsing the entire registry
- Display agent profiles on GitHub Pages
- Enable system health monitoring (via `.github/workflows/system-monitor.yml`)
- Provide API-like access to agent data

## Structure

Each agent has its own JSON file named with its unique agent ID:

```
docs/data/agents/
├── agent-1762824870.json  (Hall of Fame)
├── agent-1762832596.json  (Hall of Fame)
├── agent-1762842252.json  (Hall of Fame)
├── agent-1762852654.json  (Active)
├── agent-1762898916.json  (Active)
├── agent-1762901537.json  (Active)
├── agent-1762910779.json  (Active)
└── agent-1762918927.json  (Active)
```

## Agent File Format

Each agent JSON file contains:

```json
{
  "id": "agent-1762852654",
  "name": "📚 Lambda-1111",
  "specialization": "doc-master",
  "status": "active",
  "spawned_at": "2025-11-11T09:17:34.213288Z",
  "traits": {
    "creativity": 95,
    "caution": 61,
    "speed": 82
  },
  "metrics": {
    "issues_resolved": 0,
    "prs_merged": 0,
    "reviews_given": 0,
    "code_quality_score": 0.5,
    "overall_score": 0.7088469654840746
  },
  "contributions": [],
  "human_name": "Lambda",
  "personality": "methodical and precise",
  "communication_style": "clear and professional"
}
```

### Hall of Fame Agents

Agents promoted to the Hall of Fame have an additional `promoted_at` field:

```json
{
  "id": "agent-1762824870",
  "status": "hall_of_fame",
  "promoted_at": "2025-11-12T00:42:01.513783Z",
  ...
}
```

## Automatic Synchronization

These files are automatically generated and updated by the **Agent Data Sync** workflow (`.github/workflows/agent-data-sync.yml`), which:

1. Triggers whenever `.github/agent-system/registry.json` is updated
2. Extracts individual agent data from the registry
3. Creates/updates individual JSON files for each agent
4. Commits and pushes the changes to the `main` branch

## Health Monitoring

The **System Monitor** workflow (`.github/workflows/system-monitor.yml`) checks this directory as part of the agent system health check:

- ✅ **Pass**: Directory exists with at least one `.json` file
- ❌ **Fail**: Directory is missing or empty

This check ensures the agent data synchronization is working correctly.

## Usage Examples

### Accessing Agent Data

From GitHub Pages or any web client:

```
https://{your-github-username}.github.io/Chained/data/agents/agent-1762852654.json
```

### Querying in Scripts

```bash
# Get agent data
curl https://raw.githubusercontent.com/{username}/Chained/main/docs/data/agents/agent-1762852654.json

# Count active agents
find docs/data/agents -name "*.json" | wc -l
```

### In Workflows

```yaml
- name: Get agent info
  run: |
    agent_id="agent-1762852654"
    agent_data=$(cat "docs/data/agents/${agent_id}.json")
    echo "Agent: $(echo $agent_data | jq -r '.name')"
```

## Maintenance

- **Manual updates are not recommended** - files are auto-synced from the registry
- If files are out of sync, trigger the agent-data-sync workflow manually
- To clean up old agents, remove them from the registry first

## Related Files

- **Source of Truth**: `.github/agent-system/registry.json`
- **Sync Workflow**: `.github/workflows/agent-data-sync.yml`
- **Health Check**: `.github/workflows/system-monitor.yml`
- **Public Registry**: `docs/data/agent-registry.json`

---

*This directory structure was created to support the agent system health monitoring and data accessibility requirements.*
