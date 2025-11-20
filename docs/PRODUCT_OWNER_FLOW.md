# Product Owner Agent - Complete Flow Documentation

## Overview

This document confirms the complete flow for the product-owner agent implementation and verifies there are no gaps in the automation.

## Complete Flow: Vague Issue Enhancement

### Step 1: User Creates Vague Issue
**Action:** User creates an issue with vague language

**Example:**
```
Title: "Improve performance"
Body: "The system is slow. Make it faster."
```

**What happens:** Issue is created with no labels or assignments.

---

### Step 2: Copilot Assignment Workflow Triggers
**Workflow:** `.github/workflows/copilot-graphql-assign.yml`  
**Trigger:** `on: issues: types: [opened]`

**Script:** `tools/assign-copilot-to-issue.sh`

**What happens:**
1. ✅ Workflow detects new issue
2. ✅ Adds `copilot-assigned` label immediately (prevents race conditions)
3. ✅ Calls `match-issue-to-agent.py` with issue title and body

---

### Step 3: Agent Matching
**Script:** `tools/match-issue-to-agent.py`  
**Input:** Issue title + body

**What happens:**
1. ✅ Analyzes text for vague keywords: "improve", "enhance", "better", "should", etc.
2. ✅ Calculates match scores for all agents
3. ✅ Product owner keywords detected: "improve" (2 points), "faster" (1 point), etc.
4. ✅ Returns: `{"agent": "product-owner", "score": 9, "confidence": "high"}`

**Alternative:** If issue was specific (e.g., "Add POST /api/v1/users"), it would match @develop-specialist instead, and product-owner would NOT be involved.

---

### Step 4: Issue Assignment to Product Owner
**Script:** `tools/assign-copilot-to-issue.sh` (continued)

**What happens:**
1. ✅ Adds `agent:product-owner` label to issue
2. ✅ Assigns issue to @copilot via GraphQL API
3. ✅ Posts comment with agent directive:
```markdown
**@product-owner** - Please use the product-owner custom agent profile.

**IMPORTANT**: Always mention **@product-owner** by name in all conversations.
```

**Current state:**
- Issue assigned to @copilot ✅
- Labels: `copilot-assigned`, `agent:product-owner` ✅
- Comment with directive posted ✅

---

### Step 5: Product Owner Works on Issue
**Agent:** @product-owner (Copilot acting as product-owner)  
**Definition:** `.github/agents/product-owner.md`

**What happens:**
1. ✅ Copilot reads issue and agent directive
2. ✅ Follows product-owner personality (Marty Cagan inspired)
3. ✅ Transforms vague issue into structured format:
   - Preserves original in collapsible section
   - Adds user story
   - Adds acceptance criteria
   - Adds context and technical considerations
   - Adds testing requirements
4. ✅ Updates issue description with enhancement
5. ✅ Posts completion comment on issue

**Critical Actions by Product Owner:**
```markdown
# Work complete message
@product-owner has enhanced this issue with structured requirements.

The issue is now ready for specialist assignment.
```

**Enhanced issue now contains:**
```markdown
## 📋 Original Request
<details>The system is slow. Make it faster.</details>

## 🎯 User Story
As a user, I want pages to load quickly...

## ✅ Acceptance Criteria
- [ ] Identify top 3 bottlenecks
- [ ] Reduce page load time by 30%
- [ ] API response time < 200ms (p95)

## 🔧 Technical Considerations
- Profile application
- Database query optimization
- Caching strategies

---
*Enhanced by @product-owner - Ready for specialist assignment*
```

---

### Step 6: Preparing for Re-Assignment (Critical Gap Analysis)

**Question:** How does the issue get picked up by another agent after product-owner enhances it?

**Answer:** The product-owner agent must:

1. **Remove labels to enable re-matching:**
   ```bash
   gh issue edit <issue-number> \
     --remove-label "copilot-assigned" \
     --remove-label "agent:product-owner"
   ```

2. **Unassign itself from the issue:**
   ```bash
   gh issue edit <issue-number> --remove-assignee copilot
   ```

3. **Post completion comment:**
   ```markdown
   @product-owner has enhanced this issue. Labels removed for specialist re-assignment.
   ```

