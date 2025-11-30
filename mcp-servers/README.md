# Chained MCP Servers

Model Context Protocol (MCP) servers for the Chained autonomous AI ecosystem.

## 📦 Available Servers

### 1. chained-repository
**Status:** ✅ Ready  
**Created by:** @investigate-champion (Ada Lovelace)  
**Purpose:** Repository internals and agent operations

Provides access to:
- Agent system (registry, metrics, Hall of Fame)
- Learning data (TLDR, Hacker News, GitHub Trending)
- Repository insights (code patterns, tools)
- Workflow & automation data
- GitHub Pages data

**[Documentation →](./chained-repository/README.md)**

**Quick Start:**
```bash
cd chained-repository
npm install && npm run build
```

### 2. gcloud-mcp (External)
**Status:** ✅ Ready  
**Maintained by:** [Google Cloud](https://github.com/googleapis/gcloud-mcp)  
**Purpose:** Google Cloud Platform CLI integration

Provides access to:
- Execute gcloud CLI commands via natural language
- Google Cloud resource management
- Cloud infrastructure automation
- GCP project and service operations

**Package:** `@google-cloud/gcloud-mcp`  
**[External Documentation →](https://github.com/googleapis/gcloud-mcp)**

**Quick Start:**
```bash
# No local installation needed - uses npx
npx @google-cloud/gcloud-mcp
```

> ⚠️ **For GitHub Copilot Coding Agent:**  
> The gcloud-mcp server must be configured in **TWO places**:
> 1. **Repository Settings → Copilot → Coding agent → MCP section** - Add the MCP server JSON
> 2. **copilot-setup-steps.yml** - Provides GCP authentication (already configured)
>
> See [gcloud-mcp Copilot Setup Guide](../docs/guides/GCLOUD_MCP_COPILOT_SETUP.md) for full instructions.

### 3. chained-world-model
**Status:** 🚧 Planned  
**Purpose:** External world knowledge and trends

Will provide access to:
- Real-world technology trends
- Company and product information
- Developer ecosystem insights
- Technology adoption patterns

**[Documentation →](./chained-world-model/README.md)**

## 🎯 Purpose

These MCP servers extend Claude Desktop and other MCP clients with specialized knowledge about the Chained project, Google Cloud Platform, and the wider tech ecosystem.

### Separation of Concerns

- **chained-repository**: Internal repository data (what agents need to work)
- **gcloud-mcp**: Google Cloud Platform access (what agents need to interact with GCP)
- **chained-world-model**: External world knowledge (what agents need to understand context)

## 🚀 Quick Setup

### Prerequisites
- Node.js >= 18.0.0 for chained-repository
- Node.js >= 20.0.0 for gcloud-mcp (**required** - package uses features only available in Node.js 20+)
- Claude Desktop (or another MCP client)
- Chained repository cloned locally
- gcloud CLI installed (for gcloud-mcp) - [Install Guide](https://cloud.google.com/sdk/docs/install)

### Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "node",
      "args": [
        "/absolute/path/to/Chained/mcp-servers/chained-repository/dist/server.js"
      ]
    },
    "gcloud": {
      "command": "npx",
      "args": ["-y", "@google-cloud/gcloud-mcp"]
    }
  }
}
```

Replace `/absolute/path/to/Chained` with your actual repository path.

### Restart Claude Desktop

Close and reopen Claude Desktop for changes to take effect.

## 📚 Documentation

- [Chained Repository MCP](./chained-repository/README.md) - Full documentation
- [Quick Start Guide](./chained-repository/QUICKSTART.md) - 5-minute setup
- [gcloud-mcp](https://github.com/googleapis/gcloud-mcp) - Google Cloud MCP server docs
- [gcloud-mcp Copilot Setup](../docs/guides/GCLOUD_MCP_COPILOT_SETUP.md) - Environment secrets configuration
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP docs

## 🛠️ Development

### Building a Server

```bash
cd server-name
npm install
npm run build
```

### Watch Mode (Development)

```bash
npm run dev
```

### Testing

```bash
npm test
```

## 🔍 Usage Examples

### Example 1: Agent Performance Check

```typescript
// In Claude with MCP server configured
"Can you check the Hall of Fame agents and show me their performance metrics?"
```

Claude will automatically use:
- `get_hall_of_fame()` - to get top performers
- `get_agent_metrics()` - to get detailed metrics

### Example 2: Trend Analysis

```typescript
"What are the latest tech trends from our learning data?"
```

Claude will use:
- `get_learning_data()` - to fetch recent learnings
- `get_thematic_analysis()` - to get trend analysis

### Example 3: Agent Selection

```typescript
"Which agent should I assign to an API testing issue?"
```

Claude will use:
- `search_agent_patterns({ keywords: ["api", "testing"] })`
- `get_agent_metrics()` - to compare performance

### Example 4: GCP Cloud Operations (gcloud-mcp)

```typescript
"List all the compute instances in my project"
```

Claude will use:
- `run_gcloud_command({ command: "gcloud compute instances list" })`

### Example 5: GCP Resource Management (gcloud-mcp)

```typescript
"Create a new Cloud Storage bucket named my-new-bucket in us-central1"
```

Claude will use:
- `run_gcloud_command({ command: "gcloud storage buckets create gs://my-new-bucket --location=us-central1" })`

## 🏗️ Architecture

```
mcp-servers/
├── chained-repository/          # Repository data server
│   ├── src/
│   │   └── server.ts           # TypeScript implementation
│   ├── dist/                   # Compiled JavaScript
│   ├── package.json
│   ├── tsconfig.json
│   ├── README.md               # Full documentation
│   └── QUICKSTART.md          # Quick setup guide
│
├── chained-world-model/         # World knowledge server (planned)
│   └── README.md
│
└── README.md                    # This file
```

## 🤝 Integration with Agents

All autonomous agents in the Chained ecosystem can use these MCP servers through:

1. **Claude Desktop**: When agents work interactively
2. **GitHub Copilot**: When configured with MCP support
3. **Custom Workflows**: Through direct API calls

### Agent Benefits

- **@investigate-champion**: Access learning data and thematic analysis
- **@troubleshoot-expert**: View workflow data and mission reports
- **@engineer-master**: Query agent patterns and specializations
- **All agents**: Access performance metrics and repository insights

## 📊 Performance

Both servers are designed for:
- **Fast Startup**: &lt; 100ms to initialize
- **Low Memory**: &lt; 50MB typical usage
- **Quick Responses**: &lt; 10ms for most queries
- **Local Only**: No network calls, all data is local

## 🔐 Security

- **Read-Only**: Servers only read data, never write
- **Path Validation**: All file paths are validated
- **No Credentials**: No tokens or secrets required
- **Local Execution**: Runs on your machine only

## 🐛 Troubleshooting

### Server Not Appearing

1. Check config file path
2. Verify absolute paths (not relative)
3. Restart Claude Desktop completely
4. Check for JSON syntax errors

### Build Failures

```bash
# Clean rebuild
rm -rf dist node_modules
npm install
npm run build
```

### Runtime Errors

Check that:
- You're running from the Chained repository
- Required data files exist in the repository
- Node.js version is >= 18.0.0

## 📈 Roadmap

- [x] **chained-repository** - Repository data server (v1.0.0)
- [x] **gcloud-mcp** - Google Cloud Platform integration (external)
- [ ] **chained-world-model** - World knowledge server (planned)
- [ ] **Testing Suite** - Comprehensive tests for all tools
- [ ] **Performance Monitoring** - Track server usage and performance
- [ ] **CLI Tools** - Command-line utilities for testing

## 🙏 Acknowledgments

- **@investigate-champion** (Ada Lovelace) - Created chained-repository MCP server
- **Google Cloud Team** - gcloud-mcp server ([googleapis/gcloud-mcp](https://github.com/googleapis/gcloud-mcp))
- **Model Context Protocol Team** - Excellent SDK and documentation
- **Anthropic** - Claude Desktop and MCP support

## 📝 License

MIT License - Part of the Chained autonomous AI ecosystem.

## 📞 Support

For issues or questions:
1. Check the [QUICKSTART.md](./chained-repository/QUICKSTART.md) guide
2. Read individual server documentation
3. Open an issue in the Chained repository
4. Mention **@investigate-champion** for MCP server questions

---

**Making repository data accessible to autonomous agents** 🚀
