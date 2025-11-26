# Quick Start: Gemini Specialist Agent

## What is it?

A custom agent in the Chained ecosystem that exclusively uses Google Gemini API workflows for AI-powered automation.

## When to Use

Use `@gemini-specialist` for:
- Gemini API configuration issues
- Vertex AI authentication problems  
- Gemini workflow failures
- Model selection questions
- Prompt optimization
- GenAI automation setup

## Quick Invocation

### Automatic Assignment
Just create an issue with Gemini-related keywords and the agent is automatically assigned:

```markdown
Title: Setup Gemini code reviews
Body: Need help configuring gemini-cli for PR reviews
```

### Manual Mention
Explicitly mention the agent in any issue:

```markdown
@gemini-specialist please help configure Vertex AI authentication
```

## Available Gemini Workflows

### 1. Code Review
```markdown
@gemini-cli /review
```
Get AI-powered code review with inline suggestions

### 2. Issue Triage
```markdown
@gemini-cli /triage
```
Auto-label issues based on content

### 3. Automated Fix
```markdown
@gemini-cli /fix add error handling
```
Generate and implement code fixes

### 4. General Assistant
```markdown
@gemini-cli explain how the auth flow works
```
Ask questions, get help

## Authentication Setup

### Option 1: Google AI Studio (Recommended)
1. Get key: https://aistudio.google.com/app/apikey
2. Add secret: `GEMINI_API_KEY`

### Option 2: Vertex AI (Enterprise)
1. Create GCP project
2. Add secret: `GOOGLE_API_KEY`
3. Add variable: `GOOGLE_GENAI_USE_VERTEXAI=true`

## Common Scenarios

### Scenario: Setup First Time
```markdown
Issue: How do I add Gemini to my repo?
Agent: Guides through API key setup, workflow installation, testing
```

### Scenario: Permission Error
```markdown
Issue: Vertex AI permission denied
Agent: Diagnoses IAM issues, suggests fixes or AI Studio alternative
```

### Scenario: Optimize Usage
```markdown
Issue: Gemini is slow and expensive
Agent: Recommends Flash model, optimizes prompts, adjusts triggers
```

## Model Selection

- **gemini-2.0-flash**: Fast, cost-effective (reviews, triage)
- **gemini-2.0-pro**: High quality, complex reasoning (architecture, security)

## Documentation

- **Full Guide**: `docs/guides/GEMINI_SPECIALIST_AGENT_GUIDE.md`
- **Agent Definition**: `.github/agents/gemini-specialist.md`
- **Workflows**: `.github/workflows/gemini-*.yml`

## Example Issue

```markdown
Title: Configure Gemini for automatic PR reviews

Hi @gemini-specialist,

I want to set up automated code reviews using Gemini. I have:
- GitHub Actions enabled
- Google AI Studio account

What do I need to do?

Thanks!
```

**Result**: Agent automatically assigned, provides step-by-step setup guide

## Testing Your Setup

```bash
# Test pattern matching
python3 tools/match-issue-to-agent.py \
  "Setup Gemini API" \
  "Need help with Gemini CLI configuration"

# Expected: gemini-specialist with high score (≥9)
```

## Getting Help

1. Check the full guide first
2. Review workflow logs
3. Create issue mentioning `@gemini-specialist`
4. Provide error messages and what you tried

---

**Part of the Chained autonomous AI ecosystem** 🌟
