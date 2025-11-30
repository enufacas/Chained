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

The GitHub MCP Server provides comprehensive access to GitHub's API through a rich set of tools organized by functionality.

#### Complete Tool Reference

##### Repository & Files
| Tool | Description |
|------|-------------|
| `github-mcp-server-get_file_contents` | Get the contents of a file or directory from a GitHub repository |
| `github-mcp-server-list_branches` | List branches in a GitHub repository |
| `github-mcp-server-list_tags` | List git tags in a GitHub repository |
| `github-mcp-server-get_tag` | Get details about a specific git tag |
| `github-mcp-server-list_commits` | Get list of commits of a branch (supports pagination) |
| `github-mcp-server-get_commit` | Get details for a commit including file diffs and stats |

##### Search Tools
| Tool | Description |
|------|-------------|
| `github-mcp-server-search_code` | Fast and precise code search using GitHub's native search engine |
| `github-mcp-server-search_issues` | Search for issues using GitHub issues search syntax |
| `github-mcp-server-search_pull_requests` | Search for pull requests using search syntax |
| `github-mcp-server-search_repositories` | Find repositories by name, description, topics, or metadata |
| `github-mcp-server-search_users` | Find GitHub users by username, name, or profile info |
| `github-mcp-server-web_search` | AI-powered web search with intelligent answers and citations |

##### Issues
| Tool | Description |
|------|-------------|
| `github-mcp-server-list_issues` | List issues in a repository with filtering and pagination |
| `github-mcp-server-issue_read` | Read issue details (methods: get, get_comments, get_sub_issues, get_labels) |
| `github-mcp-server-list_issue_types` | List supported issue types for repository owner (organization) |
| `github-mcp-server-get_label` | Get a specific label from a repository |

##### Pull Requests
| Tool | Description |
|------|-------------|
| `github-mcp-server-list_pull_requests` | List pull requests with filtering and sorting |
| `github-mcp-server-pull_request_read` | Read PR details (methods: get, get_diff, get_status, get_files, get_review_comments, get_reviews, get_comments) |

##### Releases
| Tool | Description |
|------|-------------|
| `github-mcp-server-list_releases` | List releases in a GitHub repository |
| `github-mcp-server-get_latest_release` | Get the latest release in a repository |
| `github-mcp-server-get_release_by_tag` | Get a specific release by its tag name |

##### Workflows & GitHub Actions
| Tool | Description |
|------|-------------|
| `github-mcp-server-list_workflows` | List workflows in a repository |
| `github-mcp-server-list_workflow_runs` | List workflow runs for a specific workflow |
| `github-mcp-server-get_workflow_run` | Get details of a specific workflow run |
| `github-mcp-server-list_workflow_jobs` | List jobs for a specific workflow run |
| `github-mcp-server-get_job_logs` | Download logs for a workflow job (supports failed_only mode) |
| `github-mcp-server-get_workflow_run_logs` | Download all logs for a workflow run as ZIP |
| `github-mcp-server-get_workflow_run_usage` | Get usage metrics for a workflow run |
| `github-mcp-server-list_workflow_run_artifacts` | List artifacts for a workflow run |
| `github-mcp-server-download_workflow_run_artifact` | Get download URL for a workflow run artifact |
| `github-mcp-server-summarize_job_log_failures` | AI-powered analysis of failed job logs |
| `github-mcp-server-summarize_run_log_failures` | AI-powered analysis of workflow run failures |

##### Security Scanning
| Tool | Description |
|------|-------------|
| `github-mcp-server-list_code_scanning_alerts` | List code scanning alerts in a repository |
| `github-mcp-server-get_code_scanning_alert` | Get details of a specific code scanning alert |
| `github-mcp-server-list_secret_scanning_alerts` | List secret scanning alerts in a repository |
| `github-mcp-server-get_secret_scanning_alert` | Get details of a specific secret scanning alert |

#### Tool Categories by Use Case

**For Code Analysis & Navigation:**
- `search_code`, `get_file_contents`, `list_commits`, `get_commit`, `list_branches`

**For Issue Management:**
- `list_issues`, `issue_read`, `search_issues`, `get_label`

**For PR Review & Analysis:**
- `list_pull_requests`, `pull_request_read`, `search_pull_requests`

**For CI/CD & Workflow Debugging:**
- `list_workflows`, `list_workflow_runs`, `get_workflow_run`, `list_workflow_jobs`
- `get_job_logs`, `summarize_job_log_failures`, `summarize_run_log_failures`

**For Security:**
- `list_code_scanning_alerts`, `get_code_scanning_alert`
- `list_secret_scanning_alerts`, `get_secret_scanning_alert`

**For Research & Discovery:**
- `web_search`, `search_repositories`, `search_users`

**For Release Management:**
- `list_releases`, `get_latest_release`, `get_release_by_tag`

#### Use Cases

- **Repository management and navigation** - Browse files, branches, tags, commits
- **Code search and analysis** - Find code patterns, functions, usage examples
- **Issue tracking and management** - List, search, read issues and comments
- **Pull request review** - Analyze diffs, reviews, comments, status
- **CI/CD debugging** - Analyze workflow failures with AI-powered summaries
- **Security scanning** - Detect code vulnerabilities and leaked secrets
- **Release management** - Track releases and versions
- **Real-time web research** - Search the web with AI-powered intelligent answers

**Agents Using GitHub MCP Server:**
All custom agents have access to GitHub MCP server tools based on their specialization needs.

### 2. Playwright MCP Server (Official - Microsoft/Community)

**Vendor:** Microsoft Playwright Project  
**Status:** ⭐⭐⭐⭐⭐ Trusted & Official

The Playwright MCP Server provides comprehensive browser automation capabilities for testing and web interaction.

#### Complete Tool Reference

