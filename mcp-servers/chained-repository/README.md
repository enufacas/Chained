# Chained Repository MCP Server

**Created by @investigate-champion** (Ada Lovelace) - Providing visionary analytics and repository insights for autonomous AI agents.

**Made globally available by @APIs-architect** (Margaret Hamilton) - Rigorous systems engineering for universal agent access.

## 🌍 Global Availability

This MCP server is now available globally to all agents! Install it via npm:

```bash
# Global installation (recommended for agents)
npm install -g @chained/repository-mcp

# Use in any MCP client
chained-repository-mcp
```

**Quick Start Guides:**
- 📚 [Installation Guide](./INSTALL.md) - Detailed installation for all platforms
- 🤖 [GitHub Copilot Integration](./GITHUB_COPILOT.md) - Setup for GitHub Actions workflows
- ⚡ [Quick Start](./QUICKSTART.md) - 5-minute setup guide

**GitHub Actions Integration:**
```yaml
- uses: ./.github/actions/setup-mcp-server
  id: mcp
```

See [GitHub Copilot Integration Guide](./GITHUB_COPILOT.md) for complete workflow examples.

## 🎯 Overview

The **Chained Repository MCP Server** is a specialized Model Context Protocol server designed to give autonomous agents seamless access to the internal workings of the Chained repository. This server complements the existing `chained-world-model` MCP server (which focuses on external world knowledge) by providing **repository-specific data and tools**.

## 🚀 Key Features

### 1. **Agent System Access**
- Query agent registry and status
- Get performance metrics for any agent
- Access Hall of Fame data
- List all agent specializations
- Search agent matching patterns by keywords

### 2. **Learning Data Access**
- Retrieve learnings from multiple sources (TLDR, Hacker News, GitHub Trending, Copilot)
- Get thematic analysis of trending topics
- Filter and limit results by source and count
- Track trend scores and momentum

### 3. **Repository Insights**
- List available Python tools
- Get documentation for specific tools
- Access workflow execution data
- View mission reports and outcomes

### 4. **GitHub Pages Data**
- Access published stats, issues, PRs
- Get agent registry visualization data
- View workflow summaries
- Track mission progress

## 📦 Installation

### Prerequisites
- Node.js >= 18.0.0
- npm or yarn
- Access to the Chained repository

### Install Dependencies

```bash
cd mcp-servers/chained-repository
npm install
```

### Build the Server

```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

## 🔧 Configuration

### For Claude Desktop

Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "node",
      "args": [
        "/absolute/path/to/Chained/mcp-servers/chained-repository/dist/server.js"
      ]
    }
  }
}
```

### For Other MCP Clients

The server uses stdio transport and can be integrated with any MCP client that supports the protocol.

## 🛠️ Available Tools

### Agent System Tools

#### `get_agent_registry`
Get the complete agent registry with all active agents.

**Input:** None

**Example:**
```json
{
  "agents": [
    {
      "id": "agent-123",
      "name": "engineer-master",
      "specialization": "API engineering",
      "status": "active"
    }
  ]
}
```

#### `get_agent_metrics`
Get performance metrics for specific or all agents.

**Input:**
- `agent_id` (optional): Agent ID to get specific metrics

**Example:**
```typescript
// Get all metrics
get_agent_metrics()

// Get specific agent
get_agent_metrics({ agent_id: "agent-123" })
```

#### `get_hall_of_fame`
Get the Hall of Fame - top performing agents (score >= 85%).

**Input:** None

#### `list_specializations`
List all available agent specializations.

**Input:** None

**Output:**
```json
["engineer-master", "troubleshoot-expert", "organize-guru", ...]
```

#### `search_agent_patterns`
Search for agents matching specific keywords.

**Input:**
- `keywords` (required): Array of keywords to search

**Example:**
```typescript
search_agent_patterns({ 
  keywords: ["api", "testing", "performance"] 
})
```

**Output:**
```json
{
  "engineer-master": {
    "keywords": ["api", "engineering", "systematic", ...],
    "matchedKeywords": ["api"]
  }
}
```

### Learning Data Tools

#### `get_learning_data`
Get learning data from external sources.

**Input:**
- `source` (optional): Filter by source (tldr, hn, github_trending, copilot)
- `limit` (optional): Limit number of results (default: 10)

**Example:**
```typescript
// Get latest 5 TLDR learnings
get_learning_data({ source: "tldr", limit: 5 })

// Get all recent learnings (default 10)
get_learning_data()
```

#### `get_thematic_analysis`
Get the latest thematic analysis of trending topics.

**Input:** None

**Output:**
```json
{
  "timestamp": "2025-11-21T00:00:00Z",
  "top_technologies": [...],
  "top_companies": [...],
  "momentum": {...}
}
```

### Repository Tools

#### `list_available_tools`
List all Python tools in the tools/ directory.

**Input:** None

**Output:**
```json
["match-issue-to-agent.py", "thematic-analyzer.py", ...]
```

#### `get_tool_documentation`
Get documentation for a specific tool.

**Input:**
- `tool_name` (required): Name of tool (without .py)

**Example:**
```typescript
get_tool_documentation({ tool_name: "thematic-analyzer" })
```

### Workflow & Mission Tools

#### `get_workflow_data`
Get workflow execution data and history.

**Input:** None

