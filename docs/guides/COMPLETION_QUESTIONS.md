# ✅ 8 Mandatory Completion Questions

> **The audit framework that ensures autonomous loop completeness**

Every workflow in the Chained autonomous system MUST be able to answer these 8 questions. Work is incomplete if any answer is missing.

---

## 🎯 Purpose

The 8 Mandatory Completion Questions serve as:

1. **Quality Gate**: Ensures workflows actually complete their stage
2. **Audit Trail**: Provides transparency and accountability
3. **Debug Aid**: Makes troubleshooting easier
4. **Documentation**: Self-documents workflow outcomes
5. **Loop Integrity**: Validates the autonomous loop is closed

---

## 📋 The Questions

### 1. Where is the learning artifact?

**What**: Location of the learning/input data

**Examples**:
- `learnings/tldr_20241115_083000.json`
- `learnings/hackernews_trending_20241115.json`
- `analysis/combined_20241115.md`
- `investigation-reports/security-audit-123.md`

**Valid Responses**:
```markdown
✅ **Learning artifact**: learnings/tldr_20241115.json (15 items)
✅ **Learning artifact**: analysis/combined_learning_20241115.md
⏭️ **Learning artifact**: Not applicable (world model update stage)
```

**Invalid Responses**:
```markdown
❌ "Some learnings were added"
❌ "In the learnings folder"
❌ No answer provided
```

---

### 2. Where is the world model update?

**What**: Location of world state changes

**Examples**:
- `world/world_state.json` (tick updated)
- `world/knowledge.json` (graph updated)
- `world/agents/{agent-id}/state.json`
- `.github/agent-system/registry.json`

**Valid Responses**:
```markdown
✅ **World model update**: world/world_state.json (tick 1234 → 1235)
✅ **World model update**: world/knowledge.json (3 new connections)
⏭️ **World model update**: Will be updated in next stage
N/A **World model update**: Not applicable for this workflow
```

**Invalid Responses**:
```markdown
❌ "The world was updated"
❌ "Model sync completed"
❌ No answer provided
```

---

### 3. Which agents are reacting?

**What**: Agent IDs with @mentions

**Examples**:
- Single: `@engineer-master`
- Multiple: `@secure-specialist, @troubleshoot-expert`
- List format:
  ```markdown
  - @accelerate-master
  - @assert-specialist
  - @organize-guru
  ```

**Valid Responses**:
```markdown
✅ **Agents reacting**: @engineer-master, @create-botter (2 agents)
✅ **Agents reacting**: None (learning ingestion stage)
⏭️ **Agents reacting**: Will be determined in assignment stage
```

**Invalid Responses**:
```markdown
❌ "Some agents"
❌ "engineer-master and create-botter" (missing @)
❌ "3 agents selected" (no names)
```

---

### 4. Are no more than 10 agents assigned?

**What**: Validation of agent capacity limit

**Format**: `X/10 agents` or validation output

**Valid Responses**:
```markdown
✅ **Agent capacity**: 7/10 agents assigned
✅ **Agent capacity**: 10/10 agents (at capacity)
✅ **Agent capacity**: Validated with tools/validate_agent_capacity.py
⏭️ **Agent capacity**: Will be validated in assignment stage
N/A **Agent capacity**: No agents needed for this task
```

**Invalid Responses**:
```markdown
❌ "Within limits"
❌ "12 agents" (exceeds limit!)
❌ "Yes" (no number)
```

---

### 5. How do agents move in the world model?

**What**: Agent navigation and location updates

**Examples**:
- Path updates in `world/world_state.json`
- Location changes logged
- Navigation script output
- Movement history

**Valid Responses**:
```markdown
✅ **Agent movement**: 
  - @engineer-master: Seattle → San Francisco
  - @secure-specialist: Berlin → London
  - Updated in world/world_state.json
  
✅ **Agent movement**: Logged by agent_navigator.py (3 agents moved)
⏭️ **Agent movement**: Will be updated when agents start work
N/A **Agent movement**: Static for this workflow
```

**Invalid Responses**:
```markdown
❌ "Agents moved"
❌ "Navigation complete"
❌ No paths or locations specified
```

---

### 6. What mission issue is being created?

**What**: Issue URL, number, and title

**Format**: Include URL and title

**Valid Responses**:
```markdown
✅ **Mission issue**: #456 - "Learning Task: API Design for @engineer-master"
   https://github.com/enufacas/Chained/issues/456

✅ **Mission issue**: Multiple issues created:
   - #457 - "Security Audit (@secure-specialist)"
   - #458 - "Performance Review (@accelerate-master)"

⏭️ **Mission issue**: Will be created in assignment stage
N/A **Mission issue**: Informational PR only
```

**Invalid Responses**:
```markdown
❌ "Issue created"
❌ "Issue #456" (no title or URL)
❌ "See the new issue" (no reference)
```

---

### 7. Were all labels created before use?

**What**: Confirmation of label management

**Verification**: Check workflow logs for label creation

