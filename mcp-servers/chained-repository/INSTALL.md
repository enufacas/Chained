# Installing Chained Repository MCP Globally

**Created by @APIs-architect**

This guide explains how to make the Chained Repository MCP server available globally to all agents, including GitHub Copilot, Claude Desktop, and other MCP-compatible clients.

## 📦 Installation Methods

### Method 1: NPM Global Install (Recommended)

Install globally via npm:

```bash
npm install -g @chained/repository-mcp
```

Then configure your MCP client to use the global command:

```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "chained-repository-mcp"
    }
  }
}
```

### Method 2: NPM Package (Local Project)

Install in your project:

```bash
npm install @chained/repository-mcp
```

Then use via npx:

```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "npx",
      "args": ["@chained/repository-mcp"]
    }
  }
}
```

### Method 3: Direct from Repository

Clone and build locally:

```bash
git clone https://github.com/enufacas/Chained.git
cd Chained/mcp-servers/chained-repository
npm install
npm run build
```

Then reference the absolute path:

```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "node",
      "args": ["/absolute/path/to/Chained/mcp-servers/chained-repository/dist/server.js"]
    }
  }
}
```

## 🤖 Configuration for Different Clients

### Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "chained-repository-mcp",
      "description": "Access to Chained agent system, learnings, and repository insights"
    }
  }
}
```

### GitHub Copilot (GitHub Actions)

Add to your workflow configuration:

```yaml
# .github/workflows/copilot-agent.yml
- name: Install Chained MCP Server
  run: npm install -g @chained/repository-mcp

- name: Configure Copilot with MCP
  env:
    MCP_CONFIG: |
      {
        "mcpServers": {
          "chained-repository": {
            "command": "chained-repository-mcp"
          }
        }
      }
  run: |
    echo "$MCP_CONFIG" > /tmp/mcp-config.json
    export MCP_SERVERS_CONFIG=/tmp/mcp-config.json
```

### Cursor IDE

Add to Cursor settings (`Settings > MCP Servers`):

```json
{
  "chained-repository": {
    "command": "chained-repository-mcp",
    "description": "Chained Repository Access"
  }
}
```

### Continue.dev

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "chained-repository",
      "command": "chained-repository-mcp"
    }
  ]
}
```

### Zed Editor

Add to Zed settings (`~/.config/zed/settings.json`):

```json
{
  "language_servers": {
    "chained-repository": {
      "command": "chained-repository-mcp"
    }
  }
}
```

## 🔐 Environment Variables

The MCP server can be configured with environment variables:

```bash
# Repository path (default: auto-detect from installation)
export CHAINED_REPO_PATH=/path/to/Chained

# Enable debug logging
export CHAINED_MCP_DEBUG=true

# Custom cache directory
export CHAINED_MCP_CACHE_DIR=~/.chained-mcp-cache
```

## 🧪 Testing Installation

### Test 1: Verify Command

```bash
which chained-repository-mcp
# Should output: /usr/local/bin/chained-repository-mcp (or similar)
```

### Test 2: Run Server Directly

```bash
chained-repository-mcp
# Server will wait for stdin commands (MCP protocol)
# Press Ctrl+C to exit
```

### Test 3: Use MCP Inspector

```bash
npm install -g @modelcontextprotocol/inspector
mcp-inspector chained-repository-mcp
```

Opens a web interface to test MCP tools interactively.

### Test 4: Test from Claude/Cursor

In your MCP client, try:

```
Can you list the agent specializations in the Chained repository?
```

The MCP server should respond with agent data.

## 🔄 Updating

### Global Install

```bash
npm update -g @chained/repository-mcp
```

### Local Install

```bash
npm update @chained/repository-mcp
```

### Direct Repository

```bash
cd /path/to/Chained/mcp-servers/chained-repository
git pull
npm install
npm run build
```

## 📊 Available Tools

Once installed, the following MCP tools are available:

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

### Server Not Found

**Symptom:** `command not found: chained-repository-mcp`

**Solution:**
1. Verify npm global bin is in PATH:
   ```bash
   npm config get prefix
   # Add <prefix>/bin to your PATH
   ```
2. Reinstall globally:
   ```bash
   npm install -g @chained/repository-mcp
   ```

### Permission Denied

**Symptom:** `EACCES: permission denied`

**Solution:**
```bash
sudo npm install -g @chained/repository-mcp
```

Or configure npm to install globally without sudo:
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g @chained/repository-mcp
```

### Server Crashes

**Symptom:** MCP server crashes on startup

**Solution:**
1. Check Node.js version (requires >=18.0.0):
   ```bash
   node --version
   ```
2. Enable debug mode:
   ```bash
   CHAINED_MCP_DEBUG=true chained-repository-mcp
   ```
3. Check repository path:
   ```bash
   export CHAINED_REPO_PATH=/path/to/Chained
   chained-repository-mcp
   ```

### No Data Returned

**Symptom:** MCP tools return empty data

**Solution:**
1. Verify repository structure:
   ```bash
   ls $CHAINED_REPO_PATH/.github/agent-system/
   ls $CHAINED_REPO_PATH/learnings/
   ```
2. Ensure repository is cloned and up-to-date:
   ```bash
   cd $CHAINED_REPO_PATH
   git pull
   ```

### GitHub Copilot Not Detecting MCP

**Symptom:** Copilot doesn't use MCP tools

**Solution:**
1. Verify MCP_SERVERS_CONFIG environment variable is set
2. Check workflow has proper permissions:
   ```yaml
   permissions:
     contents: read
     issues: write
   ```
3. Ensure npm install succeeded in workflow
4. Check Copilot agent has access to MCP configuration

## 📚 Related Documentation

- [QUICKSTART.md](./QUICKSTART.md) - 5-minute setup guide
- [README.md](./README.md) - Complete MCP server documentation
- [MCP Protocol Spec](https://spec.modelcontextprotocol.io) - Official MCP specification

## 🤝 Contributing

To improve global availability:

1. Test on different platforms (macOS, Linux, Windows)
2. Report installation issues
3. Submit platform-specific configuration examples
4. Improve documentation

## 📞 Support

For installation help:
- **@APIs-architect** - MCP global availability
- **@investigate-champion** - MCP server implementation
- Open an issue at: https://github.com/enufacas/Chained/issues

---

**Made globally available by @APIs-architect** 🌍✨
