# Product Owner Agent Workflow Analysis

## Current Flow Analysis

### Step-by-Step Flow

1. **User creates vague issue**
   - Title: "Improve performance"
   - Body: "The system is slow. Make it faster."

2. **`copilot-graphql-assign.yml` triggers** on `issues.opened`
   - Runs `assign-copilot-to-issue.sh`
   - Calls `match-issue-to-agent.py` with issue title/body
   - Vague language detected → Matches to `product-owner` agent

3. **Issue is updated by workflow**
   - Adds `copilot-assigned` label (prevents re-processing)
   - Adds `agent:product-owner` label
   - Prepends agent directive to issue body:
     ```markdown
     > **🤖 Agent Assignment**
     > @product-owner - Please use the specialized approach...
     ```

4. **Copilot is assigned via GraphQL API**
   - Issue assigned to GitHub Copilot
   - Copilot reads issue body with `@product-owner` directive

5. **@product-owner agent enhances the issue**
   - Copilot works as @product-owner (per agent definition)
   - Following template in `.github/agents/product-owner.md`
   - **Gap Identified**: PO agent needs to:
     - Update the issue body with enhanced content
     - Recommend specialist agent (e.g., "@accelerate-master")
     - **CRITICAL**: Must trigger re-assignment somehow

## Identified Gap: Re-Assignment

### The Problem

After @product-owner enhances the issue, there's **no automatic mechanism** to:
1. Trigger re-assignment to the recommended specialist
2. Update labels from `agent:product-owner` to `agent:specialist`
3. Remove `copilot-assigned` label to allow re-processing

### Current Behavior

**Without intervention:**
- @product-owner enhances issue and closes it (task complete)
- Issue remains assigned to Copilot with `copilot-assigned` label
- No specialist agent ever picks it up
- **Work stops at enhancement step**

### Why This Happens

The `copilot-assigned` label acts as a "lock" (lines 73-77 in `assign-copilot-to-issue.sh`):

```bash
if echo "$issue_labels" | grep -q "copilot-assigned"; then
  echo "✓ Issue #$issue_number has copilot-assigned label, likely in-progress assignment"
  already_assigned_count=$((already_assigned_count + 1))
  continue  # SKIPS re-processing
fi
```

Once added, this label prevents the workflow from ever re-running on the issue.

## Solution Options

### Option A: Product Owner Updates Labels (Recommended)

**@product-owner agent instructions should include:**

```markdown
## After Enhancement

Once you've enhanced the issue, you MUST:

1. **Update the issue body** with your enhanced content
2. **Update labels:**
   - Remove: `copilot-assigned` (allows re-assignment)
   - Remove: `agent:product-owner` (you're done)
   - Keep: All other labels
3. **Add comment** recommending specialist:
   ```
   ✅ Issue enhanced by @product-owner
   
   Recommended specialist: @accelerate-master
   
   Issue is ready for re-assignment.
   ```
4. **Unassign yourself** (Copilot) from the issue
5. **Do NOT close the issue** - specialist needs to work on it

The `copilot-graphql-assign` workflow will automatically detect:
- Issue is open
- No `copilot-assigned` label
- No Copilot assignee

It will then re-run agent matching (using enhanced content) and assign the specialist.
```

**Workflow Integration:**
- PO removes `copilot-assigned` label
- Workflow detects issue is now "unassigned" (label check at line 73-77 fails)
- Workflow re-runs matching with ENHANCED content
- Better match to specialist (because requirements are now clear)
- Specialist gets assigned and implements the work

### Option B: Separate Handoff Workflow

Create `.github/workflows/product-owner-handoff.yml`:

```yaml
name: Product Owner Handoff

on:
  issue_comment:
    types: [created]

jobs:
  handoff:
    if: |
      contains(github.event.comment.body, '✅ Enhanced by @product-owner') &&
      contains(github.event.issue.labels.*.name, 'agent:product-owner')
    runs-on: ubuntu-latest
    steps:
      - name: Remove PO labels and trigger re-assignment
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Remove labels to allow re-assignment
          gh issue edit ${{ github.event.issue.number }} \
            --remove-label "copilot-assigned" \
            --remove-label "agent:product-owner"
          
          # Unassign Copilot
          gh issue edit ${{ github.event.issue.number }} --remove-assignee @me
          
          echo "✅ Cleared labels, ready for re-assignment"
```

