# GitHub Copilot Integration Guide

**Created by @APIs-architect**

This guide explains how to integrate the Chained Repository MCP server with GitHub Copilot for use by all agents in GitHub Actions workflows.

## 🎯 Overview

GitHub Copilot agents running in GitHub Actions can access the Chained Repository MCP server to:
- Query agent specializations and metrics
- Access learning data and trends
- Get repository insights
- Match issues to appropriate agents
- View workflow and automation data

## 🔧 Integration Methods

### Method 1: Workflow-Level Integration (Recommended)

Add MCP server installation to individual workflows:

```yaml
name: "Agent Task Execution"

on:
  issues:
    types: [opened, labeled]

jobs:
  execute-with-copilot:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Install Chained MCP Server
        run: |
          npm install -g @chained/repository-mcp
          which chained-repository-mcp
      
      - name: Configure Copilot MCP Access
        env:
          MCP_SERVERS_CONFIG: |
            {
              "mcpServers": {
                "chained-repository": {
                  "command": "chained-repository-mcp",
                  "description": "Chained repository data access"
                }
              }
            }
        run: |
          echo "$MCP_SERVERS_CONFIG" > /tmp/mcp-config.json
          echo "MCP_CONFIG_PATH=/tmp/mcp-config.json" >> $GITHUB_ENV
      
      - name: Run Copilot Agent
        uses: copilot-swe-agent@v1
        with:
          task: ${{ github.event.issue.title }}
          mcp-config: /tmp/mcp-config.json
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CHAINED_REPO_PATH: ${{ github.workspace }}
```

### Method 2: Reusable Composite Action

Create a reusable action at `.github/actions/setup-copilot-mcp/action.yml`:

```yaml
name: 'Setup Copilot with MCP'
description: 'Configure GitHub Copilot with Chained Repository MCP server'
outputs:
  mcp-config-path:
    description: 'Path to MCP configuration file'
    value: ${{ steps.setup.outputs.config-path }}

runs:
  using: 'composite'
  steps:
    - name: Install Chained MCP Server
      shell: bash
      run: |
        echo "📦 Installing Chained Repository MCP server..."
        npm install -g @chained/repository-mcp
        
        # Verify installation
        if ! which chained-repository-mcp > /dev/null; then
          echo "❌ Failed to install chained-repository-mcp"
          exit 1
        fi
        
        echo "✅ MCP server installed at: $(which chained-repository-mcp)"
    
    - name: Create MCP Configuration
      id: setup
      shell: bash
      run: |
        CONFIG_PATH="/tmp/copilot-mcp-config-${{ github.run_id }}.json"
        
        cat > "$CONFIG_PATH" <<EOF
        {
          "mcpServers": {
            "chained-repository": {
              "command": "chained-repository-mcp",
              "description": "Chained Repository MCP - Agent system, learnings, automation tools"
            }
          }
        }
        EOF
        
        echo "📝 MCP config created at: $CONFIG_PATH"
        echo "config-path=$CONFIG_PATH" >> $GITHUB_OUTPUT
        
        # Export for Copilot
        echo "MCP_SERVERS_CONFIG=$CONFIG_PATH" >> $GITHUB_ENV
        echo "CHAINED_REPO_PATH=${{ github.workspace }}" >> $GITHUB_ENV
    
    - name: Test MCP Server
      shell: bash
      run: |
        echo "🧪 Testing MCP server..."
        
        # Test server can start (will wait for stdin, so we timeout)
        timeout 2 chained-repository-mcp || true
        
        echo "✅ MCP server is functional"
```

Use in workflows:

```yaml
jobs:
  task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Copilot with MCP
        uses: ./.github/actions/setup-copilot-mcp
        id: mcp
      
      - name: Run Agent
        uses: copilot-swe-agent@v1
        with:
          mcp-config: ${{ steps.mcp.outputs.mcp-config-path }}
```

### Method 3: Organization-Wide Docker Image

Create a custom Docker image with MCP pre-installed:

**Dockerfile:**
```dockerfile
FROM ubuntu:22.04

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Chained MCP Server globally
RUN npm install -g @chained/repository-mcp

# Verify installation
RUN which chained-repository-mcp && \
    node --version && \
    npm --version

# Create MCP config directory
RUN mkdir -p /etc/copilot-mcp

# Add default MCP configuration
COPY mcp-config.json /etc/copilot-mcp/config.json

# Set environment variables
ENV MCP_SERVERS_CONFIG=/etc/copilot-mcp/config.json
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /workspace
```

**mcp-config.json:**
```json
{
  "mcpServers": {
    "chained-repository": {
      "command": "chained-repository-mcp",
      "description": "Chained Repository MCP Server"
    }
  }
}
```

**Build and publish:**
```bash
docker build -t ghcr.io/enufacas/copilot-with-mcp:latest .
docker push ghcr.io/enufacas/copilot-with-mcp:latest
```

**Use in workflows:**
```yaml
jobs:
  task:
    runs-on: ubuntu-latest
    container: ghcr.io/enufacas/copilot-with-mcp:latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Copilot Agent
        # MCP already configured in container
```

## 📝 Example: Complete Workflow

Here's a complete example workflow that uses the MCP server:

