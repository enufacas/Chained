# Product Owner Agent Flow Analysis

## Current Flow (Option 2 Implementation)

### Step-by-Step Process

```
1. User creates vague issue
   ↓
2. copilot-graphql-assign.yml triggers (on issues.opened)
   ↓
3. assign-copilot-to-issue.sh runs
   ↓
4. match-issue-to-agent.py analyzes issue content
   ↓
5. Detects vague language → Matches to @product-owner
   ↓
6. Adds labels:
   - "copilot-assigned" (to claim issue)
   - "agent:product-owner" (to identify agent)
   ↓
7. Updates issue body with agent directive:
   - Adds HTML comment: <!-- COPILOT_AGENT:product-owner -->
   - Adds @product-owner mention
   - Links to .github/agents/product-owner.md
   ↓
8. Assigns issue to Copilot via GraphQL API
   ↓
9. Posts success comment with agent details
   ↓
10. Copilot reads issue (with @product-owner directive)
    ↓
11. Copilot uses product-owner agent profile
    ↓
12. Product-owner enhances issue description
```

## ⚠️ IDENTIFIED GAP: Step 12 → Next Assignment

**Current Gap:**
After product-owner enhances the issue, there is NO automatic mechanism to:
1. Remove the product-owner assignment
2. Re-analyze the enhanced issue content
3. Match to the appropriate specialized agent
4. Assign the new agent to continue work

### Why This Happens

**Copilot-assigned label prevents re-assignment:**
- Line 73-77 in assign-copilot-to-issue.sh:
  ```bash
  if echo "$issue_labels" | grep -q "copilot-assigned"; then
    echo "✓ Issue #$issue_number has copilot-assigned label, likely in-progress assignment"
    already_assigned_count=$((already_assigned_count + 1))
    continue
  fi
  ```

**No trigger on issue edits:**
- copilot-graphql-assign.yml only triggers on:
  - `issues.opened` (not `issues.edited`)
  - Schedule (every 15 minutes)
  - Manual dispatch
  - After specific workflows complete

**Product-owner cannot trigger workflows:**
- When Copilot (as product-owner) edits the issue, it doesn't trigger `issues.edited`
- Even if it did, the workflow would skip due to `copilot-assigned` label

## 🔧 Solution Options

### Option A: Product Owner Self-Manages Labels (Recommended)

**Product-owner agent workflow:**
1. Enhance issue description
2. Remove `copilot-assigned` label
3. Remove `agent:product-owner` label
4. Add comment: "Issue enhanced. Ready for specialist assignment."
5. Unassign self from issue

**Result:**
- Issue is now open, no labels, no assignee
- Scheduled run (every 15 min) or manual trigger will pick it up
- assign-copilot-to-issue.sh will re-analyze enhanced content
- Match to appropriate specialist agent
- Specialist completes the work

**Implementation:**
```markdown
# In product-owner.md enhancement template:

After enhancing the issue, perform these cleanup steps:

1. Remove labels:
   - `copilot-assigned`
   - `agent:product-owner`

2. Unassign yourself from the issue

3. Add comment:
   "✅ Issue enhanced with structured requirements.
   
   Ready for specialist assignment. The issue will be 
   automatically re-analyzed and assigned to the 
   appropriate specialist agent."
```

### Option B: Add Workflow Trigger for Enhanced Issues

**Workflow change:**
```yaml
on:
  issues:
    types: [opened, labeled]  # Add labeled trigger
```

**Logic:**
- Trigger when label `enhanced-by-po` is added
- Remove `copilot-assigned` label
- Re-run agent matching
- Assign to new specialist

**Pros:**
- More automated
- Clear handoff signal

**Cons:**
- Adds complexity
- Product-owner must remember to add label
- Still needs product-owner to unassign

### Option C: Use GitHub Issue Events API

**Product-owner creates sub-issue:**
1. Product-owner enhances original issue
2. Creates NEW issue with enhanced content
3. Links to original issue
4. New issue gets assigned to specialist
5. Original issue marked as duplicate

**Pros:**
- Clean separation
- Clear audit trail

**Cons:**
- More complex
- Duplicate issues
- Harder to track

## 📋 Recommended Implementation

### Update Product Owner Agent Definition

**File: `.github/agents/product-owner.md`**

Add to the "Workflow" section:

```markdown
## After Enhancement

Once you've enhanced an issue, perform these steps to hand off to a specialist:

1. **Comment on the issue:**
   ```
   ✅ **Issue Enhanced by @product-owner**
   
   I've transformed this issue into a structured format with:
   - User story
   - Acceptance criteria
   - Technical considerations
   - Recommended specialist agent
   
   **Next Steps:**
   I'm removing the assignment labels so the issue can be 
   re-analyzed and assigned to the recommended specialist.
   
   The automated assignment workflow will pick this up within 
   15 minutes, or it can be manually triggered.
   ```

2. **Remove labels:**
   - Remove `copilot-assigned` label
   - Remove `agent:product-owner` label

3. **Unassign yourself:**
   - Unassign @github-copilot from the issue

4. **Result:**
   - Issue is now open, no assignee, no blocking labels
   - Scheduled workflow (runs every 15 min) will detect it
   - Enhanced content will match to appropriate specialist
   - Specialist will implement the well-defined requirements
```