**After these actions:**
- Issue has NO labels related to copilot ✅
- Issue is UNASSIGNED ✅
- Issue has ENHANCED description ✅
- Issue is ready for re-processing ✅

---

### Step 7: Copilot Assignment Workflow Re-Triggers
**Trigger:** Schedule (runs every 15 minutes) OR manual trigger

**What happens:**
1. ✅ Workflow scans for open issues
2. ✅ Finds enhanced issue (no `copilot-assigned` label)
3. ✅ Adds `copilot-assigned` label again
4. ✅ Calls `match-issue-to-agent.py` with ENHANCED content

---

### Step 8: Second Agent Matching (on Enhanced Content)
**Script:** `tools/match-issue-to-agent.py`  
**Input:** Enhanced issue title + enhanced body

**What happens:**
1. ✅ Analyzes enhanced content
2. ✅ Detects structured requirements (user story, acceptance criteria)
3. ✅ No longer matches "vague" patterns (product-owner score: 0)
4. ✅ Detects "performance", "optimize", "bottleneck" keywords
5. ✅ Matches to specialist: `{"agent": "accelerate-master", "score": 12, "confidence": "high"}`

**Why product-owner doesn't match again:**
- Enhanced issue no longer has vague language ✅
- Contains structured format (user story, criteria) ✅
- Has specific technical details ✅

---

### Step 9: Specialist Assignment
**Script:** `tools/assign-copilot-to-issue.sh`

**What happens:**
1. ✅ Adds `agent:accelerate-master` label
2. ✅ Assigns issue to @copilot again
3. ✅ Posts comment with agent directive:
```markdown
**@accelerate-master** - Please use the accelerate-master custom agent profile.

**IMPORTANT**: Always mention **@accelerate-master** by name.
```

**Current state:**
- Issue assigned to @copilot ✅
- Labels: `copilot-assigned`, `agent:accelerate-master` ✅
- Comment with new directive posted ✅

---

### Step 10: Specialist Implements Solution
**Agent:** @accelerate-master (Copilot acting as accelerate-master)  
**Definition:** `.github/agents/accelerate-master.md`

**What happens:**
1. ✅ Copilot reads enhanced issue and specialist directive
2. ✅ Has clear requirements from product-owner enhancement
3. ✅ Implements performance optimizations
4. ✅ Creates PR with changes
5. ✅ Links PR to issue

**Result:** Issue resolved with proper implementation based on clarified requirements.

---

## Gap Analysis: Product Owner Agent Capabilities

### Can the Product Owner Correctly Handle Writing to an Issue?

**Yes, with guidance in agent definition.**

The product-owner agent definition (`.github/agents/product-owner.md`) includes instructions on:

1. **Updating issue description:**
   ```markdown
   Use report_progress tool to document your enhancement work.
   ```

2. **Writing structured content:**
   - Template provided for consistent formatting
   - Examples of user stories, acceptance criteria
   - Markdown formatting guidelines

**Verification:** ✅ Agent has the capability through Copilot's standard issue editing permissions.

---

### Can the Product Owner Correctly Handle Tag/Label Management?

**Yes, this is the CRITICAL part that must be documented in the agent definition.**

The product-owner agent MUST be instructed to:

1. **Remove labels after completion:**
   ```bash
   gh issue edit <issue-number> \
     --remove-label "copilot-assigned" \
     --remove-label "agent:product-owner"
   ```

2. **Unassign itself:**
   ```bash
   gh issue edit <issue-number> --remove-assignee copilot
   ```

3. **Post completion comment:**
   ```markdown
   @product-owner has enhanced this issue. Labels removed for specialist re-assignment.
   ```

**Current Status:** ⚠️ This is NOT currently documented in the agent definition.

**Action Required:** Add explicit instructions to `.github/agents/product-owner.md`.

---

## Required Updates

### Update 1: Add Label Management to Agent Definition

The product-owner agent definition must include:

