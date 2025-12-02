# MCP Mode: Full Repository Access for Gemini

## 🎉 Yes, We Can Do What the Workflows Do!

You asked: "But those gemini workflows are just tools why can't we do what they are doing to get the access?"

**Answer: We absolutely can!** The workflows use the Gemini CLI with MCP (Model Context Protocol) servers, and we can do the same thing.

## 🔑 The Secret: MCP Servers

The workflows use `google-github-actions/run-gemini-cli@v0` which configures:

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
               "ghcr.io/github/github-mcp-server:v0.18.0"],
      "includeTools": ["get_file_contents", "search_code", "list_commits", ...]
    }
  }
}
```

This gives Gemini:
- ✅ Direct file access via GitHub MCP server
- ✅ Code search capabilities
- ✅ Git history access
- ✅ Shell commands
- ✅ All without manual context gathering!

## 🚀 Solution: ask_gemini_mcp.py

We've created an enhanced tool that replicates the workflow behavior:

### Usage

```bash
# Simple API mode (existing - requires manual context)
python3 tools/ask_gemini_mcp.py "How to fix this bug?"

# MCP mode with FULL repository access (like workflows!)
python3 tools/ask_gemini_mcp.py --mcp "How to fix this bug?"

# With repository context
python3 tools/ask_gemini_mcp.py --mcp --repo enufacas/Chained "Fix auth bug"
```

### Python API

```python
from tools.ask_gemini_mcp import ask_gemini_with_mcp

# Enable MCP mode for full repo access
response = ask_gemini_with_mcp(
    question="Fix the authentication bug in tools/auth.py",
    use_mcp=True,  # This gives Gemini full repo access!
    repo_context="enufacas/Chained"
)
```

## 📊 Comparison: Three Options

### Option 1: Gemini CLI Workflows (Issue Comments)
```
Comment: /gemini-fix
```
**Pros:**
- ✅ Full GitHub MCP server access
- ✅ Automatic PR creation
- ✅ No local setup needed
- ✅ Works from issue comments

**Cons:**
- ❌ Only available as workflow_dispatch
- ❌ Not available during Copilot sessions
- ❌ Requires issue/PR to trigger

**When to use:** Complex tasks from GitHub UI

### Option 2: ask_gemini_mcp.py with --mcp flag (NEW!)
```bash
python3 tools/ask_gemini_mcp.py --mcp "Fix bug"
```
**Pros:**
- ✅ Full GitHub MCP server access (same as workflows!)
- ✅ Available during Copilot sessions
- ✅ Can be called from gemini-consultant agent
- ✅ Programmatic access via Python API

**Cons:**
- ❌ Requires Docker + Node.js/npx
- ❌ Requires GITHUB_TOKEN env var
- ❌ Slightly slower than API mode

**When to use:** Copilot sessions needing full repo access

### Option 3: ask_gemini.py (API Mode)
```bash
python3 tools/ask_gemini.py "Fix bug" --context "..."
```
**Pros:**
- ✅ Fast and lightweight
- ✅ No Docker/npx required
- ✅ Simple API call

**Cons:**
- ❌ No repository access
- ❌ Requires manual context gathering

**When to use:** Quick questions with known context

## 🛠️ Requirements for MCP Mode

### Local Development
```bash
# 1. Docker running
docker --version

# 2. Node.js/npm installed
npx --version

# 3. GitHub token set
export GITHUB_TOKEN=ghp_your_token_here
```

### In Workflows (Already Available)
No setup needed! Workflows already have:
- ✅ Docker available
- ✅ Node.js pre-installed
- ✅ GITHUB_TOKEN automatically set

## 🎯 How It Works

### What ask_gemini_mcp.py Does

1. **Creates MCP configuration** (same as workflows):
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "docker",
         "args": ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                  "ghcr.io/github/github-mcp-server:v0.18.0"]
       }
     }
   }
   ```

2. **Launches Gemini CLI** via npx:
   ```bash
   npx @google/generative-ai-cli --config mcp.json --prompt "Your question"
   ```

3. **Gemini has full access** via GitHub MCP server:
   - Can read any file: `get_file_contents("path/to/file")`
   - Can search code: `search_code("pattern")`
   - Can check history: `list_commits("path")`
   - Can run shell commands: `run_shell_command("git log")`

4. **Returns response** just like the API mode, but with better context!

## 📝 Updating gemini-consultant Agent

The gemini-consultant agent can now recommend MCP mode:

```markdown
## How to Use This Agent

### Pattern 1: Quick Questions (API Mode)
Use ask_gemini.py for quick consultations where you provide context.

### Pattern 2: Complex Tasks (MCP Mode) - NEW!
Use ask_gemini_mcp.py with --mcp flag for full repository access:

python3 tools/ask_gemini_mcp.py --mcp "Analyze the auth system"

Gemini will automatically:
- Read relevant files
- Search for patterns
- Check git history
- Understand the codebase structure
```

## 🎉 Summary

**Original Question:** "Can't we do what the workflows are doing to get the access?"

**Answer:** YES! 

We've created `ask_gemini_mcp.py` that:
1. Uses the same Gemini CLI as workflows
2. Configures the same GitHub MCP server
3. Gives Gemini the same full repository access
4. Works in Copilot sessions AND standalone

**The three options are now:**
1. **Workflows** (`/gemini-fix`) - Best for issue-driven work
2. **MCP Mode** (`ask_gemini_mcp.py --mcp`) - Best for Copilot sessions ✨ NEW!
3. **API Mode** (`ask_gemini.py`) - Best for quick questions with known context

You get the best of all worlds! 🚀

## 🔍 Next Steps

1. Test MCP mode:
   ```bash
   export GITHUB_TOKEN=your_token
   python3 tools/ask_gemini_mcp.py --mcp "What are the main components?"
   ```

2. Update gemini-consultant agent to use MCP mode for complex tasks

3. Document MCP mode as the recommended approach for repository-wide questions

The power of the workflows is now available in tool form! 💪