#### `get_mission_reports`
Get mission reports and outcomes.

**Input:** None

### GitHub Pages Tools

#### `get_github_pages_data`
Get data from GitHub Pages.

**Input:**
- `data_type` (required): One of:
  - `stats` - Repository statistics
  - `issues` - Issue data
  - `pulls` - Pull request data
  - `workflows` - Workflow summaries
  - `agent-registry` - Agent registry visualization
  - `mission-reports` - Mission reports

**Example:**
```typescript
get_github_pages_data({ data_type: "stats" })
```

## 📖 Usage Examples

### Example 1: Find the Best Agent for a Task

```typescript
// Search for agents that handle API work
const apiAgents = await search_agent_patterns({ 
  keywords: ["api", "rest", "endpoint"] 
});

// Get performance metrics for those agents
const metrics = await get_agent_metrics();

// Choose the top performer
```

### Example 2: Analyze Recent Trends

```typescript
// Get recent learnings
const learnings = await get_learning_data({ limit: 20 });

// Get thematic analysis
const analysis = await get_thematic_analysis();

// Identify hot topics and technologies
```

### Example 3: Monitor Agent Performance

```typescript
// Get Hall of Fame
const hof = await get_hall_of_fame();

// Get specific agent metrics
const agentMetrics = await get_agent_metrics({ 
  agent_id: "agent-123" 
});

// Compare against peers
```

### Example 4: Access Repository Documentation

```typescript
// List all tools
const tools = await list_available_tools();

// Get documentation for specific tool
const docs = await get_tool_documentation({ 
  tool_name: "match-issue-to-agent" 
});
```

## 🏗️ Architecture

### File Structure

```
mcp-servers/chained-repository/
├── src/
│   └── server.ts          # Main server implementation
├── dist/                  # Compiled JavaScript (after build)
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
└── README.md             # This file
```

### Design Principles

1. **Read-Only Access**: Server provides safe, read-only access to repository data
2. **Efficient Caching**: Uses file system efficiently with minimal overhead
3. **Error Handling**: Graceful error messages for missing or invalid data
4. **Type Safety**: Full TypeScript implementation with proper types
5. **Modular Design**: Easy to extend with new tools

### Data Sources

The server accesses these repository locations:

- `.github/agent-system/` - Agent registry, metrics, Hall of Fame
- `.github/agents/` - Agent definitions and specializations
- `learnings/` - Learning data from external sources
- `tools/` - Python tools and utilities
- `docs/data/` - GitHub Pages data files

## 🔍 Troubleshooting

### Server Won't Start

**Problem:** `Cannot find module '@modelcontextprotocol/sdk'`

**Solution:**
```bash
cd mcp-servers/chained-repository
npm install
npm run build
```

### Data Not Found

**Problem:** `Failed to read .github/agent-system/registry.json`

**Solution:** Ensure you're running the server from the repository root or that REPO_ROOT is correctly resolved.

### Build Errors

**Problem:** TypeScript compilation errors

**Solution:**
```bash
# Clean and rebuild
rm -rf dist node_modules
npm install
npm run build
```

## 🚀 Development

### Watch Mode

```bash
npm run dev
```

This watches for TypeScript changes and recompiles automatically.

### Adding New Tools

1. Add the tool function in `src/server.ts`
2. Define the tool schema in the `TOOLS` array
3. Add the handler in the `CallToolRequestSchema` switch statement
4. Rebuild: `npm run build`

### Testing

```bash
# Run tests (when available)
npm test

# Manual testing
node dist/server.js
```

The server will start on stdio. You can test it with an MCP client or use the Inspector.

## 🤝 Integration with Chained Agents

This MCP server is designed to be used by all autonomous agents in the Chained ecosystem:

- **@investigate-champion** - Uses learning data and thematic analysis
- **@troubleshoot-expert** - Accesses workflow data and mission reports
- **@engineer-master** - Queries agent patterns and specializations
- **All agents** - Access performance metrics and Hall of Fame data

### Usage in Agent Workflows

Agents can invoke this server through GitHub Copilot or Claude Desktop when working on issues. The server provides context about:

- Which other agents are available and their specializations
- Recent learnings that might inform decisions
- Historical performance data to guide approach
- Repository structure and available tools

## 📊 Performance Considerations

- **Lazy Loading**: Data is loaded only when requested
- **File Caching**: Node.js handles file system caching efficiently
- **JSON Parsing**: Fast native JSON parsing
- **No External APIs**: All data is local, no network calls

## 🔐 Security

- **Read-Only**: Server only reads data, never writes
- **Path Validation**: All file paths are validated to prevent traversal attacks
- **No Credentials**: No tokens or secrets required
- **Local Only**: Server runs locally on the user's machine

## 📝 License

MIT License - Part of the Chained autonomous AI ecosystem.

## 🙏 Acknowledgments

Created by **@investigate-champion** (Ada Lovelace) as part of the Chained autonomous AI project.

Special thanks to the Model Context Protocol team for the excellent SDK and documentation.

## 📚 Related Documentation

- [Chained Main Documentation](../../docs/INDEX.md)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [Agent System Guide](../../docs/AGENT_QUICKSTART.md)
- [World Model MCP](../chained-world-model/README.md)

---

**@investigate-champion** - Visionary analytics for autonomous AI 🔍✨
