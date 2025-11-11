# Custom Agent Assignment Investigation Summary

## What We Did

### 1. Investigated the Problem
We researched GitHub's API and documentation to understand how custom agent assignment works when multiple agents exist in `.github/agents/`.

**Key Discovery**: The GitHub GraphQL API has **no parameter** to specify which custom agent to use when assigning Copilot to an issue.

### 2. Explored the API
- GraphQL `replaceActorsForAssignable` mutation only has:
  - `assignableId` - the issue ID  
  - `actorIds` - list of actor IDs to assign
  - **No field for custom agent selection**

- Custom agent selection works via:
  - ✅ UI dropdown (manual selection)
  - ✅ CLI `/agent <name>` command (interactive)
  - ❌ API (not supported)

### 3. Implemented Workarounds
Since the API doesn't support it, we added multiple mechanisms to communicate the agent selection:

**A. Agent Labels**
```yaml
gh issue edit --add-label "agent:bug-hunter"
```

**B. Issue Body Directive**
```markdown
> **🤖 Agent Assignment**
> This issue has been assigned to GitHub Copilot with the bug-hunter custom agent profile.
> Please use the specialized approach defined in `.github/agents/bug-hunter.md`.
```

**C. Comment Directive**
```markdown
@copilot please use the **bug-hunter** custom agent profile from `.github/agents/bug-hunter.md`
```

### 4. Created Debug Tools

**Debug Workflow** (`.github/workflows/debug-custom-agents.yml`)
- Manually triggerable
- Queries all actors in the repository
- Searches for custom agent names
- Determines if custom agents have actor IDs

**Python Script** (`tools/debug_custom_agent_actors.py`)
- Standalone debugging tool
- Can be run locally with GH_TOKEN
- Analyzes actor IDs vs custom agents
- Provides clear conclusions

### 5. Documented Everything

**Limitations Document** (`docs/CUSTOM_AGENT_ASSIGNMENT_LIMITATIONS.md`)
- Explains API limitations
- Documents workaround approaches
- Lists alternative options considered
- Provides recommendations

## The Critical Unknown

**Question**: Do custom agents (bug-hunter, feature-architect, etc.) have their own actor IDs?

### If YES:
✅ **We can fix this properly!**
- Assign directly to custom agent actor IDs
- Remove workaround directives
- Use proper API assignment

### If NO:
❌ **API limitation confirmed**
- Keep workaround directives
- Hope Copilot reads issue context
- Wait for GitHub to add API support

## Next Steps

### 1. Run the Debug Workflow
```
1. Go to repository Actions tab
2. Select "Debug Custom Agent Actors" workflow
3. Click "Run workflow"
4. Wait for results
5. Review the output
```

### 2. Analyze Results

**If custom agents appear as actors with IDs:**
1. Update `copilot-graphql-assign.yml` to use those actor IDs
2. Remove directive workarounds (not needed)
3. Assign directly to matched agent

**If custom agents don't appear as actors:**
1. Keep current workaround approach
2. Document that this is best-effort
3. Consider alternative approaches (see below)

### 3. Alternative Approaches (if needed)

**Option A: Single Meta-Agent**
- Replace 11 agents with 1 adaptive agent
- Agent analyzes issue and adapts behavior
- Works within API limitations

**Option B: Dynamic Agent Swapping**
- Temporarily keep only matched agent in `.github/agents/`
- Ensures correct agent is used
- Complex and error-prone

**Option C: UI-Only Assignment**
- Remove API assignment
- Require manual agent selection
- Defeats automation purpose

## Files Changed

### Modified
- `.github/workflows/copilot-graphql-assign.yml`
  - Added agent labels
  - Added issue body directive
  - Enhanced comment directive

### Created
- `.github/workflows/debug-custom-agents.yml`
  - Debug workflow for actor exploration
  
- `tools/debug_custom_agent_actors.py`
  - Python debug script
  
- `docs/CUSTOM_AGENT_ASSIGNMENT_LIMITATIONS.md`
  - Comprehensive documentation

## Testing Checklist

- [x] Research GitHub API and documentation
- [x] Implement workaround directives
- [x] Create debug tools
- [x] Document findings and limitations
- [x] Run security checks (codeql) - ✅ PASSED
- [ ] **Run debug workflow to discover actor IDs**
- [ ] Update workflow based on debug results
- [ ] Test with actual issue assignment
- [ ] Verify Copilot behavior
- [ ] Document final solution

## Security Summary

✅ **No security vulnerabilities found**
- CodeQL analysis passed for actions and python
- No secrets or sensitive data exposed
- Proper use of GitHub tokens
- Safe GraphQL queries

## Recommendations

### Immediate
1. **Run the debug workflow** - This is the critical next step
2. **Analyze the results** - Determine if custom agents have actor IDs
3. **Update workflow accordingly** - Based on findings

### Long-term
1. **Monitor Copilot behavior** - Does it respect the directives?
2. **Track GitHub updates** - Watch for API improvements
3. **Gather metrics** - Which agents work on which issues?

## Questions for Review

1. Should we run the debug workflow now to get immediate answers?
2. Are we comfortable with the workaround approach if actors aren't found?
3. Should we consider simplifying to a single meta-agent?
4. Do we want to add metrics/tracking to see if directives work?

## References

- [GitHub Docs: Creating Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [GitHub Docs: Assigning Issues to Copilot](https://docs.github.com/copilot/how-tos/use-copilot-agents/coding-agent/assign-copilot-to-an-issue)
- [GitHub GraphQL API: Mutations](https://docs.github.com/en/graphql/reference/mutations)
- [Custom Agents Configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

---

**Status**: ✅ Implementation complete, awaiting debug results to finalize approach

**Date**: 2025-11-11

**Author**: GitHub Copilot Coding Agent
