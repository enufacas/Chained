# Chained MCP Server

**Model Context Protocol implementation for Chained AI agents**

This server exposes all Chained agents as MCP-compatible tools, enabling integration with Claude, Cursor, OpenAI, and other MCP clients.

## 🎯 Overview

The Chained MCP Server implements the Model Context Protocol (MCP), providing standardized access to Chained's 47+ specialized AI agents. External applications can invoke agents, monitor their progress, and receive results through the MCP interface.

**Created by:** @tools-analyst  
**Mission:** JavaScript-AI-Agents Innovation (idea:28)  
**Status:** Proof of Concept

## 🚀 Quick Start

### Installation

```bash
cd tools/mcp-server
npm install
```

### Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
npm start
```

## 📋 Features

- **47+ Agent Tools**: Every Chained agent exposed as an MCP tool
- **Type-Safe**: Full TypeScript implementation with strict typing
- **Event-Driven**: Real-time events for agent actions
- **Auto-Discovery**: Automatically loads agents from `.github/agents/`
- **Standardized**: Fully MCP-compliant for maximum compatibility

## 🔧 Usage

### From TypeScript/JavaScript

```typescript
import { ChainedMCPServer } from './chained-mcp-server';

const server = new ChainedMCPServer();
await server.loadAgents();

// List available tools
console.log(server.tools);

// Invoke an agent
const result = await server.invokeAgent('tools-analyst', {
  task: 'Analyze the performance of our API endpoints',
  context: {
    files: ['src/api/*.ts'],
    priority: 'high'
  }
});

console.log(result.issueUrl);
```

### From MCP Clients (Claude, Cursor, etc.)

Once deployed, the server can be used from any MCP-compatible client:

```
# Claude Desktop config.json
{
  "mcpServers": {
    "chained-agents": {
      "url": "https://your-mcp-server.com",
      "apiKey": "your-api-key"
    }
  }
}
```

Then in Claude:
```
@chained-agents invoke_tools_analyst task="Research JavaScript frameworks"
```

## 📊 Agent Tools

Each Chained agent is exposed as an MCP tool with the naming convention:

```
invoke_{agent_name}
```

Examples:
- `invoke_tools_analyst` - Tools and infrastructure expert
- `invoke_secure_specialist` - Security implementation expert
- `invoke_accelerate_master` - Performance optimization expert
- `invoke_engineer_master` - API engineering expert

## 🔐 Input Schema

All agent tools accept the same input schema:

```typescript
{
  task: string;           // Required: Task description
  context?: {
    files?: string[];     // Relevant file paths
    references?: string[]; // Related issues/PRs
    priority?: 'low' | 'medium' | 'high' | 'critical';
  };
}
```

## 📤 Output Schema

Agent invocations return:

```typescript
{
  status: 'queued' | 'in_progress' | 'completed' | 'failed';
  issueNumber?: number;   // GitHub issue number
  issueUrl?: string;      // GitHub issue URL
  message: string;        // Status message
}
```

## 🎪 Events

The server emits events for monitoring:

```typescript
server.on('agent:loaded', (agent) => {
  console.log(`Loaded ${agent.name}`);
});

server.on('agent:invoke', ({ agentName, task }) => {
  console.log(`${agentName} invoked for: ${task}`);
});

server.on('server:ready', ({ agentCount }) => {
  console.log(`Server ready with ${agentCount} agents`);
});

server.on('server:error', (error) => {
  console.error('Server error:', error);
});
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│      MCP Client (Claude/Cursor)     │
└──────────────┬──────────────────────┘
               │ MCP Protocol
               ▼
┌─────────────────────────────────────┐
│      ChainedMCPServer               │
│  ┌─────────────────────────────┐   │
│  │  Agent Registry             │   │
│  │  • Load from .github/agents │   │
│  │  • Parse Markdown defs      │   │
│  │  • Generate MCP tools       │   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ GitHub API
               ▼
┌─────────────────────────────────────┐
│      GitHub Issues & Workflows      │
└─────────────────────────────────────┘
```

## 🔄 Integration Flow

1. **Tool Discovery**: MCP client requests available tools
2. **Tool Invocation**: Client calls `invoke_{agent_name}` with task
3. **Issue Creation**: Server creates GitHub issue with agent assignment
4. **Agent Execution**: GitHub Actions workflow triggers agent
5. **Result Tracking**: Server monitors issue for completion
6. **Response Return**: Results sent back to MCP client

## 📝 Configuration

### Environment Variables

```bash
# GitHub API Token (required for production)
GITHUB_TOKEN=your_github_token

# Repository (default: enufacas/Chained)
GITHUB_REPO=owner/repo

# Server Port (default: 3000)
MCP_PORT=3000

# Debug Mode (default: false)
DEBUG=true
```

### Deployment Options

#### Option 1: Gram Cloud (Recommended)

```bash
npm install -g @gram/cli
gram login
gram deploy --project chained-agents
```

#### Option 2: Self-Hosted

Deploy to any Node.js hosting platform:
- Heroku
- AWS Lambda
- Google Cloud Functions
- Azure Functions
- DigitalOcean App Platform

#### Option 3: Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🧪 Testing

```bash
# Run the CLI to test locally
npm run dev

# Expected output:
# ✅ Loaded agent: @tools-analyst
# ✅ Loaded agent: @secure-specialist
# ...
# 🚀 Server ready with 47 agents
```

## 🤝 Contributing

To add support for a new agent:

1. Create agent definition in `.github/agents/{agent-name}.md`
2. Server automatically discovers it on next load
3. No code changes needed!

## 📚 Related Documentation

- [Investigation Report](../../investigation-reports/javascript-ai-agents-integration-idea28.md)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io)
- [Chained Agent System](../../.github/agents/README.md)

## 🎯 Roadmap

- [x] Basic MCP server implementation
- [x] Agent auto-discovery from Markdown
- [x] Type-safe tool definitions
- [ ] Real GitHub API integration
- [ ] Webhook-based status updates
- [ ] Authentication and rate limiting
- [ ] Caching and performance optimization
- [ ] Deployment to Gram Cloud
- [ ] Production monitoring and logging

## 📞 Support

For questions about the MCP server, contact @tools-analyst or open an issue in the Chained repository.

---

**Built by @tools-analyst** as part of Mission ID: idea:28 - JavaScript-AI-Agents Innovation 🚀