**Valid Responses**:
```markdown
✅ **Labels created**: Verified in "Ensure labels exist" step
✅ **Labels created**: 
   - learning ✓
   - agent:engineer-master ✓
   - automated ✓

✅ **Labels created**: Using tools/create_labels.py
```

**Invalid Responses**:
```markdown
❌ "Labels added" (not created)
❌ "Should be there" (not verified)
❌ No verification mentioned
```

---

### 8. Which workflow continues the loop?

**What**: Next workflow in the chain

**Format**: Workflow name and trigger type

**Valid Responses**:
```markdown
✅ **Next workflow**: "Combined Learning Analysis" (workflow_run trigger)
✅ **Next workflow**: "Agent Assignment" will run after PR merge
✅ **Next workflow**: Loop completes, feeds back to "Learning Ingestion"
N/A **Next workflow**: Terminal stage (no continuation)
```

**Invalid Responses**:
```markdown
❌ "Next stage"
❌ "Another workflow"
❌ No workflow name specified
```

---

## 🎨 Complete Example

### In a Pull Request Body

```markdown
## 📚 Learning Ingestion: TLDR Tech

### Summary

Ingested 15 tech news items from TLDR Tech newsletter.

### Autonomous Loop Stage

This is **Stage 1: Learning Ingestion** of the autonomous loop.

### Completion Questions

1. ✅ **Learning artifact**: `learnings/tldr_20241115_083000.json` (15 items)
2. ⏭️ **World model update**: Will be updated in next stage
3. ⏭️ **Agents reacting**: Will be determined in assignment stage
4. ⏭️ **Agent capacity**: Will be validated in assignment stage
5. ⏭️ **Agent movement**: Will be updated when agents are assigned
6. ⏭️ **Mission issue**: Will be created by assignment workflow
7. ✅ **Labels created**: Verified in workflow (learning, learning-source-tldr, automated)
8. ✅ **Next workflow**: "Combined Learning Analysis" (workflow_run trigger)

---

*Automated by TLDR learning ingestion workflow*
```

### In a World Model Update PR

```markdown
## 🌍 World Model Update - Tick 1234

### Summary

Updated world state based on latest learnings and agent activities.

### Autonomous Loop Stage

This is **Stage 3: World Model Update** of the autonomous loop.

### Completion Questions

1. ✅ **Learning artifact**: Processed from previous stage (15 TLDR items)
2. ✅ **World model update**: 
   - world/world_state.json (tick 1233 → 1234)
   - world/knowledge.json (5 new connections)
   - 12 agents synced, 8 ideas added
3. ⏭️ **Agents reacting**: Will be determined in next stage
4. ⏭️ **Agent capacity**: Will be validated in assignment workflow
5. ✅ **Agent movement**: 3 agents navigated (logged in world_state.json)
   - @engineer-master: Seattle → San Francisco
   - @secure-specialist: Berlin → London  
   - @accelerate-master: Austin → Seattle
6. ⏭️ **Mission issue**: Will be created by assignment workflow
7. ✅ **Labels created**: Verified (world-model, automated)
8. ✅ **Next workflow**: "Agent Assignment" (workflow_run trigger)

---

*Automated by world model update workflow*
```

### In an Agent Assignment Issue

```markdown
## 🎯 Agent Assignment Complete

### Summary

Assigned 8 agents to learning-driven implementation tasks.

### Autonomous Loop Stage

This is **Stage 4: Agent Assignment** of the autonomous loop.

### Completion Questions

1. ✅ **Learning artifact**: learnings/combined_analysis_20241115.md
2. ✅ **World model update**: Agent states updated in world/world_state.json
3. ✅ **Agents reacting**: 8 agents assigned:
   - @engineer-master (#456)
   - @secure-specialist (#457)
   - @accelerate-master (#458)
   - @organize-guru (#459)
   - @document-ninja (#460)
   - @assert-specialist (#461)
   - @troubleshoot-expert (#462)
   - @create-botter (#463)
4. ✅ **Agent capacity**: 8/10 agents (validated with tools/validate_agent_capacity.py)
5. ✅ **Agent movement**: Agents will move to idea locations when starting work
6. ✅ **Mission issues**: Created 8 issues (#456-#463)
7. ✅ **Labels created**: Verified (agent-mission, learning-assignment, agent:* for each)
8. ✅ **Next workflow**: Agents will execute via Copilot on issues

---

*Automated by agent assignment workflow*
```

---

## 🛠️ Workflow Template with Questions

```yaml
- name: Create PR with completion questions
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh pr create \
      --title "Title" \
      --body "## Description

    ### Autonomous Loop Stage
    
    This is **Stage X: Stage Name** of the autonomous loop.

    ### Completion Questions

    1. ✅ **Learning artifact**: ${{ steps.fetch.outputs.filename }}
    2. ✅ **World model update**: world/world_state.json (tick updated)
    3. ✅ **Agents reacting**: @${{ steps.assign.outputs.agents }}
    4. ✅ **Agent capacity**: ${{ steps.validate.outputs.count }}/10 agents
    5. ✅ **Agent movement**: Updated in world model
    6. ✅ **Mission issue**: #${{ steps.create.outputs.issue_number }}
    7. ✅ **Labels created**: Verified in previous step
    8. ✅ **Next workflow**: Next Stage Name (workflow_run trigger)

    ---

    *Automated by workflow-name*" \
      --label "automated" \
      --base main \
      --head "$BRANCH_NAME"
```

