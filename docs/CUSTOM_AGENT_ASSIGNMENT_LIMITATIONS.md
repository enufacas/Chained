# Custom Agent Assignment

## Overview

This document explains how this repository handles custom agent assignment via GitHub's GraphQL API, including both direct assignment (when supported) and fallback approaches.

## The Solution

This repository now implements **intelligent custom agent assignment** that attempts direct API assignment to custom agents when possible, with automatic fallback to directive-based assignment.

### Assignment Methods

The workflow now uses a **two-tier approach**:

#### Method 1: Direct Custom Agent Assignment (Preferred)

The workflow first attempts to find the custom agent as a separate actor in the GitHub API:

```bash
# Query all available actors
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      suggestedActors(capabilities: [CAN_BE_ASSIGNED], first: 100) {
        nodes {
          login
          __typename
          ... on Bot { id }
          ... on User { id }
        }
      }
    }
  }'

# Try to find custom agent by name (e.g., "bug-hunter")
custom_agent_actor_id=$(... | select(.login == "bug-hunter") | .id)
```

**If found:** Assign directly to the custom agent actor ID
- ✅ Direct API assignment to specific custom agent
- ✅ No directives needed
- ✅ Guaranteed agent selection

#### Method 2: Generic Copilot with Directives (Fallback)

If the custom agent doesn't have a separate actor ID, the workflow falls back to the previous approach:

1. Assigns to the generic Copilot bot
2. Adds agent-specific label (`agent:bug-hunter`)
3. Prepends directive to issue body
4. Adds comment with agent instructions

### How It Works

## Alternative Approaches Considered

### Option A: Single Meta-Agent
**Approach**: Replace 11 specialized agents with one agent that adapts based on issue content.

**Pros**:
- Works within API limitations
- Still provides specialized behavior
- Cleaner with current constraints

**Cons**:
- Loses explicit agent definitions
- Less transparent
- All behavior in one large file

### Option B: Dynamic Agent Swapping
**Approach**: Temporarily rename/move agent files so only the matched agent exists during assignment.

**Pros**:
- Guarantees correct agent selection
- Works with current API

**Cons**:
- Complex implementation
- Race conditions with concurrent assignments
- Git history pollution
- Fragile and error-prone

### Option C: Manual Assignment Only
**Approach**: Skip API assignment, require manual agent selection via UI.

**Pros**:
- Reliable agent selection
- Uses officially supported method

**Cons**:
- Defeats automation purpose
- Requires manual intervention
- Slower workflow

## Current Decision

We're using the **multiple communication methods** approach (Option from main solution) because:

1. **Documents Intent**: Even if ignored, it clearly shows which agent was matched
2. **Future-Proof**: If GitHub adds support, our directives might start working
3. **Best Effort**: Provides value even if partial
4. **Transparent**: Users can see the matching logic and agent selection
5. **Non-Breaking**: Doesn't prevent Copilot from working, just potentially with wrong specialization

## Recommendations

### For Repository Maintainers
- ✅ Keep the intelligent matching system for transparency
- ✅ Monitor if Copilot respects the agent directives
- ✅ Update this documentation if GitHub adds official support
- ⚠️ Be aware that agent selection may not work as intended

### For Issue Creators
- If specific agent behavior is critical, manually assign via UI
- Mention the desired agent in the issue description
- Add relevant labels to help with matching

### For GitHub
We hope future API versions will add:
```graphql
mutation {
  replaceActorsForAssignable(input: {
    assignableId: "<ISSUE_ID>",
    actorIds: ["<COPILOT_ACTOR_ID>"],
    customAgent: "bug-hunter"  # ← THIS WOULD BE GREAT!
  })
}
```

## Testing & Validation

### How to Test
1. Create test issues with clear agent matches
2. Let workflow assign with directives
3. Observe which agent behavior Copilot exhibits
4. Check if specialized instructions are followed

### Success Metrics
- Does Copilot follow agent-specific guidelines?
- Are agent tools being used appropriately?
- Do PRs reflect agent specialization?

### Current Status
- ❓ **Unknown**: Not yet validated if directives influence Copilot
- 📊 **Tracking Needed**: Monitor Copilot's behavior patterns
- 🔬 **Experimental**: Consider this approach as experimental

## Related Documentation

- [Intelligent Agent Matching](./INTELLIGENT_AGENT_MATCHING.md) - How agents are matched to issues
- [Custom Agents Conventions](./CUSTOM_AGENTS_CONVENTIONS.md) - Agent definitions and structure
- [Custom Agent API Invocation](./CUSTOM_AGENT_API_INVOCATION.md) - **NEW**: Deep insights from actual API logs
- [Inspecting Agent Assignments](./INSPECTING_AGENT_ASSIGNMENTS.md) - Tools for discovering actor IDs
- [GitHub Docs: Creating Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [GitHub Docs: Assigning Issues to Copilot](https://docs.github.com/copilot/how-tos/use-copilot-agents/coding-agent/assign-copilot-to-an-issue)

## Updates

**2025-11-11**: Initial documentation after researching API limitations and implementing workaround directives.

---

*This limitation exists as of November 2025. Check GitHub's documentation for updates.*