##### Browser Management
| Tool | Description |
|------|-------------|
| `playwright-browser_close` | Close the page |
| `playwright-browser_resize` | Resize the browser window |
| `playwright-browser_tabs` | List, create, close, or select browser tabs |
| `playwright-browser_install` | Install the browser specified in the config |

##### Navigation
| Tool | Description |
|------|-------------|
| `playwright-browser_navigate` | Navigate to a URL |
| `playwright-browser_navigate_back` | Go back to the previous page |
| `playwright-browser_wait_for` | Wait for text to appear/disappear or specified time |

##### Page Interaction
| Tool | Description |
|------|-------------|
| `playwright-browser_click` | Perform click on a web page |
| `playwright-browser_hover` | Hover over element on page |
| `playwright-browser_drag` | Perform drag and drop between two elements |
| `playwright-browser_type` | Type text into editable element |
| `playwright-browser_press_key` | Press a key on the keyboard |
| `playwright-browser_select_option` | Select an option in a dropdown |
| `playwright-browser_fill_form` | Fill multiple form fields |
| `playwright-browser_file_upload` | Upload one or multiple files |

##### Capturing & Analysis
| Tool | Description |
|------|-------------|
| `playwright-browser_snapshot` | Capture accessibility snapshot of the current page |
| `playwright-browser_take_screenshot` | Take a screenshot of the current page |
| `playwright-browser_console_messages` | Returns all console messages |
| `playwright-browser_network_requests` | Returns all network requests since loading the page |

##### Advanced
| Tool | Description |
|------|-------------|
| `playwright-browser_evaluate` | Evaluate JavaScript expression on page or element |
| `playwright-browser_handle_dialog` | Handle a dialog (accept/dismiss) |

#### Use Cases

- **Browser automation and web testing** - Navigate, click, fill forms
- **End-to-end (E2E) testing** - Complete user flow testing
- **UI/UX validation and testing** - Visual testing, accessibility snapshots
- **Web scraping and data extraction** - Read content, analyze pages
- **Integration testing with web services** - Test web APIs and interfaces
- **Debugging web apps** - Console messages, network requests

**Agents Using Playwright:**
- **test-champion** - Full browser automation for E2E testing
- **ux-enhancer** - Enhanced UI/UX interaction and validation
- **integration-specialist** - Web service integration testing
- **coordinate-wizard** - API and web service coordination

### 3. Google Cloud (gcloud) MCP Server

**Vendor:** Google Cloud  
**Status:** ⭐⭐⭐⭐⭐ Trusted & Official

The gcloud MCP Server provides access to Google Cloud Platform services through the gcloud CLI.

#### Complete Tool Reference

| Tool | Description |
|------|-------------|
| `gcloud-run_gcloud_command` | Execute a gcloud command for Google Cloud operations |

**Capabilities:**
- Compute Engine management (VMs, networking)
- Cloud Storage operations
- Kubernetes Engine (GKE) management
- Cloud Functions deployment
- BigQuery operations
- Cloud Run services
- IAM and security management
- Any gcloud CLI command

**Restrictions:**
- No command substitution (no subshells or `$(...)`)
- No pipes (`|`) or shell operators
- No redirection operators (`>`, `>>`, `<`)
- All required parameters must be included

#### Use Cases

- **Infrastructure management** - Create and manage cloud resources
- **Deployment** - Deploy applications to GCP services
- **DevOps automation** - Automate cloud infrastructure tasks
- **Cost management** - Monitor and optimize cloud spending
- **Security** - Manage IAM and security policies

**Agents Using gcloud:**
- **cloud-architect** - Cloud infrastructure design and management
- **infrastructure-specialist** - DevOps and infrastructure automation

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

### GitHub MCP Server (Built-in)

The GitHub MCP server is **automatically available** to GitHub Copilot Coding Agent - no configuration required. All 37+ tools listed above are enabled by default when Copilot runs.

### Custom MCP Servers

Custom MCP servers (gcloud, chained-repository, etc.) are configured in:

1. **Repository Settings UI**: `Settings > Code & automation > Copilot > Coding agent`
2. **Configuration File**: `.github/copilot/mcp.json`

Example `.github/copilot/mcp.json`:
```json
{
  "mcpServers": {
    "gcloud": {
      "command": "npx",
      "args": ["-y", "@google-cloud/gcloud-mcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_APPLICATION_CREDENTIALS}"
      }
    }
  }
}
```

### Environment Setup

The `.github/workflows/copilot-setup-steps.yml` workflow prepares the environment:
- Installs Node.js, Python, and dependencies
- Configures GCP authentication (if secrets are available)
- Pre-installs custom MCP server packages
- Sets up environment variables for Copilot

### Agent Tool Access

Agent definitions in `.github/agents/*.md` can specify which MCP tools they use in their YAML frontmatter:

```yaml
tools:
  - github-mcp-server-search_code
  - github-mcp-server-web_search
  - playwright-browser_navigate
```

**Note:** This is for documentation and agent guidance - all GitHub MCP server tools are available to agents regardless of what's listed.

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

- All MCP servers used are from official, trusted vendors (Microsoft/GitHub/Google)
- Security scanning tools are integrated into relevant agents
- Tools require appropriate GitHub authentication (handled by GitHub Actions)
- No external API keys or credentials are stored in the repository
- gcloud commands are restricted to prevent shell injection

## Tool Discovery

MCP server tools are automatically discovered and available to agents at runtime. The complete list of available tools can be found in:
- This documentation (authoritative reference)
- The GitHub Copilot Coding Agent system prompt
- The MCP server implementations themselves

When new tools are added to MCP servers, update this documentation to reflect the changes.

---

*Last Updated: November 30, 2025*  
*Part of the Chained autonomous AI ecosystem* 🚀
