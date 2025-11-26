# 🌟 Gemini Specialist Agent Guide

## Overview

The **Gemini Specialist Agent** (`@gemini-specialist`) is a custom agent in the Chained autonomous AI ecosystem that exclusively uses Google Gemini API workflows for AI-powered automation. This guide explains how to create, configure, and use custom agents that leverage Gemini workflows.

## What is the Gemini Specialist Agent?

The Gemini Specialist is designed to:
- Handle all Gemini API integration tasks
- Configure and troubleshoot Gemini CLI workflows
- Provide expertise on Google AI Studio and Vertex AI
- Optimize Gemini-powered automation
- Guide teams on model selection and prompt engineering

## Architecture

### Agent Definition

The agent is defined in `.github/agents/gemini-specialist.md` with:

```yaml
---
name: gemini-specialist
description: "Specialized agent for Google Gemini API and Vertex AI integrations..."
tools:
  - view
  - edit
  - create
  - bash
  - github-mcp-server-*
---
```

### Pattern Matching

The agent is automatically assigned to issues containing keywords like:
- `gemini`, `gemini api`, `vertex ai`
- `google ai studio`, `genai`
- `gemini-cli`, `@gemini-cli`
- `gemini workflow`, `gemini review`
- And many more (see `tools/match-issue-to-agent.py`)

## Gemini Workflows Available

### 1. Gemini Dispatch (Central Router)

**File:** `.github/workflows/gemini-dispatch.yml`

This is the central dispatcher that routes `@gemini-cli` commands to specialized workflows.

**How to Use:**
```markdown
@gemini-cli /review
@gemini-cli /triage
@gemini-cli /fix
@gemini-cli <your custom request>
```

**Features:**
- Responds to comments on issues and PRs
- Routes commands to appropriate workflows
- Provides acknowledgment feedback
- Can be configured for auto-triggering

**Current Mode:** Manual only (responds to explicit `@gemini-cli` commands)

**To Enable Auto-Triggers:**
Uncomment the `pull_request` and `issues` sections in the workflow file.

### 2. Gemini Invoke (General Assistant)

**File:** `.github/workflows/gemini-invoke.yml`

Free-form AI assistance using Gemini's conversational abilities.

**Use Cases:**
- Answer questions about code
- Provide implementation suggestions
- Explain complex concepts
- Assist with troubleshooting

**Example Invocation:**
```markdown
@gemini-cli can you explain how the agent matching system works?
```

**Configuration:**
- Model: `gemini-2.0-flash` (default)
- Max session turns: 25
- Telemetry: Enabled with local logging
- GitHub MCP server: Integrated
- Shell tools: cat, echo, grep, head, tail

### 3. Gemini Review (Code Review)

**File:** `.github/workflows/gemini-review.yml`

AI-powered code reviews with inline suggestions.

**Use Cases:**
- Quality assurance before merge
- Educational feedback for contributors
- Catch potential bugs and anti-patterns
- Best practice recommendations

**Example Invocation:**
```markdown
@gemini-cli /review please check for security issues
```

**What It Analyzes:**
- Code quality and style
- Potential bugs
- Performance considerations
- Security vulnerabilities
- Best practices adherence

### 4. Gemini Triage (Auto-Labeling)

**File:** `.github/workflows/gemini-triage.yml`

Intelligent issue categorization and labeling.

**Use Cases:**
- Automatic issue organization
- Consistent labeling across repository
- Improved issue discoverability
- Reduced manual triage work

**Example Invocation:**
```markdown
@gemini-cli /triage
```

**How It Works:**
1. Fetches all repository labels
2. Analyzes issue title and body
3. Suggests appropriate labels
4. Applies labels automatically (if configured)

### 5. Gemini Fix (Automated Fixes)

**File:** `.github/workflows/gemini-fix.yml`

Implements fixes for issues using Gemini's code generation.

**Use Cases:**
- Bug fixes
- Feature implementation
- Documentation updates
- Code refactoring

**Example Invocation:**
```markdown
@gemini-cli /fix add error handling to the API endpoint
```

**What It Does:**
1. Understands issue requirements
2. Generates code solution
3. Creates a branch and PR
4. Provides detailed explanation

## Authentication Setup

The Gemini workflows support two authentication methods:

### Option 1: Google AI Studio (Recommended)

