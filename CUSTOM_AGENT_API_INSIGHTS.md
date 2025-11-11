# Custom Agent API Insights Summary

## Quick Reference

This document provides a quick reference for the key insights from analyzing GitHub Copilot custom agent API invocations. For detailed analysis, see [CUSTOM_AGENT_API_INVOCATION.md](./docs/CUSTOM_AGENT_API_INVOCATION.md).

## Key Discovery

**Agent selection happens via environment variables, not GraphQL mutation parameters.**

When a custom agent is invoked, the specific agent/model is specified through the `COPILOT_AGENT_MODEL` environment variable:

```bash
COPILOT_AGENT_MODEL: sweagent-capi:claude-sonnet-4.5
```

This means:
- ✅ Issue assignment via GraphQL assigns to "Copilot" (generic)
- ✅ Agent specialization is determined at runtime invocation
- ⚠️ The mechanism for mapping metadata → agent model is not fully documented

## Critical Environment Variables

From actual GitHub Actions logs ([run 19253915320](https://github.com/enufacas/Chained/actions/runs/19253915320/job/55044456947)):

```bash
# Agent Model Selection
COPILOT_AGENT_MODEL: sweagent-capi:claude-sonnet-4.5

# User Context
COPILOT_AGENT_ACTOR: enufacas
COPILOT_AGENT_ACTOR_ID: 1485431

# Task Context
COPILOT_AGENT_ACTION: fix
COPILOT_AGENT_PROMPT: RG9jIG1hc3RlciB3aGF0IGlzIHlvdXIgYWN0b3JpZD8=  # Base64
COPILOT_AGENT_ISSUE_NUMBER: 0

# Runtime
COPILOT_AGENT_RUNTIME_VERSION: runtime-f3613bf5ec2817b73adf2dd3f90afcf66893ba7a
COPILOT_AGENT_TIMEOUT_MIN: 59

# API Endpoints
COPILOT_API_URL: https://api.githubcopilot.com
COPILOT_AGENT_CALLBACK_URL: https://api.githubcopilot.com/agents/swe/agent
```

## Tool Restrictions

Custom agents may have **limited tool access**. From the logs:

**Available in this instance:**
- `view`, `create`, `edit`, `report_progress`

**NOT available in this instance:**
- `bash` - Shell command execution
- GitHub API tools
- Web search
- Browser/Playwright tools

**Configure tools in:** `.github/agents/<agent-name>.md`

## Agent Preparation Phase

The logs reveal that agents go through an **orientation phase** when first invoked:

### 1. Repository Navigation
```
Agent explores filesystem:
/root → /home → /home/runner → /home/runner/work → repository
```

### 2. Tool Discovery
```
Agent attempts tools and learns restrictions from error messages:
"Tool 'bash' does not exist. Available tools are view, create, edit, report_progress."
```

### 3. Convention Search
```
Agent searches for standard files:
- PR templates
- Configuration files
- Repository conventions
```

### 4. Response Format Learning
```
Agent learns expected formats from error feedback:
"Agent response did not contain expected template_path and template_content tags"
```

## Response Format Requirements

For certain workflows, agents must structure responses with XML-style tags:

```xml
<template_path>path/to/template.md</template_path>
<template_content>
# Template content here
</template_content>
```

## Assignment Flow

```
1. Create Issue
   ↓
2. Match to Agent (via intelligent matching)
   ↓
3. Add Metadata (labels, body directives)
   ├─ Label: "agent:doc-master"
   ├─ Body directive: "<!-- COPILOT_AGENT:doc-master -->"
   └─ Comment: "@copilot use doc-master agent"
   ↓
4. Assign via GraphQL
   mutation replaceActorsForAssignable(
     issueId: "<ID>",
     actorIds: ["<COPILOT_ACTOR_ID>"]  # Generic Copilot
   )
   ↓
5. Copilot Runtime Reads Metadata
   (Mechanism unknown - likely reads labels/directives)
   ↓
6. Runtime Sets Environment Variables
   COPILOT_AGENT_MODEL="sweagent-capi:claude-sonnet-4.5"
   + many other COPILOT_AGENT_* variables
   ↓
7. Agent Executes with Configured Tools
   ↓
8. Agent Creates PR with Solution
```

## The Missing Link

**Unknown**: How does Copilot runtime map issue metadata to `COPILOT_AGENT_MODEL`?

Hypotheses:
- A. Label parsing: `agent:doc-master` → specific model config
- B. Directive parsing: `<!-- COPILOT_AGENT:doc-master -->` → model
- C. External config file with agent-to-model mappings
- D. Manual UI selection stored in GitHub's database

## Practical Recommendations

### For Workflows
1. ✅ Use GraphQL mutation to assign issues to Copilot
2. ✅ Add multiple forms of metadata (labels + directives + comments)
3. ✅ Log assignment method and actor IDs for debugging
4. ✅ Document tool requirements in agent definition files

### For Custom Agents
1. ✅ Define tools explicitly in `.github/agents/<name>.md`
2. ✅ Don't assume `bash` or all tools are available
3. ✅ Use structured responses (XML tags) when required
4. ✅ Handle base64-encoded prompts

### For Debugging
1. ✅ Check `COPILOT_AGENT_*` environment variables in logs
2. ✅ Look for "Tool does not exist" errors
3. ✅ Verify GraphQL mutation success
4. ✅ Inspect response format expectations

## Open Questions

1. How exactly does metadata map to `COPILOT_AGENT_MODEL`?
2. Can tool configurations be customized per agent?
3. Do custom agents have separate actor IDs?
4. What other response formats are expected?
5. How do runtime versions affect behavior?

## Documentation Links

- **[Detailed Analysis](./docs/CUSTOM_AGENT_API_INVOCATION.md)** - Complete log analysis
- **[Assignment Investigation](./CUSTOM_AGENT_ASSIGNMENT_INVESTIGATION.md)** - Full investigation
- **[Inspecting Assignments](./docs/INSPECTING_AGENT_ASSIGNMENTS.md)** - Discovery tools
- **[Assignment Limitations](./docs/CUSTOM_AGENT_ASSIGNMENT_LIMITATIONS.md)** - Known constraints
- **[Actor ID System](./docs/ACTOR_ID_SYSTEM.md)** - ID systems explained

## Source

Analysis based on GitHub Actions run:
https://github.com/enufacas/Chained/actions/runs/19253915320/job/55044456947

---

**Last Updated**: 2025-11-11  
**Status**: Active investigation