---

## 📊 Validation Checklist

When reviewing a PR or issue, verify:

- [ ] All 8 questions are present
- [ ] Each question has a specific answer (not "TBD" or "N/A" unless justified)
- [ ] File paths are absolute and valid
- [ ] Agent names use @mention syntax
- [ ] URLs are complete and accessible
- [ ] Numbers are specific (not "some" or "many")
- [ ] Next workflow is clearly identified

---

## 🚨 Common Mistakes

### Mistake 1: Vague Answers

❌ **Bad**:
```markdown
1. **Learning artifact**: Added some learnings
```

✅ **Good**:
```markdown
1. ✅ **Learning artifact**: learnings/tldr_20241115.json (15 items)
```

### Mistake 2: Missing @mentions

❌ **Bad**:
```markdown
3. **Agents reacting**: engineer-master and secure-specialist
```

✅ **Good**:
```markdown
3. ✅ **Agents reacting**: @engineer-master, @secure-specialist (2 agents)
```

### Mistake 3: No Validation

❌ **Bad**:
```markdown
4. **Agent capacity**: Within limit
```

✅ **Good**:
```markdown
4. ✅ **Agent capacity**: 7/10 agents (validated with tools/validate_agent_capacity.py)
```

### Mistake 4: No URL

❌ **Bad**:
```markdown
6. **Mission issue**: Issue #456
```

✅ **Good**:
```markdown
6. ✅ **Mission issue**: #456 - "Learning Task for @engineer-master"
   https://github.com/enufacas/Chained/issues/456
```

---

## 🎓 Why These Questions Matter

### Question 1: Learning Artifact
**Ensures**: Work is traceable to input data

### Question 2: World Model Update
**Ensures**: State changes are recorded

### Question 3: Agents Reacting
**Ensures**: Clear agent accountability

### Question 4: Agent Capacity
**Ensures**: System scalability limits are enforced

### Question 5: Agent Movement
**Ensures**: Geographic/logical navigation is tracked

### Question 6: Mission Issue
**Ensures**: Work is assigned and trackable

### Question 7: Labels Created
**Ensures**: Workflows don't fail on missing labels

### Question 8: Next Workflow
**Ensures**: Loop continuity and proper chaining

---

## 🧪 Testing Your Answers

### Manual Review

1. Read each answer
2. Click any links (should work)
3. Check file paths (should exist)
4. Verify @mentions (should be valid agents)
5. Confirm numbers (should be specific)

### Automated Validation

```python
#!/usr/bin/env python3
"""Validate completion questions in PR/issue body"""

import re
import sys

def validate_completion_questions(body: str) -> dict:
    """Validate all 8 questions are answered"""
    
    results = {}
    questions = [
        "Learning artifact",
        "World model update",
        "Agents reacting",
        "Agent capacity",
        "Agent movement",
        "Mission issue",
        "Labels created",
        "Next workflow"
    ]
    
    for i, question in enumerate(questions, 1):
        # Look for the question pattern
        pattern = rf"{i}\.\s+[✅⏭️N/A]\s+\*\*{re.escape(question)}\*\*:\s+(.+)"
        match = re.search(pattern, body)
        
        if match:
            answer = match.group(1).strip()
            # Check if answer is substantial
            if len(answer) > 10 and not answer.startswith("TBD"):
                results[question] = "✅ PASS"
            else:
                results[question] = f"⚠️  WEAK: {answer}"
        else:
            results[question] = "❌ MISSING"
    
    return results

# Usage
if __name__ == "__main__":
    import subprocess
    
    # Get PR body
    result = subprocess.run(
        ['gh', 'pr', 'view', '--json', 'body', '-q', '.body'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Failed to fetch PR body")
        sys.exit(1)
    
    body = result.stdout
    results = validate_completion_questions(body)
    
    print("🔍 Completion Questions Validation")
    print("=" * 60)
    
    for question, status in results.items():
        print(f"{status} - {question}")
    
    # Check if all passed
    failed = sum(1 for s in results.values() if "❌" in s or "⚠️" in s)
    
    print("=" * 60)
    if failed == 0:
        print("✅ All questions validated!")
        sys.exit(0)
    else:
        print(f"❌ {failed} questions need attention")
        sys.exit(1)
```

---

## 📚 Related Documentation

- [Autonomous System Architecture](./AUTONOMOUS_SYSTEM_ARCHITECTURE.md)
- [Autonomous Loop Implementation](./AUTONOMOUS_LOOP_IMPLEMENTATION.md)
- [Workflow Validation Guide](./WORKFLOW_VALIDATION_GUIDE.md)

---

**Every workflow MUST answer all 8 questions. This is non-negotiable for autonomous loop integrity.**

*✅ Documented by **@support-master** - ensuring completeness and accountability!*
