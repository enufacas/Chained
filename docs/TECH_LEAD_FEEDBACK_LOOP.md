# Tech Lead Feedback Loop

## Overview

The **Tech Lead Feedback Loop** automates the process of taking tech lead review comments and converting them into actionable work items for specialized agents. This creates a seamless review cycle where tech leads provide expert feedback, and agents automatically address that feedback.

## The Problem It Solves

**Before this system:**
- Tech leads review PRs and request changes
- PR author has to manually understand and implement fixes
- No automated tracking of feedback → fix → re-review cycle
- Feedback can sit unaddressed for extended periods

**With this system:**
- Tech lead requests changes on a PR
- System automatically creates a follow-up issue
- Issue is assigned to the most appropriate specialized agent
- Agent addresses feedback and updates the PR
- Tech lead is notified for re-review
- Cycle repeats until approval ✅

## Complete Workflow

### Stage 1: Initial PR Review

```
PR Created → tech-lead-review.yml analyzes → Assigns tech lead → Labels applied
```

**Key Actions:**
1. PR is opened or updated
2. `tech-lead-review.yml` workflow triggers
3. System analyzes PR complexity and file paths
4. Appropriate tech lead is assigned
5. Labels added: `needs-tech-lead-review`, `tech-lead:<name>`

### Stage 2: Tech Lead Reviews

```
Tech Lead Reviews PR → Approves OR Requests Changes
```

**Approval Path:**
- Tech lead approves the PR
- `tech-lead-approved` label added
- `needs-tech-lead-review` label removed
- Auto-review-merge can proceed ✅

**Changes Requested Path:**
- Tech lead requests changes
- `tech-lead-changes-requested` label added
- **Feedback handler activates** 🔄

### Stage 3: Feedback Processing (NEW!)

```
Changes Requested → tech-lead-feedback-handler.yml triggers → Creates issue for agent
```

**Automated by `tech-lead-feedback-handler.yml`:**

1. **Detect feedback**
   - Workflow monitors `pull_request_review` events
   - Triggers when review state is `changes_requested`
   - Extracts review body and comments

2. **Analyze feedback**
   - Parses review comments for actionable items
   - Checks for task lists, numbered items, specific requests
   - Determines if automated fix is appropriate

3. **Match to agent**
   - Uses `match-issue-to-agent.py` to find best agent
   - Considers PR content + review feedback
   - Selects agent based on expertise needed

4. **Create follow-up issue**
   - Generates detailed issue with:
     - Full review feedback
     - Link to original PR
     - Step-by-step instructions for agent
     - Expected workflow commands
   - Assigns to appropriate agent
   - Labels: `tech-lead-feedback`, `agent:<name>`, `linked-to-pr`

5. **Link back to PR**
   - Comments on PR with follow-up issue link
   - Notifies tech lead that agent will address feedback
   - Updates PR labels to track state

### Stage 4: Agent Fixes

```
Agent assigned → Checks out PR branch → Makes fixes → Updates PR → Notifies tech lead
```

**Agent Workflow:**

1. **Receive assignment**
   - Agent is assigned via issue created by feedback handler
   - Issue contains all context needed

2. **Review feedback**
   - Reads tech lead's review comments
   - Understands what needs to be changed
   - Plans fixes according to agent's specialization

3. **Checkout PR branch**
   ```bash
   gh pr checkout <pr_number>
   ```

4. **Make fixes**
   - Implements changes per tech lead feedback
   - Follows agent's specialized approach
   - Ensures changes align with review requests

5. **Commit and push**
   ```bash
   git add .
   git commit -m "fix: address @tech-lead feedback - <description>"
   git push
   ```

6. **Notify stakeholders**
   - Comment on PR: "Addressed your feedback, ready for re-review"
   - Comment on follow-up issue: "Completed fixes"
   - System auto-updates labels

### Stage 5: Re-Review Cycle

```
PR updated → tech-lead-review.yml re-triggers → Tech lead notified → Reviews again
```

**Re-review Process:**

1. **PR update detected**
   - Push to PR branch triggers `tech-lead-review.yml`
   - System detects that tech lead review is in progress
   - Removes `tech-lead-changes-requested` label
   - Keeps `needs-tech-lead-review` label

2. **Tech lead notified**
   - Automatic notification of PR update
   - Tech lead sees agent's comment
   - Review feedback has been addressed

3. **Tech lead reviews again**
   - Approves → `tech-lead-approved` label → merge proceeds ✅
   - Still has concerns → requests changes again → cycle repeats 🔄