### Update Documentation

**File: `docs/PRODUCT_OWNER_AGENT.md`**

Add section explaining the handoff process:

```markdown
## Product Owner Handoff Process

The product owner agent follows a two-phase workflow:

### Phase 1: Enhancement
1. Receives vague issue
2. Analyzes requirements
3. Enhances with structured format
4. Adds acceptance criteria and recommendations

### Phase 2: Handoff
1. Removes assignment labels:
   - `copilot-assigned`
   - `agent:product-owner`
2. Unassigns self from issue
3. Posts handoff comment
4. Issue becomes available for re-assignment

### Phase 3: Specialist Assignment (Automatic)
1. Scheduled workflow detects unassigned issue (runs every 15 min)
2. Re-analyzes enhanced content
3. Matches to specialist agent (e.g., @accelerate-master)
4. Assigns specialist to complete implementation
```

## ✅ Verification Checklist

For product-owner agent to correctly handle the flow:

- [x] Can read issue content
- [x] Can edit issue body
- [x] Can add comments to issue
- [ ] **NEEDS UPDATE:** Remove `copilot-assigned` label
- [ ] **NEEDS UPDATE:** Remove `agent:product-owner` label  
- [ ] **NEEDS UPDATE:** Unassign self from issue
- [ ] **NEEDS UPDATE:** Add handoff comment

## 📊 Flow After Implementation

```
User creates vague issue: "Make system faster"
  ↓
copilot-graphql-assign.yml triggers
  ↓
Matches to @product-owner (vague language detected)
  ↓
Issue assigned to Copilot with @product-owner directive
  ↓
@product-owner enhances issue:
  - Adds user story
  - Adds acceptance criteria
  - Recommends @accelerate-master
  ↓
@product-owner performs cleanup:
  - Removes copilot-assigned label ✅
  - Removes agent:product-owner label ✅
  - Unassigns self ✅
  - Posts handoff comment ✅
  ↓
Issue now: open, no assignee, no blocking labels
  ↓
Scheduled workflow runs (within 15 min)
  ↓
Matches enhanced content to @accelerate-master
  ↓
Issue assigned to Copilot with @accelerate-master directive
  ↓
@accelerate-master implements performance improvements
  ↓
Creates PR, merges, closes issue
```

## 🎯 Key Points

1. **Product-owner CAN edit issues** ✅
2. **Product-owner CAN add comments** ✅
3. **Product-owner CAN remove labels** ✅ (via gh CLI or API)
4. **Product-owner CAN unassign self** ✅ (via gh CLI or API)
5. **Scheduled workflow WILL pick up unassigned issues** ✅ (every 15 min)
6. **Enhanced content WILL match to specialist** ✅ (better keywords)

## ⚠️ Current Gap

**The product-owner agent definition needs to be updated** to include:
1. Instructions to remove labels after enhancement
2. Instructions to unassign self
3. Handoff comment template
4. Clear workflow for specialist handoff

## 📝 Implementation Plan

1. Update `.github/agents/product-owner.md`:
   - Add "After Enhancement" section
   - Include label removal instructions
   - Include unassign instructions
   - Add handoff comment template

2. Update `docs/PRODUCT_OWNER_AGENT.md`:
   - Document the handoff process
   - Explain the two-phase workflow
   - Show example flow diagram

3. Test the complete flow:
   - Create vague test issue
   - Verify product-owner enhancement
   - Verify label removal
   - Verify unassignment
   - Verify specialist re-assignment
   - Verify specialist completion

## 🔬 Testing Commands

```bash
# Create test issue
gh issue create --title "Make the dashboard better" \
  --body "The dashboard is confusing. Can we improve it?" \
  --label "test"

# Wait for product-owner assignment (automatic)

# After product-owner enhancement, verify:
gh issue view <issue-number> --json labels
# Should NOT have: copilot-assigned, agent:product-owner

gh issue view <issue-number> --json assignees
# Should be empty or not include Copilot

# Wait 15 minutes for scheduled run OR manually trigger:
gh workflow run copilot-graphql-assign.yml

# Verify specialist assignment:
gh issue view <issue-number> --json labels
# Should have: copilot-assigned, agent:accelerate-master (or other specialist)
```

## 🎉 Expected Results

**After full implementation:**
- ✅ Product-owner can enhance vague issues
- ✅ Product-owner can hand off to specialists
- ✅ Specialists receive well-structured requirements
- ✅ No manual intervention needed
- ✅ Complete audit trail maintained
- ✅ All labels in correct state throughout flow
