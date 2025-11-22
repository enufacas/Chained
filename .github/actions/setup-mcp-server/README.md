# Setup Chained MCP Server Action

**Created by @APIs-architect**

A GitHub Actions composite action that installs and configures the Chained Repository MCP server for use by GitHub Copilot and other AI agents.

## 🎯 Purpose

This action makes it easy to add MCP (Model Context Protocol) capabilities to any workflow, giving agents access to:
- Agent system registry, metrics, and hall of fame
- Learning data from TLDR, Hacker News, GitHub Trending
- Repository insights and code patterns
- Workflow and automation tools
- GitHub Pages data and statistics

## 📦 Usage

### Basic Usage

```yaml
steps:
  - uses: actions/checkout@v4
  
  - name: Setup MCP Server
    uses: ./.github/actions/setup-mcp-server
    id: mcp
  
  - name: Use MCP in Copilot
    # Your Copilot agent can now access MCP tools
    run: |
      echo "MCP Config: ${{ steps.mcp.outputs.config-path }}"
```

### With Debug Logging

```yaml
- name: Setup MCP Server
  uses: ./.github/actions/setup-mcp-server
  with:
    debug: 'true'
```

### With Custom Cache Directory

```yaml
- name: Setup MCP Server
  uses: ./.github/actions/setup-mcp-server
  with:
    cache-dir: '/tmp/custom-mcp-cache'
```

## 📥 Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `debug` | Enable debug logging | No | `false` |
| `cache-dir` | Custom cache directory | No | `/tmp/mcp-cache` |

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `config-path` | Path to MCP configuration JSON file |
| `server-path` | Path to MCP server executable |
| `status` | Installation status (`success` or `failed`) |

## 🌍 Environment Variables Set

This action sets the following environment variables for subsequent steps:

- `MCP_SERVERS_CONFIG` - Path to MCP configuration file
- `CHAINED_REPO_PATH` - Path to Chained repository
- `CHAINED_MCP_DEBUG` - Debug mode setting
- `CHAINED_MCP_CACHE_DIR` - Cache directory path

## 🔧 Complete Example

```yaml
name: "Agent Task with MCP"

on:
  issues:
    types: [opened]

jobs:
  execute-task:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Setup MCP Server
        uses: ./.github/actions/setup-mcp-server
        id: mcp
        with:
          debug: 'true'
      
      - name: Verify MCP Setup
        run: |
          echo "✅ MCP configured at: ${{ steps.mcp.outputs.config-path }}"
          echo "✅ Server path: ${{ steps.mcp.outputs.server-path }}"
          echo "✅ Status: ${{ steps.mcp.outputs.status }}"
          
          # Test MCP environment
          echo "MCP_SERVERS_CONFIG=$MCP_SERVERS_CONFIG"
          echo "CHAINED_REPO_PATH=$CHAINED_REPO_PATH"
      
      - name: Run Copilot with MCP
        # Your Copilot agent execution here
        # It will automatically have access to MCP tools
        run: |
          echo "Copilot can now use MCP tools like:"
          echo "  - list_agents"
          echo "  - get_agent_metrics"
          echo "  - search_learnings"
          echo "  - match_issue_to_agent"
```

## 🧪 Testing

After using this action, verify MCP is configured:

```bash
# Check MCP server is installed
which chained-repository-mcp

# Check configuration file exists
cat $MCP_SERVERS_CONFIG

# Verify environment variables
echo $CHAINED_REPO_PATH
echo $CHAINED_MCP_DEBUG
```

## 📚 Available MCP Tools

Once installed, these tools are available to AI agents:

### Agent System
- `list_agents` - List all agent specializations
- `get_agent_details` - Get detailed agent information
- `search_agent_patterns` - Find agents matching keywords
- `get_agent_metrics` - View agent performance metrics
- `get_hall_of_fame` - See top-performing agents

### Learning Data
- `get_learning_data` - Access TLDR, HN, GitHub Trending data
- `search_learnings` - Search through learning history
- `get_thematic_analysis` - View learning themes and trends

### Repository Insights
- `get_tool_documentation` - Access tool documentation
- `list_available_tools` - List automation tools
- `get_workflow_data` - View workflow information
- `get_github_pages_data` - Access GitHub Pages stats

### Automation
- `match_issue_to_agent` - Find best agent for an issue
- `get_mission_reports` - View mission completion data

## 🐛 Troubleshooting

### Installation Fails

If the action fails to install the MCP server:

1. Check Node.js version is >=18.0.0
2. Verify npm is available
3. Check network connectivity
4. Enable debug mode for more details

### MCP Tools Not Available

If MCP tools aren't accessible:

1. Verify the action completed successfully
2. Check environment variables are set
3. Ensure repository structure is correct
4. Review workflow logs for errors

### Permission Issues

If you see permission errors:

```yaml
# Add explicit permissions to your job
permissions:
  contents: read
  issues: write
```

## 🤝 Contributing

To improve this action:

1. Test on different runner OS (ubuntu, windows, macos)
2. Add error recovery mechanisms
3. Improve validation and testing
4. Submit feedback and issues

## 📞 Support

For help with this action:
- **@APIs-architect** - Action creator and maintainer
- **@investigate-champion** - MCP server implementation
- Open an issue at: https://github.com/enufacas/Chained/issues

## Related Documentation

- [MCP Server Documentation](../../mcp-servers/chained-repository/README.md)
- [Installation Guide](../../mcp-servers/chained-repository/INSTALL.md)
- [GitHub Copilot Integration](../../mcp-servers/chained-repository/GITHUB_COPILOT.md)

---

**Built by @APIs-architect** to make MCP globally available to all agents 🌍✨
