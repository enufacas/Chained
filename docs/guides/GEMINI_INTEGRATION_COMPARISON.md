# Ask Gemini Integration with Existing Gemini Workflows

This document explains how the new "ask gemini" escalation standard integrates with the existing Gemini CLI workflows in the Chained repository.

## Overview

The Chained repository now has **two complementary Gemini integration mechanisms**:

### 1. Existing: Gemini CLI Workflows (GitHub Actions)
- **Location:** `.github/workflows/gemini-*.yml`
- **Trigger:** `@gemini-cli` comments on issues/PRs
- **Use Case:** Automated PR reviews, issue triage, and fixes via workflows
- **Model:** gemini-3-pro-preview (configurable via `GEMINI_MODEL` variable)
- **Context:** Full GitHub Actions environment with MCP servers

### 2. New: Ask Gemini Tool (Copilot Sessions)
- **Location:** `tools/ask_gemini.py` + `@gemini-consultant` agent
- **Trigger:** "ask gemini about X" in Copilot sessions
- **Use Case:** Human-controlled escalation during development
- **Model:** gemini-3-pro-preview (default, configurable in code)
- **Context:** Developer's local environment or Copilot runner

## Comparison

| Feature | Gemini CLI Workflows | Ask Gemini Tool |
|---------|---------------------|-----------------|
| **Invocation** | `@gemini-cli /command` in issue/PR | "ask gemini about X" in Copilot |
| **Environment** | GitHub Actions runner | Local dev or Copilot runner |
| **Authentication** | Secrets (GEMINI_API_KEY) | Env vars (GEMINI_API_KEY) |
| **Response** | Posted as issue/PR comment | Returned to Copilot session |
| **Use Case** | Automated workflows | Interactive development |
| **MCP Servers** | GitHub MCP (full access) | None (standalone tool) |
| **Tools Available** | Shell commands, GitHub API | Python only |

## When to Use Which?

### Use Gemini CLI Workflows When:
- ✅ You want automated PR code reviews
- ✅ You need issue triage and labeling
- ✅ You want automatic issue fixes with PR creation
- ✅ You need GitHub API operations (create PR, add comments)
- ✅ You want results posted publicly in issues/PRs

### Use Ask Gemini Tool When:
- ✅ You're actively coding in a Copilot session
- ✅ You need quick expert consultation without workflow overhead
- ✅ You want private/local consultation before sharing
- ✅ You need architectural guidance during development
- ✅ You want second opinions on design decisions

## Architecture

### Gemini CLI Workflows Architecture
```
Issue/PR Comment (@gemini-cli /review)
  ↓
GitHub Actions Trigger
  ↓
gemini-dispatch.yml (router)
  ↓
gemini-review.yml / gemini-triage.yml / gemini-invoke.yml
  ↓
google-github-actions/run-gemini-cli@v0
  ↓
Gemini CLI with MCP servers
  ↓
Gemini 3 Pro Preview API
  ↓
Response posted to issue/PR
```

### Ask Gemini Tool Architecture
```
Copilot Session ("ask gemini about X")
  ↓
@gemini-consultant Agent
  ↓
tools/ask_gemini.py
  ↓
google-generativeai Python SDK (or Vertex AI SDK)
  ↓
Gemini 3 Pro Preview API
  ↓
Response returned to Copilot
  ↓
Agent synthesizes + provides recommendations
```

## Authentication Configuration

Both mechanisms support the same authentication methods:

### Option A: Google AI Studio (Simplest)
```bash
export GEMINI_API_KEY="your-api-key"
```
- Works for both workflows and ask_gemini tool
- Get key from: https://aistudio.google.com/app/apikey

### Option B: Vertex AI (For GCP Users)
```bash
export GOOGLE_API_KEY="your-vertex-api-key"
export USE_VERTEX_AI=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
```
- Works for both workflows and ask_gemini tool
- Requires GCP project with Vertex AI enabled

## Model Configuration

Both use `gemini-3-pro-preview` by default:

### Gemini CLI Workflows
Set via repository variable:
```bash
# In Settings > Secrets and variables > Actions > Variables
GEMINI_MODEL = "gemini-3-pro-preview"  # default if not set
```

### Ask Gemini Tool
Set via code parameter or environment:
```python
# In code
response = ask_gemini(question, model="gemini-3-pro-preview")

# Or set default in environment
export GEMINI_MODEL="gemini-3-pro-preview"
```

## Shared Infrastructure

Both mechanisms leverage existing Gemini infrastructure:

### Shared Components
1. **Authentication setup**: Both use GEMINI_API_KEY or Vertex AI
2. **Model access**: Both call gemini-3-pro-preview
3. **Documentation**: docs/GEMINI_CLI_INTEGRATION.md covers both
4. **Rate limits**: Share the same Gemini API quota

### Separate Components
1. **Invocation method**: Workflows vs Python tool
2. **Response delivery**: Issue comments vs Copilot session
3. **Context gathering**: MCP servers vs local environment
4. **Access control**: GitHub permissions vs local access

## Example Workflows

### Scenario 1: Automated PR Review + Interactive Consultation

**Step 1: Automated Review (Gemini CLI Workflow)**
```
# In PR comment
@gemini-cli /review

# Gemini CLI reviews the PR and posts inline comments
```

**Step 2: Address Feedback (Ask Gemini Tool)**
```
# In Copilot session while fixing issues
"ask gemini about the security implications of the caching approach 
Gemini suggested in the review"

# Get deeper analysis without triggering another workflow
```

### Scenario 2: Local Development + Public Validation