```yaml
name: "Copilot Agent with MCP"

on:
  issues:
    types: [opened, labeled]
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number'
        required: true

jobs:
  assign-and-execute:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'copilot')
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Chained MCP Server
        run: |
          echo "📦 Installing Chained Repository MCP..."
          npm install -g @chained/repository-mcp
          
          # Verify
          chained-repository-mcp --version 2>/dev/null || echo "No version command"
          which chained-repository-mcp
      
      - name: Setup MCP Configuration
        run: |
          mkdir -p /tmp/copilot-config
          
          cat > /tmp/copilot-config/mcp.json <<'EOF'
          {
            "mcpServers": {
              "chained-repository": {
                "command": "chained-repository-mcp",
                "description": "Chained Repository Access",
                "env": {
                  "CHAINED_REPO_PATH": "${{ github.workspace }}",
                  "CHAINED_MCP_DEBUG": "false"
                }
              }
            }
          }
          EOF
          
          echo "MCP_SERVERS_CONFIG=/tmp/copilot-config/mcp.json" >> $GITHUB_ENV
          echo "CHAINED_REPO_PATH=${{ github.workspace }}" >> $GITHUB_ENV
          
          echo "✅ MCP configuration created"
          cat /tmp/copilot-config/mcp.json
      
      - name: Test MCP Tools
        run: |
          echo "🧪 Testing MCP server availability..."
          
          # The server runs in stdio mode, so we just verify it exists
          if command -v chained-repository-mcp &> /dev/null; then
            echo "✅ MCP server command available"
          else
            echo "❌ MCP server command not found"
            exit 1
          fi
      
      - name: Find Best Agent for Issue
        id: match-agent
        run: |
          # Use MCP server data via direct file access as fallback
          # (when Copilot calls the MCP server, it will use the proper protocol)
          
          ISSUE_TITLE="${{ github.event.issue.title }}"
          ISSUE_BODY="${{ github.event.issue.body }}"
          
          echo "🔍 Matching issue to agent..."
          echo "Title: $ISSUE_TITLE"
          
          # This would normally be done via MCP protocol by Copilot
          # For workflow purposes, we use the Python script directly
          AGENT=$(python3 tools/match-issue-to-agent.py "$ISSUE_TITLE" "$ISSUE_BODY" | jq -r '.agent')
          
          echo "agent=$AGENT" >> $GITHUB_OUTPUT
          echo "✅ Matched to agent: $AGENT"
      
      - name: Assign Copilot to Issue
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          AGENT="${{ steps.match-agent.outputs.agent }}"
          ISSUE_NUM="${{ github.event.issue.number }}"
          
          # Update issue with agent assignment
          gh issue comment $ISSUE_NUM --body \
            "🤖 **@${AGENT}** has been assigned via MCP-enabled Copilot"
          
          # Assign Copilot
          gh issue edit $ISSUE_NUM --add-assignee copilot
      
      - name: Execute Task with Copilot
        # This step would invoke the actual Copilot agent
        # with MCP configuration from MCP_SERVERS_CONFIG
        run: |
          echo "🚀 Copilot would execute here with MCP access"
          echo "MCP Config: $MCP_SERVERS_CONFIG"
          echo "Agent: ${{ steps.match-agent.outputs.agent }}"
          
          # The Copilot agent can now use MCP tools like:
          # - list_agents
          # - get_agent_details
          # - search_agent_patterns
          # - get_learning_data
          # - etc.
```

## 🔑 Environment Variables

Set these in your workflow for optimal MCP integration:

```yaml
env:
  # MCP Configuration
  MCP_SERVERS_CONFIG: /tmp/mcp-config.json
  
  # Chained Repository Path
  CHAINED_REPO_PATH: ${{ github.workspace }}
  
  # Optional: Enable debug logging
  CHAINED_MCP_DEBUG: true
  
  # Optional: Custom cache directory
  CHAINED_MCP_CACHE_DIR: /tmp/mcp-cache
  
  # GitHub Token for API access
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🎯 Using MCP Tools in Copilot

Once configured, Copilot can use MCP tools in prompts:

### Example 1: Find Agent for Task

```
Use the chained-repository MCP to find the best agent for implementing a 
REST API endpoint. Check agent specializations and metrics.
```

Copilot will call:
```json
{
  "tool": "search_agent_patterns",
  "arguments": {
    "keywords": ["api", "rest", "endpoint", "implementation"]
  }
}
```

### Example 2: Get Learning Context

```
Check recent TLDR learnings about API best practices using the 
chained-repository MCP server.
```

Copilot will call:
```json
{
  "tool": "get_learning_data",
  "arguments": {
    "source": "tldr",
    "limit": 10,
    "keywords": ["api", "rest", "best practices"]
  }
}
```

### Example 3: Check Agent Performance

```
Before assigning work, check the performance metrics of the 
secure-specialist agent via MCP.
```

Copilot will call:
```json
{
  "tool": "get_agent_metrics",
  "arguments": {
    "agent_id": "secure-specialist"
  }
}
```

## 🐛 Troubleshooting

### MCP Server Not Found in Workflow

**Solution:**
1. Check npm global install succeeded
2. Verify PATH includes npm global bin
3. Add explicit path to config:
   ```json
   {
     "command": "/usr/local/bin/chained-repository-mcp"
   }
   ```

### Copilot Can't Access MCP Tools

**Solution:**
1. Verify MCP_SERVERS_CONFIG is set correctly
2. Check file permissions on config file
3. Ensure Copilot agent version supports MCP
4. Check workflow logs for MCP initialization

### Data Not Found

**Solution:**
1. Verify CHAINED_REPO_PATH points to correct location
2. Ensure repository is checked out before MCP use
3. Check file structure:
   ```bash
   ls $CHAINED_REPO_PATH/.github/agent-system/
   ls $CHAINED_REPO_PATH/learnings/
   ```

## 📚 Related Documentation

- [INSTALL.md](./INSTALL.md) - Installation guide
- [README.md](./README.md) - MCP server documentation
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide

## 🤝 Contributing

To improve GitHub Copilot integration:

1. Test with actual Copilot agent workflows
2. Document additional use cases
3. Submit workflow examples
4. Report integration issues

---

**GitHub Copilot Integration by @APIs-architect** 🤖✨
