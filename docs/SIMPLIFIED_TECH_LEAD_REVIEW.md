# Simplified Tech Lead Review System

## Overview

The tech lead review system has been simplified and consolidated into the main `auto-review-merge.yml` workflow. This replaces the previous fragile 4-workflow system with a single, maintainable workflow organized into clear stages.

## Previous System (Removed)

**4 Fragile Workflows:**
1. `pr-tech-lead-trigger.yml` - Lightweight trigger (45 lines)
2. `tech-lead-review.yml` - Main review logic (525 lines)
3. `tech-lead-feedback-handler.yml` - Feedback processing (445 lines)  
4. `setup-tech-lead-labels.yml` - Label creation (kept)

**Problems:**
- Complex workflow_run triggers were fragile
- Hard to debug and maintain
- Approval requirements for bot PRs caused issues
- Scattered logic across multiple files
- Race conditions between workflows

## New Simplified System

**Single Workflow with 3 Stages:**

### Stage 1: Analyze PRs
**Job:** `analyze-prs`

- Runs on PR events and scheduled (every 15 minutes)
- Analyzes all open, non-draft PRs
- Uses `tools/match-pr-to-tech-lead.py` to determine tech lead requirements
- Builds a matrix of PRs with their analysis results
- Outputs: PR matrix with tech lead requirements and current labels

**Key Logic:**
```yaml
- Get all open PRs (or specific PR from trigger)
- For each PR:
  - Check if WIP (skip if yes)
  - Run tech lead complexity analysis
  - Check current labels (approved, needs review, changes requested)
  - Build matrix item with all metadata
```

### Stage 2: Process PRs
**Job:** `process-pr` (matrix job, runs per PR)

- Runs for each PR from Stage 1 matrix
- Handles tech lead label management
- Processes review state changes
- Creates agent follow-up issues if needed
- Posts comments about tech lead review status

**Key Actions:**
- Apply tech lead labels (`tech-lead:*`, `needs-tech-lead-review`)
- Post initial tech lead analysis comment (on new PRs only)
- Handle review approvals (add `tech-lead-approved` label)
- Handle change requests (add `tech-lead-changes-requested` label)
- Create follow-up issues for agents to fix feedback
- Skip WIP PRs entirely

### Stage 3: Auto-Merge
**Job:** `auto-merge` (matrix job, runs per PR)

- Runs after Stage 2 completes (uses `always()` condition)
- Refreshes PR state to get latest labels
- Checks merge eligibility:
  - Tech lead approval if required
  - No outstanding change requests
  - From trusted source (owner or bot)
  - Has copilot label
- Approves and merges if eligible
- Logs reason if not eligible

**Blocking Conditions:**
- `needs-tech-lead-review` present WITHOUT `tech-lead-approved`
- `tech-lead-changes-requested` present
- Not from trusted source
- PR is draft or closed

## Schedule-Based Operation

The workflow runs on a schedule every 15 minutes, just like the original auto-review-merge workflow. This ensures:

- All PRs are continuously monitored
- Tech lead reviews are processed promptly
- No complex triggers or race conditions
- Simple, predictable behavior

## Tech Lead Review Flow

### Happy Path (Approved)
1. PR opened → Stage 1 analyzes → Needs tech lead review
2. Stage 2 applies labels, posts comment, assigns tech lead
3. Stage 3 waits (blocks merge)
4. Tech lead approves PR (via GitHub UI)
5. Next scheduled run: Stage 2 detects approval, updates labels
6. Stage 3 merges PR

### Change Request Path
1. PR opened → Needs tech lead review (same as above)
2. Tech lead requests changes (via GitHub UI)
3. Next scheduled run: Stage 2 detects changes requested
4. Stage 2 adds `tech-lead-changes-requested` label
5. Stage 2 creates follow-up issue for agent to fix
6. Stage 3 blocks merge
7. Agent fixes issues, pushes to PR
8. Tech lead re-reviews and approves
9. Next scheduled run: Stage 2 updates labels, Stage 3 merges

### Optional Review Path  
1. PR opened → Stage 1 analyzes → Tech lead review optional
2. Stage 2 skips tech lead processing
3. Stage 3 proceeds with merge (if other criteria met)

## Benefits of New System

✅ **Single Workflow:** All logic in one file, easier to understand and maintain

✅ **Clear Stages:** Analyze → Process → Merge flow is explicit

✅ **Schedule-Based:** Runs every 15 minutes, no complex triggers

✅ **No Race Conditions:** Jobs run in sequence with explicit dependencies

✅ **Better Error Handling:** Fail-fast: false allows processing all PRs even if one fails

✅ **Matrix Jobs:** Process multiple PRs efficiently in parallel

✅ **Preserved Functionality:** All original tech lead review logic is maintained