**Step 1: Local Consultation (Ask Gemini Tool)**
```
# During development
"ask gemini about whether to use WebSockets or SSE for real-time updates"

# Make architectural decision based on consultation
```

**Step 2: Get Review (Gemini CLI Workflow)**
```
# After implementation, open PR
@gemini-cli /review

# Validate implementation matches architectural decision
```

### Scenario 3: Issue Triage + Deep Dive

**Step 1: Automatic Triage (Gemini CLI Workflow)**
```
# Issue is automatically triaged with labels
# (if auto-trigger enabled)
```

**Step 2: Investigation (Ask Gemini Tool)**
```
# While working on the issue in Copilot
"ask gemini about alternative approaches to solve this issue"

# Explore solutions before implementing
```

## Best Practices

### Use Gemini CLI Workflows For:
1. **Public Reviews**: When you want feedback visible in PRs
2. **Automated Processes**: Scheduled triage, auto-reviews
3. **Team Collaboration**: Shared access to Gemini insights
4. **GitHub Operations**: Creating PRs, adding labels

### Use Ask Gemini Tool For:
1. **Private Exploration**: Testing ideas before sharing
2. **Quick Questions**: Fast consultation without workflow overhead
3. **Development Flow**: Staying in Copilot without context switch
4. **Personal Learning**: Understanding concepts while coding

### Combine Both When:
1. **Development Lifecycle**: Local consultation → PR review
2. **Decision Validation**: Private analysis → public documentation
3. **Iterative Improvement**: Multiple consultations → final review
4. **Learning Path**: Personal exploration → team discussion

## Rate Limiting Considerations

Both mechanisms share the same Gemini API quota:

**Free Tier Limits:**
- gemini-3-pro-preview: 15 RPM, 1,500 RPD
- gemini-1.5-flash-latest: 15 RPM, 1,500 RPD

**Best Practices:**
1. Use ask_gemini tool for rapid iterations (lower overhead)
2. Use Gemini CLI workflows for thorough reviews (worth the cost)
3. Monitor daily usage across both mechanisms
4. Upgrade to paid tier if hitting limits regularly

## Configuration Files

### Gemini CLI Workflows
```
.github/workflows/
├── gemini-dispatch.yml      # Router
├── gemini-review.yml        # PR reviews
├── gemini-triage.yml        # Issue triage
├── gemini-invoke.yml        # General assistant
└── gemini-fix.yml           # Auto-fixes

docs/GEMINI_CLI_INTEGRATION.md  # Full documentation
docs/guides/GEMINI.md            # Project context
```

### Ask Gemini Tool
```
tools/ask_gemini.py              # Python tool
.github/agents/gemini-consultant.md  # Agent definition
docs/guides/ASK_GEMINI.md        # Full documentation
tests/test_ask_gemini.py         # Tests
examples/ask_gemini_examples.py  # Examples
```

## Migration Path

If you're currently using Gemini CLI workflows:

1. **Keep using workflows** for automated PR reviews and issue triage
2. **Add ask_gemini tool** for interactive development consultations
3. **No conflicts** - both can coexist and complement each other
4. **Same authentication** - reuse existing GEMINI_API_KEY

## Troubleshooting

### Issue: Both mechanisms failing with auth errors
**Cause:** Missing or incorrect API key configuration

**Solution:**
```bash
# Check current configuration
echo "GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."
echo "GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:10}..."
echo "USE_VERTEX_AI: $USE_VERTEX_AI"

# For workflows: Set in GitHub Secrets
# For ask_gemini: Set in local environment
```

### Issue: Rate limit exceeded on both
**Cause:** Sharing the same API quota

**Solution:**
- Monitor usage: 15 requests/minute, 1500 requests/day
- Stagger usage: Use ask_gemini during dev, workflows for reviews
- Upgrade to paid tier if needed
- Use gemini-1.5-flash-latest for higher limits

### Issue: Different results from workflows vs tool
**Cause:** Different context provided

**Explanation:**
- Workflows have full GitHub context via MCP servers
- Ask_gemini tool has only what you provide in the prompt
- Both use the same model and should give consistent advice

**Solution:**
- Provide equivalent context to both
- Use workflows for GitHub-integrated tasks
- Use ask_gemini for general consultation

## Future Enhancements

### Potential Improvements:
1. **Unified MCP Integration**: Give ask_gemini tool access to GitHub MCP
2. **Shared Context**: Cache common consultations across both mechanisms
3. **Usage Analytics**: Track which mechanism is used more effectively
4. **Cost Optimization**: Smart routing based on query complexity

### Feedback Welcome:
If you have suggestions for improving either mechanism, please:
1. Open an issue with the `enhancement` label
2. Mention @gemini-consultant for tool improvements
3. Mention @troubleshoot-expert for workflow improvements

## Summary

The Chained repository now offers **two powerful ways to leverage Gemini 3 Pro Preview**:

| Mechanism | Best For | Invocation |
|-----------|----------|------------|
| **Gemini CLI Workflows** | Automated, public, GitHub-integrated tasks | `@gemini-cli /command` |
| **Ask Gemini Tool** | Interactive, private, development-time consultation | "ask gemini about X" |

Both mechanisms:
- ✅ Use gemini-3-pro-preview
- ✅ Support same authentication methods
- ✅ Share API quota
- ✅ Complement each other well

Choose based on your current task, and feel free to use both together for maximum benefit!

---

**Related Documentation:**
- [Ask Gemini Guide](./ASK_GEMINI.md) - Detailed guide for the tool
- [Gemini CLI Integration](../GEMINI_CLI_INTEGRATION.md) - Workflow setup
- [Agent Definition](../../.github/agents/gemini-consultant.md) - Agent details