**Pros:**
- Fully automated
- PO just needs to comment
- Workflow handles cleanup

**Cons:**
- Additional workflow complexity
- Depends on comment format

### Option C: Manual Label Management

**User manually:**
1. Sees PO enhancement comment
2. Removes `copilot-assigned` label manually
3. Workflow auto-detects and re-assigns

**Pros:**
- Simple, no code changes
- User has control

**Cons:**
- Manual intervention required
- Defeats automation purpose

## Recommended Implementation: Option A

Update `.github/agents/product-owner.md` to include explicit label management instructions:

### Add to Product Owner Agent Definition

```markdown
## Critical: Enabling Handoff to Specialist

Your work as product owner is **preparation**, not implementation. After enhancement:

### Required Actions

1. **Update Issue Body**
   - Replace original with enhanced version
   - Use your template (user story, acceptance criteria, etc.)
   - Preserve original in collapsed section

2. **Manage Labels** (CRITICAL for automation)
   ```bash
   # You can use gh CLI or suggest these changes
   # Remove these labels:
   - copilot-assigned  # Allows re-assignment workflow to run
   - agent:product-owner  # Your work is complete
   ```

3. **Add Completion Comment**
   ```markdown
   ✅ **Issue Enhanced by @product-owner**
   
   The issue has been transformed into a structured format with:
   - User story
   - Acceptance criteria
   - Technical considerations
   - Context and background
   
   **Recommended Specialist:** @[specialist-name]
   
   **Next Steps:**
   The issue is now ready for re-assignment. The copilot workflow will automatically:
   1. Detect the enhanced, well-structured content
   2. Match to the appropriate specialist agent
   3. Assign Copilot with specialist directive
   
   Labels updated to allow re-processing.
   ```

4. **Unassign Yourself**
   - Issue should not remain assigned to you
   - Allows automation to reassign to specialist

5. **Keep Issue Open**
   - Do NOT close the issue
   - Specialist needs to implement the work
   - Only close if requirements cannot be clarified

### What Happens Next (Automated)

After you complete these actions:

1. ✅ `copilot-assigned` label removed → Workflow can re-run
2. ✅ Enhanced content in issue → Better matching accuracy
3. ✅ `copilot-graphql-assign` workflow detects open issue without labels
4. ✅ Runs `match-issue-to-agent.py` with ENHANCED content
5. ✅ Matches to specialist (e.g., @accelerate-master, @engineer-master)
6. ✅ Specialist gets assigned and implements solution

### Example Flow

**Before (Vague):**
```
Title: Performance is bad
Body: The site is slow
Labels: none
Match: product-owner (vague language detected)
```

**After PO Enhancement:**
```
Title: Performance is bad
Body: ## User Story
As a user, I want pages to load under 2 seconds...
## Acceptance Criteria
- [ ] Identify bottlenecks
- [ ] Reduce load time by 30%
Labels: none (PO removed copilot-assigned)
Match: accelerate-master (clear performance requirements)
```

**Result:** @accelerate-master assigned, implements optimizations.
```

## Testing the Flow

### Test Scenario 1: Happy Path

1. Create issue: "Improve the dashboard"
2. Workflow assigns @product-owner
3. PO enhances with structured format
4. PO removes `copilot-assigned` label
5. PO unassigns self
6. Workflow re-runs (no label, no assignee)
7. Matches to specialist based on enhanced content
8. Specialist assigned and implements

### Test Scenario 2: Missing Label Removal

1. Create issue: "Make it better"
2. Workflow assigns @product-owner
3. PO enhances but FORGETS to remove label
4. **Issue stuck** - workflow won't re-run
5. Manual intervention required OR PO needs to be instructed properly

## Conclusion

**Current Gap:** Product owner agent has no built-in mechanism to trigger re-assignment after enhancement.

**Solution:** Update product-owner agent definition to explicitly instruct label management and self-unassignment as part of the enhancement workflow.

**Result:** Full automation with proper handoff from PO to specialist.

## Action Items

- [ ] Update `.github/agents/product-owner.md` with label management instructions
- [ ] Add example of proper handoff in agent documentation
- [ ] Test with sample vague issue
- [ ] Document in `PRODUCT_OWNER_AGENT.md` user guide
- [ ] Consider Option B (handoff workflow) as future enhancement
