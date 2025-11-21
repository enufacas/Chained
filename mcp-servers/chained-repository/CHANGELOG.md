# Changelog

All notable changes to the Chained Repository MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-21

### Added by @APIs-architect - Global Availability

- **NPM Package Configuration**: Set up `@chained/repository-mcp` for global installation
- **Global Binary**: Added `chained-repository-mcp` command for global CLI access
- **Installation Guide** (`INSTALL.md`): Comprehensive platform-specific instructions
  - macOS installation via npm
  - Linux installation via npm
  - Windows installation via npm
  - Docker installation option
  - Configuration for Claude Desktop, Cline, and other MCP clients
- **GitHub Copilot Integration** (`GITHUB_COPILOT.md`): Complete workflow integration guide
  - Reusable GitHub Action: `.github/actions/setup-mcp-server`
  - Environment variable configuration
  - Example workflow patterns
  - Troubleshooting guide
- **Quick Start Guide** (`QUICKSTART.md`): 5-minute setup for all platforms
  - Fastest path to working MCP server
  - Platform-specific quick commands
  - Verification steps
- **Publishing Guide** (`PUBLISHING.md`): NPM publishing documentation
  - Pre-publishing checklist
  - Step-by-step publishing process
  - Version management
  - Security best practices
  - CI/CD automation options
- **Example Workflow** (`.github/workflows/example-copilot-mcp.yml`): Working demonstration
  - MCP server setup in GitHub Actions
  - Data access examples
  - Agent matching examples
  - Learning search examples
- **NPM Configuration**:
  - `.npmignore`: Excludes development files from package
  - Package scope: `@chained` for organization
  - Files whitelist for clean package distribution
- **README Updates**: Added global availability section with quick start

### Changed

- **README.md**: Added global availability section at top with npm installation
- **Package metadata**: Enhanced description and keywords for npm discoverability

### Original Creation by @investigate-champion (PR #2144)

The foundational MCP server implementation that this release builds upon:

- **Core MCP Server**: TypeScript-based stdio transport server
- **Repository Tools**:
  - `get_agent_details`: Retrieve agent metadata and capabilities
  - `list_agents`: Browse all available agents
  - `search_agents`: Find agents by keywords and patterns
  - `match_issue_to_agent`: Intelligent agent assignment
  - `get_workflow_info`: Access GitHub Actions workflow details
  - `list_workflows`: Browse repository workflows
  - `search_learnings`: Query autonomous system learnings
  - `list_available_tools`: Discover Python tools
  - `get_github_pages_data`: Access documentation site data
- **Data Resources**:
  - Agent registry access
  - Learning repository access
  - Workflow metadata access
  - GitHub Pages data access
- **Pre-built Prompts**:
  - Agent discovery and selection
  - Repository analysis
  - Learning queries
- **MCP Protocol Compliance**:
  - Full tools support
  - Resources enumeration
  - Prompts system
  - Stdio transport
- **Documentation**:
  - Comprehensive README
  - Claude Desktop configuration example
  - Tool usage examples
- **TypeScript Build System**:
  - Clean compilation to dist/
  - Type definitions
  - ES modules support

## [Unreleased]

### Planned Features

- [ ] Published to npm registry
- [ ] CI/CD automated publishing
- [ ] Additional MCP clients support
- [ ] Performance optimizations
- [ ] Extended tool set
- [ ] Caching layer for frequent queries
- [ ] Real-time repository monitoring
- [ ] Agent collaboration tools

## Version History

- **v1.0.0** (2025-11-21): Global availability release by @APIs-architect
  - NPM package configuration
  - Comprehensive documentation suite
  - GitHub Actions integration
  - Multi-platform installation support

- **v0.1.0** (PR #2144): Initial implementation by @investigate-champion
  - Core MCP server functionality
  - Repository data access tools
  - Basic documentation

---

**Maintained by @APIs-architect** (global availability) and **@investigate-champion** (original implementation)

For publishing updates, see: [PUBLISHING.md](./PUBLISHING.md)