### Complete Cycle Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        PR CREATED/UPDATED                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              tech-lead-review.yml ANALYZES PR                    │
│  • Checks file paths                                             │
│  • Analyzes complexity                                           │
│  • Assigns tech lead                                             │
│  • Applies labels: needs-tech-lead-review, tech-lead:<name>     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  TECH LEAD REVIEWS PR                            │
└───────────┬───────────────────────────────────┬─────────────────┘
            │                                   │
         APPROVE                          REQUEST CHANGES
            │                                   │
            ▼                                   ▼
┌───────────────────────────┐   ┌──────────────────────────────────┐
│ tech-lead-approved label  │   │ tech-lead-changes-requested label│
│ needs-* label removed     │   │ tech-lead-feedback-handler.yml   │
│ Auto-merge can proceed ✅ │   │         TRIGGERS                 │
└───────────────────────────┘   └──────────┬───────────────────────┘
                                           │
                                           ▼
                        ┌──────────────────────────────────────────┐
                        │  FEEDBACK HANDLER PROCESSES REVIEW       │
                        │  • Extracts review comments              │
                        │  • Analyzes for actionable items         │
                        │  • Matches to appropriate agent          │
                        │  • Creates follow-up issue               │
                        │  • Links issue to PR                     │
                        └──────────┬───────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────────────────────────┐
                        │   AGENT RECEIVES ASSIGNMENT              │
                        │  • Issue created with full context       │
                        │  • Agent: agent:X label applied          │
                        │  • Copilot auto-assigned                 │
                        └──────────┬───────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────────────────────────┐
                        │     AGENT ADDRESSES FEEDBACK             │
                        │  • Checks out PR branch                  │
                        │  • Makes fixes per tech lead comments    │
                        │  • Commits and pushes to PR              │
                        │  • Comments on PR and issue              │
                        └──────────┬───────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────────────────────────┐
                        │    PR UPDATED WITH FIXES                 │
                        │  • tech-lead-review.yml re-triggers      │
                        │  • Labels updated                        │
                        │  • Tech lead notified                    │
                        └──────────┬───────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────────────────────────┐
                        │       TECH LEAD RE-REVIEWS               │
                        │  Approve → merge ✅                      │
                        │  Still needs work → cycle repeats 🔄     │
                        └──────────────────────────────────────────┘
```

## Workflow Files

### 1. `tech-lead-review.yml`
**Purpose:** Initial analysis and tech lead assignment

**Triggers:**
- PR opened, synchronized, reopened
- Manual workflow dispatch

**Responsibilities:**
- Analyze PR complexity
- Assign appropriate tech lead(s)
- Apply initial labels
- Post analysis comment

### 2. `tech-lead-feedback-handler.yml` (NEW)
**Purpose:** Convert tech lead feedback into agent work items

**Triggers:**
- `pull_request_review` with `changes_requested`
- `pull_request_review_comment` created
- `issue_comment` on PRs
- Manual workflow dispatch

**Responsibilities:**
- Extract review feedback
- Analyze for actionable items
- Match to appropriate agent
- Create follow-up issue
- Link issue to PR
- Update PR labels
- Notify stakeholders

### 3. `auto-review-merge.yml`
**Purpose:** Enforce tech lead approval before merge

**Responsibilities:**
- Check for `needs-tech-lead-review` label
- Block merge if `tech-lead-changes-requested` present
- Allow merge when `tech-lead-approved`
- Post explanatory comments

## Labels Used

| Label | Applied By | Purpose | Blocks Merge |
|-------|-----------|---------|--------------|
| `needs-tech-lead-review` | tech-lead-review.yml | Tech lead review required | ✅ Yes |
| `tech-lead-approved` | Manual/tech-lead-review.yml | Tech lead approved | ❌ No (enables merge) |
| `tech-lead-changes-requested` | tech-lead-feedback-handler.yml | Changes needed | ✅ Yes |
| `tech-lead-review-cycle` | tech-lead-review.yml | In review iteration | ℹ️ Info |
| `tech-lead:<name>` | tech-lead-review.yml | Identifies tech lead | ℹ️ Info |
| `tech-lead-feedback` | tech-lead-feedback-handler.yml | Follow-up issue | ℹ️ Info |
| `agent:<name>` | tech-lead-feedback-handler.yml | Agent assignment | ℹ️ Info |
| `linked-to-pr` | tech-lead-feedback-handler.yml | Issue linked to PR | ℹ️ Info |

## Agent Matching Logic

The feedback handler uses `match-issue-to-agent.py` to determine which agent should fix the issues:

### Matching Process

1. **Combine PR context + feedback**
   - PR title and files changed
   - Tech lead review comments
   - Specific change requests

2. **Score agents based on:**
   - Keyword matches in feedback
   - File paths in PR
   - Agent specializations
   - Complexity factors

3. **Select best agent**
   - Highest scoring agent selected
   - Fallback to `create-guru` if unclear
   - Agent assigned via issue creation

### Example Matching

**Scenario:** Tech lead requests changes to workflow file

```yaml
PR: Modifies .github/workflows/deploy.yml
Feedback: "Please add error handling and improve comments"