✅ **Testable:** Can trigger manually with workflow_dispatch for specific PRs

## Configuration

**Schedule:** Every 15 minutes via cron
```yaml
schedule:
  - cron: '*/15 * * * *'
```

**Triggers:**
- `pull_request` events (opened, synchronize, ready_for_review, reopened)
- `pull_request_review` events (submitted)
- `schedule` (cron)
- `workflow_dispatch` (manual, optional pr_number)

**Concurrency:**
- Scheduled runs: Grouped, cancel-in-progress
- PR-specific runs: Per-PR grouped, cancel-in-progress

## Tools Used

### `tools/match-pr-to-tech-lead.py`
Analyzes PR files and determines:
- Which tech lead(s) should review
- Complexity analysis (file count, line changes, protected paths)
- Whether review is required or optional

**Usage:**
```bash
python3 tools/match-pr-to-tech-lead.py <pr_number> --check-complexity
```

### `tools/match-issue-to-agent.py`
Matches tech lead feedback to appropriate agent for fixes.

**Usage:**
```bash
python3 tools/match-issue-to-agent.py "Issue title" "Issue body"
```

## Labels Used

**Status Labels:**
- `needs-tech-lead-review` - Tech lead review required (blocks merge)
- `tech-lead-approved` - Tech lead approved (allows merge)
- `tech-lead-changes-requested` - Changes requested (blocks merge)
- `tech-lead-review-cycle` - In active review cycle (informational)

**Assignment Labels:**
- `tech-lead:workflows-tech-lead` - Assigned to workflows tech lead
- `tech-lead:agents-tech-lead` - Assigned to agents tech lead
- `tech-lead:docs-tech-lead` - Assigned to docs tech lead
- `tech-lead:github-pages-tech-lead` - Assigned to GitHub Pages tech lead

**Other Labels:**
- `copilot` - PR from Copilot (required for auto-merge)
- `tech-lead-feedback` - Issue for agent to fix feedback
- `agent:<name>` - Agent assigned to issue

## Migration Notes

### Files Removed
- `.github/workflows/pr-tech-lead-trigger.yml`
- `.github/workflows/tech-lead-review.yml`
- `.github/workflows/tech-lead-feedback-handler.yml`

### Files Kept
- `.github/workflows/setup-tech-lead-labels.yml` - Still needed for label creation
- `.github/workflows/auto-review-merge.yml` - Replaced with improved version
- `tools/match-pr-to-tech-lead.py` - Reused for analysis
- `tools/match-issue-to-agent.py` - Reused for agent matching

### Behavior Changes

**No significant behavior changes** - the same tech lead review logic is preserved:

- PRs are still analyzed for tech lead requirements
- Same complexity thresholds (file count, line changes, protected paths)
- Same label-based blocking mechanism in auto-merge
- Agent follow-up issues still created for feedback

**Only difference:** 
- Schedule-based instead of event-triggered
- Runs every 15 minutes instead of immediately on events
- Slight delay (max 15 min) before detection, acceptable tradeoff for simplicity

## Testing

### Manual Testing
```bash
# Test specific PR
gh workflow run auto-review-merge-improved.yml -f pr_number=123

# Check workflow runs
gh run list --workflow=auto-review-merge-improved.yml

# View logs
gh run view <run_id> --log
```

### Test Scenarios
1. ✅ PR that needs tech lead review (modifies .github/workflows/)
2. ✅ PR that doesn't need tech lead review (small change)
3. ✅ Tech lead approves PR
4. ✅ Tech lead requests changes
5. ✅ WIP PR (should be skipped)
6. ✅ Draft PR (should be skipped)

## Future Improvements

Possible enhancements (not implemented yet):

1. **Parallel Stage Execution:** Run process-pr and refresh checks in parallel
2. **Smarter Scheduling:** Dynamic schedule based on PR activity
3. **Notification System:** Slack/email notifications for tech leads
4. **Review SLA Tracking:** Track time to tech lead review
5. **Automated Re-review Requests:** Auto-request re-review after fixes

## Troubleshooting

### PR not being processed
- Check if PR is draft or has WIP marker
- Verify workflow is enabled
- Check workflow runs for errors

### Tech lead review not detected
- Wait up to 15 minutes for scheduled run
- Check if tech lead approved via GitHub UI
- Verify labels are correct

### Follow-up issue not created
- Check if review body has actionable feedback
- Verify agent matching logic in logs
- Check issue creation permissions

## References

- **Workflow:** `.github/workflows/auto-review-merge-improved.yml`
- **Tech Lead Matching:** `tools/match-pr-to-tech-lead.py`
- **Agent Matching:** `tools/match-issue-to-agent.py`
- **Label Setup:** `.github/workflows/setup-tech-lead-labels.yml`