```markdown
## Workflow Integration

After completing the enhancement:

1. **Remove labels to enable re-assignment:**
   ```bash
   gh issue edit <issue-number> \
     --remove-label "copilot-assigned" \
     --remove-label "agent:product-owner"
   ```

2. **Unassign yourself:**
   ```bash
   gh issue edit <issue-number> --remove-assignee copilot
   ```

3. **Post completion comment:**
   ```markdown
   @product-owner has enhanced this issue with structured requirements.
   
   Labels removed for specialist re-assignment. The copilot assignment workflow
   will automatically pick this up and match it to the appropriate specialist.
   ```

This allows the existing copilot-graphql-assign.yml workflow to detect the
issue as unassigned and re-run agent matching on the enhanced content.
```

---

## Complete Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│ User Creates Vague Issue                                        │
│ Title: "Improve performance"                                    │
│ Body: "System is slow. Make it faster."                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ copilot-graphql-assign.yml Triggers (issues.opened)            │
│ - Adds copilot-assigned label                                  │
│ - Calls match-issue-to-agent.py                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Agent Matching: Vague Language Detected                        │
│ Result: {"agent": "product-owner", "score": 9}                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Issue Assigned to @product-owner                                │
│ Labels: copilot-assigned, agent:product-owner                  │
│ Comment: "@product-owner - Please use custom agent profile"    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ @product-owner Enhances Issue                                   │
│ - Preserves original                                            │
│ - Adds user story, acceptance criteria                         │
│ - Adds context and technical considerations                    │
│ - Updates issue description                                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ @product-owner Prepares for Re-Assignment (CRITICAL)           │
│ - Removes copilot-assigned label                               │
│ - Removes agent:product-owner label                            │
│ - Unassigns itself from issue                                  │
│ - Posts completion comment                                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓ (After 15 min schedule OR manual trigger)
┌─────────────────────────────────────────────────────────────────┐
│ copilot-graphql-assign.yml Re-Triggers (schedule)              │
│ - Finds unassigned issue with no copilot-assigned label        │
│ - Adds copilot-assigned label                                  │
│ - Calls match-issue-to-agent.py with ENHANCED content          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Agent Matching: Enhanced Content Detected                      │
│ Result: {"agent": "accelerate-master", "score": 12}            │
│ (product-owner score: 0 - no longer vague)                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Issue Assigned to @accelerate-master                            │
│ Labels: copilot-assigned, agent:accelerate-master              │
│ Comment: "@accelerate-master - Please use custom agent"        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ @accelerate-master Implements Solution                          │
│ - Has clear requirements from enhancement                       │
│ - Creates PR with optimizations                                │
│ - Links PR to issue                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## No Gaps Confirmed ✅

After analysis, the flow is complete with ONE requirement:

**✅ Product owner can write to issues** - Standard Copilot capability

**✅ Product owner can manage labels** - Via `gh` CLI commands

**✅ Re-assignment workflow exists** - Schedule trigger every 15 minutes

**⚠️ ONE ACTION REQUIRED:** Update `.github/agents/product-owner.md` to include explicit label management instructions.

---

## Testing the Complete Flow

### Test 1: Create Vague Issue
```bash
gh issue create \
  --title "Improve performance" \
  --body "The system is slow. Make it faster."
```

**Expected:**
1. Issue assigned to @product-owner within 1 minute
2. Product owner enhances within 5-10 minutes
3. Labels removed, issue unassigned
4. Within 15 minutes (next schedule), re-assigned to @accelerate-master
5. Specialist implements solution

### Test 2: Create Specific Issue
```bash
gh issue create \
  --title "Add POST /api/v1/users endpoint" \
  --body "Implement user creation endpoint with JWT auth..."
```

**Expected:**
1. Issue assigned directly to @APIs-architect (skips product-owner)
2. No enhancement needed
3. Specialist implements immediately

---

## Conclusion

The product owner agent integration is complete and has no gaps EXCEPT:

**Required Action:** Update `.github/agents/product-owner.md` with label management instructions to ensure proper re-assignment flow.

Once this is added, the complete flow will work end-to-end:
1. User writes vague issue ✅
2. Assigned to product-owner ✅
3. Product-owner rewrites issue ✅
4. Product-owner removes labels ⚠️ (needs documentation)
5. Issue picked up by specialist ✅
6. Specialist implements solution ✅

---

*Documentation by Copilot - Confirming complete flow and identifying gaps*