Match Result:
- workflows-tech-lead: score 15 (workflow expert)
- document-ninja: score 8 (comments mention)
- → Selected: workflows-tech-lead ✅
```

## Integration Points

### With Existing Systems

1. **Issue Assignment System**
   - Follow-up issues use same assignment mechanism
   - `assign-copilot-to-issue.sh` handles Copilot assignment
   - Agent labels applied for proper routing

2. **Auto-Review-Merge**
   - Feedback handler updates labels
   - Auto-merge respects `tech-lead-changes-requested`
   - Merge blocked until fixes applied

3. **Agent System**
   - Agents work normally on follow-up issues
   - Full context provided in issue body
   - Agent specialization guides fixes

### Data Flow

```
Tech Lead Review → Feedback Handler → Issue Creation → Agent Assignment → Agent Work → PR Update → Re-Review
```

**Key Data:**
- PR number and metadata
- Review comments and state
- Matched agent and confidence
- Issue links and references

## Example Scenario

### Real-World Example

**PR #1234:** "Add new authentication workflow"
- **Files Changed:** `.github/workflows/auth.yml`, `tools/auth-helper.sh`
- **Complexity:** High (security-sensitive)

**Stage 1: Initial Review**
```
1. tech-lead-review.yml triggers
2. Analyzes PR: workflow file + security keywords
3. Assigns: @workflows-tech-lead
4. Labels: needs-tech-lead-review, tech-lead:workflows-tech-lead
```

**Stage 2: Tech Lead Review**
```
@workflows-tech-lead reviews:
"Changes requested:
- [ ] Add input validation for auth tokens
- [ ] Include timeout handling
- [ ] Add comprehensive error messages
- [ ] Update documentation for new workflow"
```

**Stage 3: Feedback Processing**
```
1. tech-lead-feedback-handler.yml triggers
2. Extracts 4 action items
3. Matches to agent:
   - Keywords: "validation", "error", "workflow", "documentation"
   - File paths: workflows, tools
   - Result: @workflows-tech-lead (same agent for consistency)
4. Creates issue #1235: "[Tech Lead Feedback] Address review comments for PR #1234"
5. Assigns @workflows-tech-lead to issue #1235
6. Comments on PR #1234 with issue link
7. Adds label: tech-lead-changes-requested
```

**Stage 4: Agent Fixes**
```
@workflows-tech-lead (via Copilot):
1. Receives issue #1235 assignment
2. Reviews feedback requirements
3. Checks out PR #1234 branch
4. Implements all 4 changes:
   - Adds input validation
   - Adds timeout handling
   - Improves error messages
   - Updates documentation
