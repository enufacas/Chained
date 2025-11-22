# Quick Reference Card

**Chained Repository MCP Server** - Made globally available by @APIs-architect

## 🚀 Installation

### Global (when published to npm)
```bash
npm install -g @chained/repository-mcp
```

### Local Development
```bash
cd mcp-servers/chained-repository
npm install && npm run build
node dist/server.js
```

## ⚙️ Configuration

### Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "chained-repository-mcp",
      "env": {
        "CHAINED_REPO_PATH": "/path/to/Chained"
      }
    }
  }
}
```

### Cline (VSCode)
Add to VSCode settings or `.vscode/settings.json`:
```json
{
  "cline.mcpServers": {
    "chained-repository": {
      "command": "chained-repository-mcp",
      "env": {
        "CHAINED_REPO_PATH": "${workspaceFolder}"
      }
    }
  }
}
```

### GitHub Actions
```yaml
- uses: ./.github/actions/setup-mcp-server
  id: mcp
```

## 🛠️ Available Tools

| Tool | Purpose |
|------|---------|
| `get_agent_details` | Get agent metadata |
| `list_agents` | List all agents |
| `search_agents` | Find agents by keyword |
| `match_issue_to_agent` | Intelligent agent matching |
| `get_workflow_info` | Workflow details |
| `list_workflows` | List all workflows |
| `search_learnings` | Search learnings |
| `list_available_tools` | List Python tools |
| `get_github_pages_data` | GitHub Pages data |

## 📖 Documentation

| Guide | Location | Purpose |
|-------|----------|---------|
| Installation | `INSTALL.md` | Platform-specific setup |
| Quick Start | `QUICKSTART.md` | 5-minute setup |
| Copilot Integration | `GITHUB_COPILOT.md` | GitHub Actions |
| Publishing | `PUBLISHING.md` | npm publishing |
| Full Docs | `README.md` | Complete reference |
| Changelog | `CHANGELOG.md` | Version history |

## 🧪 Testing

### Test Server Locally
```bash
cd mcp-servers/chained-repository
npm run build
node dist/server.js  # Should output: "Chained Repository MCP Server running on stdio"
```

### Test npm Package
```bash
npm pack --dry-run  # Shows what would be published
```

### Test GitHub Action
Run workflow: `.github/workflows/example-copilot-mcp.yml`

## 🆘 Troubleshooting

### Server doesn't start
- Check Node.js version: `node --version` (need 18+)
- Rebuild: `npm run build`
- Check for TypeScript errors

### "Module not found"
- Install dependencies: `npm install`
- Check dist/ exists: `ls -la dist/`

### MCP client can't connect
- Verify server path is correct
- Check environment variables
- Enable debug mode: `"CHAINED_MCP_DEBUG": "true"`

### Permission denied (global install)
- Use sudo: `sudo npm install -g @chained/repository-mcp`
- Or use nvm: https://github.com/nvm-sh/nvm

## 🔗 Links

- **Original Implementation**: PR #2144 by @investigate-champion
- **Global Availability**: This issue by @APIs-architect
- **MCP Protocol**: https://modelcontextprotocol.io/
- **NPM Package**: https://www.npmjs.com/package/@chained/repository-mcp

## 📞 Support

- **Issues**: GitHub Issues
- **Questions**: GitHub Discussions
- **Documentation**: `mcp-servers/chained-repository/`

---

**Quick reference by @APIs-architect** | v1.0.0
