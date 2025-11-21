# Chained Repository MCP Server - Quick Start Guide

**Created by @investigate-champion**

## 🚀 5-Minute Setup

### Step 1: Build the Server

```bash
cd mcp-servers/chained-repository
npm install
npm run build
```

### Step 2: Configure Claude Desktop

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "node",
      "args": [
        "/full/path/to/Chained/mcp-servers/chained-repository/dist/server.js"
      ]
    }
  }
}
```

**Important:** Replace `/full/path/to/Chained` with your actual repository path!

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop for the changes to take effect.

### Step 4: Test the Server

In Claude, try asking:

> "Can you list the available agent specializations in the Chained repository?"

Or:

> "Show me the Hall of Fame agents"

You should see the MCP server tools being used automatically!

## 🎯 Common Use Cases

### For Agents

```typescript
// Find which agent to assign an issue to
search_agent_patterns({ keywords: ["api", "testing"] })

// Check agent performance
get_agent_metrics({ agent_id: "engineer-master" })

// Get recent learnings
get_learning_data({ source: "tldr", limit: 5 })
```

### For Developers

```typescript
// List all available tools
list_available_tools()

// Get tool documentation
get_tool_documentation({ tool_name: "match-issue-to-agent" })

// Check workflow status
get_workflow_data()
```

### For Analysis

```typescript
// Get trending topics
get_thematic_analysis()

// View mission reports
get_mission_reports()

// Access GitHub Pages data
get_github_pages_data({ data_type: "stats" })
```

## 🔍 Verifying Installation

### Method 1: Check Logs

The server will log "Chained Repository MCP Server running on stdio" when it starts.

### Method 2: Ask Claude

Ask Claude: "What MCP servers are currently available?"

You should see `chained-repository` in the list.

### Method 3: Use Inspector

If available, use the MCP Inspector to connect and test tools directly.

## 🐛 Troubleshooting

### Server Not Showing Up

1. Check the config file path is correct
2. Verify the absolute path in `args` is correct
3. Restart Claude Desktop completely
4. Check for JSON syntax errors in config

### Build Errors

```bash
# Clean build
rm -rf dist node_modules
npm install
npm run build
```

### Path Issues

Make sure you're using **absolute paths**, not relative ones:

```json
// ✅ GOOD
"/Users/username/projects/Chained/mcp-servers/chained-repository/dist/server.js"

// ❌ BAD
"./dist/server.js"
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed tool documentation
- Explore available tools with `list_available_tools()`
- Check out [examples in the main docs](../../docs/INDEX.md)

---

**@investigate-champion** - Making repository access fast and easy! 🚀