**Best for:** Personal projects, quick start, testing

**Setup Steps:**
1. Get API key from https://aistudio.google.com/app/apikey
2. Go to repository Settings > Secrets and variables > Actions
3. Create secret: Name=`GEMINI_API_KEY`, Value=your API key

**Advantages:**
- Simple setup
- No GCP account required
- Free tier available
- Great for getting started

### Option 2: Vertex AI

**Best for:** Enterprise, production, GCP users

**Setup Steps:**
1. Create GCP project with billing enabled
2. Enable Vertex AI API
3. Create API key with `aiplatform.endpoints.predict` permission
4. Add secrets:
   - `GOOGLE_API_KEY`: Your Vertex AI API key
5. Add variable:
   - `GOOGLE_GENAI_USE_VERTEXAI`: `true`

**Advantages:**
- Better for production use
- More control and compliance
- Integration with GCP services
- Enterprise support

## Creating Your Own Gemini-Focused Agent

Follow these steps to create a custom agent that uses Gemini workflows:

### Step 1: Define the Agent

Create `.github/agents/your-agent-name.md`:

```markdown
---
name: your-agent-name
description: "Your agent description focusing on Gemini capabilities"
tools:
  - view
  - edit
  - bash
  - github-mcp-server-list_workflows
  - github-mcp-server-get_file_contents
---

# Your Agent Name

Your agent instructions here...

## Core Responsibilities

1. Specific Gemini-related tasks
2. Workflow optimization
3. ...

## How I Use Gemini Workflows

Explain which workflows you leverage and when...
```

### Step 2: Add Pattern Matching

Edit `tools/match-issue-to-agent.py` and add your agent:

```python
'your-agent-name': {
    'keywords': [
        'keyword1', 'keyword2', 'gemini', 'related-terms',
        # Add 10+ keywords
    ],
    'patterns': [
        r'\bkeyword1\b', r'\bkeyword2\b', r'\bgemini\b',
        # Add 5+ regex patterns
    ]
},
```

### Step 3: Test the Matching

```bash
python3 tools/match-issue-to-agent.py \
  "Test title with keywords" \
  "Body text with relevant terms"
```

Expected output should show your agent with a score ≥ 5 for high confidence.

### Step 4: Document Usage

Create a guide in `docs/guides/` explaining:
- When to use your agent
- What workflows it leverages
- Example scenarios
- Best practices

## Configuration Variables

Control Gemini workflow behavior with repository variables:

### Required Secrets
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: Authentication

### Optional Variables
- `GEMINI_MODEL`: Model to use (default: `gemini-2.0-flash`)
- `GEMINI_CLI_VERSION`: CLI version (default: `latest`)
- `GOOGLE_GENAI_USE_VERTEXAI`: Use Vertex AI (default: `false`)
- `DEBUG`: Enable debug logging (default: `false`)
- `UPLOAD_ARTIFACTS`: Upload workflow artifacts (default: `false`)

### Model Selection

**gemini-2.0-flash:**
- Fast responses
- Cost-effective
- Good for: reviews, triage, general assistance
- Best for high-volume tasks

**gemini-2.0-pro:**
- Superior reasoning
- Detailed analysis
- Good for: complex fixes, architecture decisions
- Best for quality-critical tasks

## Advanced Workflow Customization

### MCP Server Configuration

The Gemini workflows include GitHub MCP server integration:

```yaml
mcpServers:
  github:
    command: docker
    args: [...]
    includeTools:
      - add_issue_comment
      - get_issue
      - create_pull_request
      # ... more tools
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_TOKEN}
```

**Available MCP Tools:**
- Issue management (get, comment, list, search)
- PR operations (create, read, list, search)
- Branch operations (create)
- File operations (create, update, delete)
- Code search
- And more...

### Custom Prompts

Each workflow can use custom prompts. For example, to create a specialized review prompt:

1. Create `.github/prompts/custom-review.md`
2. Update workflow to use: `prompt: '/custom-review'`

### Telemetry and Monitoring

Enable telemetry to track Gemini usage:

