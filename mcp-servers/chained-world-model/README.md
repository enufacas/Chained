# Chained World Model MCP Server

MCP (Model Context Protocol) server providing access to Chained's world knowledge base.

**Created by:** @connector-ninja (Vint Cerf)  
**Mission:** idea:29 (Claude-Cloud-Infrastructure Integration)

## Features

- 🌍 Query world knowledge base
- 🔍 Search for patterns and trends
- 📊 Get idea/mission details
- 🤖 Access agent insights
- 🔌 Standard MCP protocol
- ☁️ Cloud deployment ready

## Installation

```bash
npm install
npm run build
```

## Usage

### Local Development

```bash
npm start
```

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "chained-world-model": {
      "command": "node",
      "args": ["/path/to/Chained/mcp-servers/chained-world-model/dist/server.js"],
      "env": {
        "CHAINED_ROOT": "/path/to/Chained"
      }
    }
  }
}
```

### Available Tools

1. **query_world_knowledge** - Search the world knowledge base
2. **get_idea_details** - Get details about specific learning missions
3. **search_patterns** - Find technology patterns and trends
4. **get_agent_insights** - Access agent performance data

## Examples

### Query World Knowledge

```
Human: Query the Chained world knowledge for Claude innovation patterns

Claude: [Uses MCP tool to query world model]
Found 3 relevant ideas about Claude:
- idea:29: Claude-Cloud-Infrastructure Innovation (7/10 relevance)
- idea:15: AI Security Trends (6/10 relevance)
- idea:8: MCP Protocol Adoption (8/10 relevance)
```

### Get Mission Details

```
Human: Get details about idea 29

Claude: [Uses MCP tool]
Idea 29: Claude-Cloud-Infrastructure Innovation
- Status: Complete
- Agent: @investigate-champion, @connector-ninja
- Deliverables: Research report, ecosystem assessment, integration implementation
- Artifacts: learnings/claude-innovation-idea29/
```

## Architecture

```
chained-world-model-mcp/
├── src/
│   └── server.ts          # Main MCP server implementation
├── dist/                  # Compiled JavaScript
├── package.json
├── tsconfig.json
└── README.md
```

## Environment Variables

- `CHAINED_ROOT` - Path to Chained repository root (required)
- `NODE_ENV` - Environment (development|production)

## Protocol

This server implements the Model Context Protocol (MCP) v0.5.0 specification.

Compatible with:
- Claude Desktop
- Claude CLI
- Any MCP-compliant client

## License

MIT

## Author

**@connector-ninja** (Vint Cerf)  
*Protocol-minded and inclusive - enabling interoperability*

## Related

- [MCP Specification](https://modelcontextprotocol.io)
- [Chained Repository](https://github.com/enufacas/Chained)
- [Mission idea:29](https://github.com/enufacas/Chained/issues/)
