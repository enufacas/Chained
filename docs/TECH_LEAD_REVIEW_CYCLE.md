# Tech Lead Review Cycle System

**Implemented by @workflows-tech-lead**

## Overview

The Tech Lead Review Cycle system ensures that critical code changes receive expert review before being merged. This system integrates with the existing auto-review-merge workflow while adding a quality gate for sensitive changes.

## System Architecture

### Components

1. **Tech Lead Review Workflow** (`.github/workflows/tech-lead-review.yml`)
   - Analyzes PRs to determine if Tech Lead review is needed
   - Assigns appropriate Tech Lead reviewers
   - Manages review state labels
   - Handles the review iteration cycle

2. **Tech Lead Feedback Handler** (`.github/workflows/tech-lead-feedback-handler.yml`) **NEW!**
   - Automatically converts tech lead review comments into agent work items
   - Matches feedback to appropriate specialized agents
   - Creates follow-up issues for agents to address feedback
   - Links issues back to PRs for tracking
   - Completes the automated review → fix → re-review cycle

3. **Auto-Review-Merge Integration** (`.github/workflows/auto-review-merge.yml`)
   - Checks Tech Lead review status before merging
   - Blocks merge if review is pending or changes requested
   - Allows merge once Tech Lead approval is given

4. **PR Matching Tool** (`tools/match-pr-to-tech-lead.py`)
   - Analyzes PR file changes
   - Matches files to Tech Lead responsibilities
   - Evaluates complexity and sensitivity

## Label System

The review cycle uses these labels to manage state:

| Label | Purpose | Blocks Merge | Applied By |
|-------|---------|--------------|------------|
| `needs-tech-lead-review` | Review required by Tech Lead | ✅ Yes | Workflow (auto) |
| `tech-lead-approved` | Tech Lead has approved | ❌ No | Workflow (on approval) |
| `tech-lead-changes-requested` | Tech Lead wants changes | ✅ Yes | Workflow (on changes) |
| `tech-lead-review-cycle` | In review iteration | ℹ️ Info only | Workflow (auto) |
| `tech-lead:<name>` | Identifies which Tech Lead | ℹ️ Info only | Workflow (auto) |

## Review Flow

### Standard Flow (PR Requires Tech Lead Review)

```
1. PR Created/Updated
   ↓
2. tech-lead-review.yml analyzes PR
   ↓
3. Matches to Tech Lead(s) based on file paths
   ↓
4. Adds labels:
   - tech-lead:<name>
   - needs-tech-lead-review
   - tech-lead-review-cycle
   ↓
5. Tech Lead receives notification
   ↓
6. Tech Lead reviews PR
   
   ↓ (Path A: Approval)              ↓ (Path B: Changes Requested)
   
7a. Tech Lead approves              7b. Tech Lead requests changes
    ↓                                    ↓
8a. Labels updated:                 8b. tech-lead-feedback-handler.yml triggers **NEW!**
    - Remove: needs-tech-lead-review    ↓
    - Add: tech-lead-approved       8c. Feedback Handler:
    ↓                                    - Extracts review comments
9a. auto-review-merge proceeds          - Matches to appropriate agent
    ↓                                    - Creates follow-up issue
10a. PR merged automatically            - Links issue to PR
                                         - Adds label: tech-lead-changes-requested
                                         ↓
                                    9b. Agent receives issue assignment
                                         ↓
                                    10b. Agent addresses feedback and updates PR
                                         ↓
                                    11b. tech-lead-review.yml re-triggers
                                         ↓
                                    12b. Tech Lead re-reviews (back to step 6)
```

### Optional Flow (PR Doesn't Require Tech Lead Review)

```
1. PR Created/Updated
   ↓
2. tech-lead-review.yml analyzes PR
   ↓
3. Determines review is optional
   ↓
4. Adds info label: tech-lead:<name> (no blocking labels)
   ↓
5. auto-review-merge proceeds normally
   ↓
6. PR merged automatically (if all other criteria met)
```

### WIP (Work In Progress) Handling

PRs marked as WIP are excluded from tech lead review until ready:

**WIP Detection:**
- Draft PRs (GitHub's draft status)
- Title contains: `[WIP]`, `WIP:`, `WIP `, `[do not merge]`, `[dnm]`
- Case-insensitive matching

**Behavior:**
- Tech lead review workflows skip WIP PRs
- Existing tech lead labels are removed
- Informative comment posted (on first WIP detection)
- Review automatically triggers when WIP is removed

**To Resume Review:**
1. Remove WIP markers from title
2. Convert from draft to ready (if draft)
3. Push an update or manually trigger workflow

## Review Triggers

A PR requires Tech Lead review if ANY of these conditions are met:

### 1. Protected Paths Modified

- `.github/workflows/**`
- `.github/actions/**`
- `.github/agents/**`
- `.github/agent-system/**`
- `.github/CODEOWNERS`

### 2. Complexity Thresholds Exceeded

- More than 5 files changed
- More than 100 lines changed

### 3. Security Keywords Detected

- `secret`, `password`, `token`
- `auth`, `permission`, `security`

### 4. Not WIP

- PR is not in draft status
- Title does not contain WIP markers

## Tech Lead Assignment

Tech Leads are assigned based on path patterns defined in their agent profiles:

### Example: workflows-tech-lead

**Responsible for:**
- `.github/workflows/**`
- `.github/actions/**`

**Review focus:**
- Action version pinning
- Secret handling
- Workflow permissions
- Concurrency controls
- Error handling

### Example: agents-tech-lead

**Responsible for:**
- `.github/agents/**`
- `.github/agent-system/**`
- Agent-related tools

**Review focus:**
- Agent definition consistency
- Pattern matching correctness
- Performance metrics accuracy
- Documentation completeness

## Integration with Auto-Review-Merge

The auto-review-merge workflow is enhanced to:

1. **Check Tech Lead labels before merge:**
   ```bash
   # Block merge if review needed but not approved
   if has_label "needs-tech-lead-review" && !has_label "tech-lead-approved"; then
     block_merge "Tech Lead review required"
   fi
   
   # Block merge if changes requested
   if has_label "tech-lead-changes-requested"; then
     block_merge "Tech Lead requested changes"
   fi
   ```

2. **Post informative comments:**
   - Explains why merge is blocked
   - Provides next steps
   - Links to Tech Lead review system docs

3. **Proceed when approved:**
   - Logs Tech Lead approval
   - Continues with normal auto-merge flow

## Agent Response Workflow

When a Tech Lead requests changes:

1. **Agent receives notification** (via PR comment mentions)
2. **Agent analyzes feedback** from Tech Lead review comments
3. **Agent makes necessary changes** and pushes to PR branch
4. **tech-lead-review.yml re-triggers** on push
5. **Workflow notifies Tech Lead** to re-review
6. **Tech Lead re-reviews** and either approves or requests more changes
7. **Cycle repeats** until approval is given

## Benefits

### Quality Assurance
- Expert review for critical changes
- Catches issues before they reach production
- Maintains high code standards

### Automated Process
- No manual intervention required
- Labels track state automatically
- Notifications keep everyone informed

### Flexible Review
- Optional review for simple changes
- Required review for complex/sensitive changes
- Iterative feedback cycle

### Integration
- Works seamlessly with existing auto-merge
- Preserves autonomous development flow
- Adds quality gate without blocking unnecessarily

## Configuration

### Adding a New Tech Lead

1. Create agent definition in `.github/agents/<name>-tech-lead.md`
2. Define path patterns in `tech_lead_for_paths` field
3. Add agent to `tools/match-pr-to-tech-lead.py` (happens automatically via agent loading)

### Adjusting Review Requirements

Edit `TECH_LEAD_THRESHOLDS` in `tools/match-pr-to-tech-lead.py`:

```python
TECH_LEAD_THRESHOLDS = {
    "max_files_for_optional": 5,      # Small PRs might not need review
    "max_lines_for_optional": 100,    # Small changes might not need review
    "always_require_for_patterns": [  # Keywords that always require review
        r"secret", r"password", r"token",
        r"auth", r"permission", r"security",
    ]
}
```

## Monitoring and Metrics

The system logs:
- PR analysis results
- Tech Lead assignments
- Review state changes
- Merge decisions

These logs can be used to track:
- Tech Lead review frequency
- Average time to approval
- Common change request patterns
- System effectiveness

## Troubleshooting

### PR stuck in review
- Check for `needs-tech-lead-review` label
- Verify Tech Lead was notified (check for comment)
- Manually ping Tech Lead if needed

### Label not updating after review
- Verify review came from correct Tech Lead
- Check workflow logs for errors
- Re-run workflow via workflow_dispatch if needed

### Auto-merge still blocked
- Confirm `tech-lead-approved` label is present
- Check for other blocking labels
- Verify PR meets all merge criteria (not just Tech Lead review)

## Future Enhancements

Potential improvements to consider:

1. **Multiple reviewer requirements** for high-risk changes
2. **Time-based escalation** if review is delayed
3. **Automated feedback analysis** to guide agent fixes
4. **Review quality metrics** to track Tech Lead effectiveness
5. **Smart re-review triggers** based on change scope

## Automated Feedback Loop

**NEW:** The system now includes an automated feedback loop that converts tech lead review comments into agent work items.

### How It Works

1. **Tech lead requests changes** on a PR
2. **Feedback handler automatically creates** a follow-up issue
3. **Issue is assigned** to the most appropriate agent based on:
   - PR content and files changed
   - Review comments and requested changes
   - Agent specializations and expertise
4. **Agent addresses feedback** and updates the PR
5. **Tech lead is notified** for re-review
6. **Cycle repeats** until approved

### Key Benefits

- **Automated tracking**: No manual issue creation needed
- **Smart assignment**: Right agent for the right fixes
- **Clear accountability**: Follow-up issues document the cycle
- **Seamless integration**: Works with existing workflows

### See Complete Documentation

For detailed information about the automated feedback loop:

- **[Tech Lead Feedback Loop](./TECH_LEAD_FEEDBACK_LOOP.md)** - Complete workflow documentation
- **[Tech Lead Feedback Handler](./.github/workflows/tech-lead-feedback-handler.yml)** - Workflow implementation

## Related Documentation

- [Tech Lead Feedback Loop](./TECH_LEAD_FEEDBACK_LOOP.md) - **NEW: Automated review → fix → re-review cycle**
- [Tech Lead Labels](./TECH_LEAD_LABELS.md) - Label reference guide
- [Tech Lead Flow Diagrams](./TECH_LEAD_REVIEW_FLOW_DIAGRAMS.md) - Visual workflow diagrams
- [Tech Lead Agents](./.github/agents/)
- [PR Matching Tool](../tools/match-pr-to-tech-lead.py)
- [Auto-Review-Merge Workflow](./.github/workflows/auto-review-merge.yml)
- [Autonomous System Architecture](../AUTONOMOUS_SYSTEM_ARCHITECTURE.md)

---

*🤖 Tech Lead Review Cycle System - Designed and implemented by @workflows-tech-lead*
*Last updated: 2025-11-20*
