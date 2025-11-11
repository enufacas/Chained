# MCP Servers Configuration

## Overview

This document describes the Model Context Protocol (MCP) servers configured across the Chained repository's GitHub Copilot custom agents. These MCP servers provide agents with enhanced capabilities to interact with external systems, search the web, automate browser interactions, and more.

## What are MCP Servers?

MCP (Model Context Protocol) is an open standard that allows AI assistants to securely connect to external tools, APIs, and data sources. MCP servers enable GitHub Copilot agents to:

- Access real-time information from the web
- Interact with GitHub repositories programmatically
- Automate browser testing and interaction
- Organize and manage knowledge efficiently

## Configured MCP Servers

### 1. GitHub MCP Server (Official - GitHub/Microsoft)

**Vendor:** GitHub/Microsoft  
**Status:** ⭐⭐⭐⭐⭐ Trusted & Official

**Available Tools:**
- `github-mcp-server-get_file_contents` - Read repository files
- `github-mcp-server-search_code` - Search code across repositories
- `github-mcp-server-search_issues` - Search GitHub issues
- `github-mcp-server-list_issues` - List repository issues
- `github-mcp-server-list_secret_scanning_alerts` - Security vulnerability scanning
- `github-mcp-server-list_code_scanning_alerts` - Code security analysis
- `github-mcp-server-web_search` - AI-powered web search with citations

**Use Cases:**
- Repository management and navigation
- Code search and analysis
- Issue tracking and management
- Security scanning and vulnerability detection
- Real-time web research with verified sources

**Agents Using GitHub MCP Server:**
All 14 custom agents have access to GitHub MCP server tools based on their specialization needs.

### 2. Playwright MCP Server (Official - Microsoft/Community)

**Vendor:** Microsoft Playwright Project  
**Status:** ⭐⭐⭐⭐⭐ Trusted & Official

**Available Tools:**
- `playwright-browser_navigate` - Navigate to URLs
- `playwright-browser_snapshot` - Capture page accessibility snapshots
- `playwright-browser_take_screenshot` - Take page screenshots
- `playwright-browser_click` - Click elements
- `playwright-browser_fill_form` - Fill form fields
- `playwright-browser_hover` - Hover over elements
- `playwright-browser_evaluate` - Execute JavaScript in browser context

**Use Cases:**
- Browser automation and web testing
- End-to-end (E2E) testing
- UI/UX validation and testing
- Web scraping and data extraction
- Integration testing with web services

**Agents Using Playwright:**
- **test-champion** - Full browser automation for E2E testing
- **ux-enhancer** - Enhanced UI/UX interaction and validation
- **integration-specialist** - Web service integration testing
- **coordinate-wizard** - API and web service coordination

## Agent-Specific MCP Server Configurations

### Testing & Quality Assurance
- **test-champion**: GitHub tools + Full Playwright suite for comprehensive E2E testing
- **validate-wizard**: GitHub tools + web_search for validation research
- **validate-pro**: GitHub tools + security scanning + web_search

### Development & Architecture
- **feature-architect**: GitHub tools + web_search for research on new features
- **bug-hunter**: GitHub tools + web_search for bug investigation
- **code-poet**: GitHub tools + web_search for coding best practices

### Security & Performance
- **security-guardian**: GitHub tools + security scanning + web_search
- **performance-optimizer**: GitHub tools + web_search for optimization techniques

### Documentation & Knowledge
- **doc-master**: GitHub tools + web_search for documentation research
- **teach-wizard**: GitHub tools + web_search for tutorial creation

### Integration & Coordination
- **integration-specialist**: GitHub tools + web_search + Playwright for testing integrations
- **coordinate-wizard**: GitHub tools + web_search + Playwright for service coordination

### Code Quality
- **refactor-wizard**: GitHub tools + web_search for refactoring patterns
- **ux-enhancer**: GitHub tools + web_search + Enhanced Playwright for UI/UX work

## Why These MCP Servers?

### Selection Criteria

1. **Widely Adopted**: Both GitHub and Playwright MCP servers are among the most popular MCP servers in 2025
2. **Trusted Vendors**: Official servers from Microsoft/GitHub
3. **Organize Information**: 
   - GitHub MCP helps organize code, issues, and repository information
   - Web search provides organized, cited information from the internet
4. **Understand AI Concepts**: Web search enables agents to research latest AI developments, best practices, and emerging patterns
5. **Security**: Official servers from trusted vendors with established security practices

### Benefits

- **Real-time Information**: Agents can access current information through web search
- **Enhanced Testing**: Playwright enables comprehensive browser-based testing
- **Better Integration**: Tools for testing and coordinating web services
- **Security Focus**: Built-in security scanning and vulnerability detection
- **Knowledge Management**: Efficient code search and information organization

## Configuration Location

MCP server tools are configured in the YAML frontmatter of each agent definition:

```
/home/runner/work/Chained/Chained/.github/agents/*.md
```

Each agent's tools list specifies which MCP server capabilities it has access to.

## Additional Resources

- [GitHub MCP Server Documentation](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server)
- [Playwright MCP Server](https://github.com/microsoft/playwright)
- [MCP Market Leaderboard](https://mcpmarket.com/leaderboards) - Top 100 MCP servers
- [Awesome MCP Servers](https://mcp-awesome.com/) - 1200+ verified MCP servers
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP specification

## Future Enhancements

Potential MCP servers to consider in the future:
- **PostgreSQL MCP** - For database management and natural language SQL
- **MongoDB Atlas MCP** - For NoSQL database operations
- **Notion MCP** - For enhanced knowledge base management
- **Slack MCP** - For team communication integration

These would be added based on specific needs and use cases that emerge from the agent ecosystem.

## Security Considerations

- All MCP servers used are from official, trusted vendors (Microsoft/GitHub)
- Security scanning tools are integrated into relevant agents
- Tools require appropriate GitHub authentication (handled by GitHub Actions)
- No external API keys or credentials are stored in the repository

---

*Last Updated: November 11, 2025*  
*Part of the Chained autonomous AI ecosystem* 🚀
