# Custom Agent Assignment Limitations

## Overview

This document explains the current limitations of GitHub Copilot's API when working with multiple custom agents and how this repository attempts to work around them.

## The Problem

When using GitHub's API to assign Copilot to an issue, there is **no official way to specify which custom agent profile should be used** when multiple agents exist in `.github/agents/`.

### What Works

✅ **UI Assignment**: When manually assigning Copilot via GitHub's web interface, you can select which custom agent to use from a dropdown.

✅ **CLI Usage**: When using the GitHub Copilot CLI, you can invoke specific agents using `/agent <name>` command.

✅ **API Assignment**: You can assign the generic Copilot bot to an issue via the GraphQL API.

### What Doesn't Work

❌ **API Agent Selection**: The GraphQL `replaceActorsForAssignable` mutation has no parameter to specify which custom agent profile to use.

## API Structure

The `replaceActorsForAssignable` mutation only accepts:
```graphql
mutation {
  replaceActorsForAssignable(input: {
    assignableId: "<ISSUE_ID>",
    actorIds: ["<COPILOT_ACTOR_ID>"],
    clientMutationId: "optional-tracking-id"
  }) {
    # ...
  }
}
```

**Missing**: No field for `agentProfile`, `customAgent`, or similar to specify which agent.

## Current Workaround

This repository uses a **best-effort approach** to communicate agent selection:

### 1. Intelligent Matching
The workflow analyzes issue content and identifies the most appropriate agent:
- `bug-hunter` for bug reports
- `feature-architect` for new features
- `doc-master` for documentation
- etc.

### 2. Multiple Communication Methods
The workflow attempts to communicate the matched agent through:

**A. Labels**: Adds `agent:<agent-name>` label to the issue
```yaml
gh issue edit --add-label "agent:bug-hunter"
```

**B. Issue Body Directive**: Prepends agent instruction to issue description
```markdown
> **🤖 Agent Assignment**
> This issue has been assigned to GitHub Copilot with the bug-hunter custom agent profile.
> Please use the specialized approach defined in `.github/agents/bug-hunter.md`.
```

**C. Assignment Comment**: Adds a comment mentioning the agent
```markdown
@copilot please use the **bug-hunter** custom agent profile from `.github/agents/bug-hunter.md` when working on this issue.
```

### 3. Hope for the Best
Since these methods are not officially documented, we hope that:
- Copilot's system reads and respects these directives
- The issue context influences agent selection
- Future GitHub updates will make this work

## Limitations of This Approach

### Uncertainty
- ⚠️ **Not officially supported**: GitHub doesn't document that Copilot respects these directives
- ⚠️ **May be ignored**: Copilot might use a default agent or random selection
- ⚠️ **No guarantee**: Success rate unknown and untestable

### What Copilot Might Actually Do
When assigned to an issue with multiple custom agents, Copilot likely:
1. Uses the first agent found alphabetically
2. Uses a repository-level default (if configured)
3. Uses built-in default behavior
4. **Unknown** - behavior is not documented

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
- [GitHub Docs: Creating Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [GitHub Docs: Assigning Issues to Copilot](https://docs.github.com/copilot/how-tos/use-copilot-agents/coding-agent/assign-copilot-to-an-issue)

## Updates

**2025-11-11**: Initial documentation after researching API limitations and implementing workaround directives.

---

*This limitation exists as of November 2025. Check GitHub's documentation for updates.*