```yaml
telemetry:
  enabled: true
  target: "local"
  outfile: ".gemini/telemetry.log"
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Found
**Error:** "Missing Gemini API Key"

**Solution:**
- Verify secret name matches exactly: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- Check secret is in Actions secrets (not variables)
- Ensure secret has the correct API key value

#### 2. Vertex AI Permission Denied
**Error:** "aiplatform.endpoints.predict permission denied"

**Solutions:**
- Enable Vertex AI API in GCP console
- Grant proper IAM permissions to API key
- Ensure billing is enabled on GCP project
- OR switch to Google AI Studio (simpler)

#### 3. Workflow Not Triggering
**Error:** Gemini workflows don't run

**Possible Causes:**
- Not using `@gemini-cli` command format
- User doesn't have proper repository permissions
- Workflow is disabled
- Concurrency limits reached

**Solutions:**
- Use exact format: `@gemini-cli /command`
- Ensure user is OWNER, MEMBER, or COLLABORATOR
- Check workflow is enabled in Actions settings
- Wait for other runs to complete

#### 4. Poor Quality Responses
**Error:** Gemini gives generic or incorrect responses

**Solutions:**
- Provide more context in your request
- Use more specific prompts
- Consider switching to gemini-2.0-pro for complex tasks
- Review and optimize prompt templates

## Best Practices

### 1. Choose the Right Workflow
- **Review:** Code quality checks, educational feedback
- **Triage:** Issue organization, labeling
- **Fix:** Implementation tasks, bug fixes
- **Invoke:** Questions, explanations, general help

### 2. Provide Good Context
```markdown
# ✅ Good
@gemini-cli /review please check for SQL injection vulnerabilities in the auth module

# ❌ Bad
@gemini-cli /review check this
```

### 3. Use Appropriate Models
- High-volume, simple tasks → Flash
- Complex reasoning, quality-critical → Pro

### 4. Secure Your API Keys
- Never commit API keys to code
- Use GitHub Secrets properly
- Rotate keys regularly
- Monitor usage for anomalies

### 5. Monitor and Optimize
- Review telemetry logs
- Track API usage and costs
- Optimize prompts based on results
- Adjust models based on needs

## Example Use Cases

### Case 1: Automated Code Review Pipeline
```markdown
# On PR creation, trigger automatic review
@gemini-cli /review focus on security and performance
```

**Result:** Gemini analyzes changes, provides inline suggestions, catches issues

### Case 2: Issue Triage Automation
```markdown
# On issue creation, auto-label
@gemini-cli /triage
```

**Result:** Issue automatically tagged with appropriate labels

### Case 3: Quick Bug Fix
```markdown
# On bug report, generate fix
@gemini-cli /fix add null check before accessing user.email
```

**Result:** Gemini creates PR with fix and tests

### Case 4: Knowledge Base Assistant
```markdown
# Ask questions about codebase
@gemini-cli how does the authentication flow work?
```

**Result:** Gemini explains with code references

## Integration with Other Agents

The Gemini Specialist can collaborate with other agents:

- **@troubleshoot-expert**: For workflow debugging
- **@secure-specialist**: For security-focused reviews
- **@document-ninja**: For documentation generation
- **@meta-coordinator**: For multi-agent task coordination

## Performance Tracking

The Gemini Specialist agent is evaluated on:
- **Code Quality (30%)**: Clean workflow configurations
- **Issue Resolution (25%)**: Successfully resolved Gemini issues
- **PR Success (25%)**: Merged PRs improving Gemini usage
- **Peer Review (20%)**: Quality of Gemini-related reviews

## Resources

### Documentation
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [GitHub Actions - Run Gemini CLI](https://github.com/marketplace/actions/run-gemini-cli)

### Repository Files
- Agent Definition: `.github/agents/gemini-specialist.md`
- Pattern Matching: `tools/match-issue-to-agent.py`
- Workflows: `.github/workflows/gemini-*.yml`

### Getting Help

For Gemini-related issues:
1. Check this guide first
2. Review workflow logs in Actions tab
3. Create issue mentioning `@gemini-specialist`
4. Provide details: error messages, what you tried, expected behavior

## Conclusion

The Gemini Specialist agent demonstrates how to create custom agents that leverage specific AI workflows. By combining:
- Clear agent definitions
- Pattern-based assignment
- Specialized workflows
- Good documentation

You can build powerful, focused agents that excel at specific tasks within the autonomous AI ecosystem.

---

*Happy automating with Gemini! 🌟*