5. Commits: "fix: address @workflows-tech-lead feedback on auth workflow"
6. Pushes to PR #1234
7. Comments on PR: "Addressed all feedback points. Ready for re-review."
8. Comments on issue #1235: "✅ Completed all fixes for PR #1234"
```

**Stage 5: Re-Review**
```
1. PR #1234 updated → tech-lead-review.yml re-triggers
2. Removes tech-lead-changes-requested label
3. @workflows-tech-lead notified of update
4. Reviews fixes
5. Approves: "LGTM! ✅"
6. tech-lead-approved label added
7. Auto-review-merge proceeds
8. PR #1234 merged ✅
9. Issue #1235 auto-closed (linked to merged PR)
```

## Benefits

### 1. Automated Workflow
- No manual tracking of feedback
- Automatic agent assignment
- Self-documenting process

### 2. Clear Accountability
- Tech lead provides expert review
- Specific agent assigned to fix
- Traceable via issues and labels

### 3. Consistent Quality
- Expert review on critical changes
- Specialized agents make fixes
- Iterative improvement cycle

### 4. Transparent Communication
- All feedback visible in issues
- PR comments link everything
- Labels show current state

### 5. Preserves Autonomy
- Agents work independently
- Automated assignment and tracking
- Human oversight where needed

## Configuration

### Thresholds for Review Requirements

In `match-pr-to-tech-lead.py`:

```python
# Complexity thresholds
COMPLEXITY_THRESHOLDS = {
    'file_count': 5,        # >5 files = complex
    'total_changes': 100,   # >100 lines = complex
}
```

### Protected Paths (Always Require Review)

```python
PROTECTED_PATHS = [
    '.github/workflows/**',
    '.github/agents/**',
    'tools/**/*.sh',
]
```

### Sensitive Keywords (Trigger Review)

```python
SENSITIVE_KEYWORDS = [
    'password', 'secret', 'token', 'auth',
    'credential', 'private', 'key'
]
```

## Monitoring and Metrics

### Queries for Dashboard

**Active Tech Lead Reviews:**
```
is:pr is:open label:"needs-tech-lead-review"
```

**Changes Requested:**
```
is:pr is:open label:"tech-lead-changes-requested"
```

**Tech Lead Feedback Issues:**
```
is:issue is:open label:"tech-lead-feedback"
```

**Review Cycle Time:**
- Time from `changes_requested` to fixes pushed
- Time from fixes to re-review
- Total cycle time to approval

### Success Metrics

1. **Feedback Response Time**
   - How quickly agents address feedback
   - Target: < 24 hours

2. **Re-Review Rate**
   - How many re-reviews needed per PR
   - Target: < 2 on average

3. **Approval Rate**
   - % of PRs approved on re-review
   - Target: > 80%

4. **Feedback Issue Closure**
   - % of feedback issues completed
   - Target: > 95%

## Troubleshooting

### Issue: WIP PR getting reviewed

**Symptoms:** PR has WIP marker but tech lead review still triggered

**Causes:**
- WIP marker not in recognized format
- PR converted from draft but title not updated
- Manual workflow dispatch

**Solutions:**
- Use standard WIP markers: `[WIP]`, `WIP:`, `[do not merge]`, `[dnm]`
- Update title when converting from draft
- Remove all WIP markers before requesting review

### Issue: Feedback not detected

**Symptoms:** Review submitted but no follow-up issue created

**Causes:**
- Review state not `changes_requested`
- Review body empty
- No tech lead label on PR

**Solutions:**
- Ensure tech lead uses "Request Changes" review type
- Include detailed feedback in review body
- Verify tech lead label present on PR

### Issue: Wrong agent assigned

**Symptoms:** Agent doesn't have expertise for the fix

**Causes:**
- Unclear feedback keywords
- Ambiguous PR content
- Scoring too low/high

**Solutions:**
- Improve feedback specificity
- Manually re-assign in follow-up issue
- Adjust matching patterns in `match-issue-to-agent.py`

### Issue: Agent doesn't address feedback

**Symptoms:** Follow-up issue created but no work done

**Causes:**
- Agent not receiving notification
- Issue not clear enough
- Instructions ambiguous

**Solutions:**
- Verify Copilot is assigned
- Check issue has proper labels
- Manually trigger via issue comment
- Ensure issue body has all context

### Issue: Re-review not triggered

**Symptoms:** Fixes pushed but tech lead not notified

**Causes:**
- PR labels not updated
- tech-lead-review.yml not triggered
- Notifications disabled

**Solutions:**
- Manually remove `tech-lead-changes-requested` label
- Re-run tech-lead-review.yml via workflow_dispatch
- Check workflow permissions
- Verify tech lead notification settings

## Future Enhancements

### Planned Improvements

1. **Smart notification timing**
   - Only notify tech lead when all action items addressed
   - Batch notifications for multiple fixes

2. **Feedback categorization**
   - Separate "must fix" from "nice to have"
   - Priority-based agent assignment

3. **Multi-agent coordination**
   - Split feedback across multiple agents
   - Coordinate fixes for complex changes

4. **Metrics dashboard**
   - Visualize review cycle times
   - Track agent fix success rates
   - Show tech lead workload

5. **Learning system**
   - Learn from feedback patterns
   - Improve agent matching over time
   - Suggest preventive measures

### Extension Points

- Custom feedback parsers for specific review styles
- Integration with external review tools
- Slack/Discord notifications
- Weekly digest of tech lead activity
- Automated quality metrics on fixes

## Related Documentation

- [Tech Lead Review Cycle](TECH_LEAD_REVIEW_CYCLE.md) - Overall system
- [Tech Lead Labels](TECH_LEAD_LABELS.md) - Label reference
- [Tech Lead Flow Diagrams](TECH_LEAD_REVIEW_FLOW_DIAGRAMS.md) - Visual flows
- [Agent System](../AGENT_QUICKSTART.md) - Agent profiles and matching

---

*🤖 Documentation for the automated Tech Lead Feedback Loop*
*Enabling seamless expert review + agent fixes cycle*
