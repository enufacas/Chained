# Simplified Tech Lead Review System

## Overview

The tech lead review system has been simplified and consolidated into the main `auto-review-merge.yml` workflow. 

**IMPORTANT:** Tech leads (@workflows-tech-lead, @agents-tech-lead, @docs-tech-lead, @github-pages-tech-lead) are **custom agents**, not human reviewers. They review PRs and provide feedback as agents via Copilot.

## How Tech Lead Agents Work

### Tech Lead Agents
- @workflows-tech-lead - Reviews GitHub Actions workflows
- @agents-tech-lead - Reviews agent system changes  
- @docs-tech-lead - Reviews documentation
- @github-pages-tech-lead - Reviews GitHub Pages content

### Review Process

**Option 1: Via Issue (Recommended for Agents)**
1. PR is opened → Auto-review workflow detects need for tech lead review
2. Workflow applies `needs-tech-lead-review` label
3. If PR has a linked issue, tech lead agent (already assigned via Copilot assignment workflow) reviews on the issue
4. Tech lead agent comments with "✅ APPROVED" or "🔄 CHANGES REQUESTED"  
5. Human or workflow applies appropriate label based on response
6. Auto-merge proceeds if approved

**Option 2: Via GitHub Review UI (Fallback for Humans)**
1. PR needs review → Labels applied
2. Human tech lead (or agent impersonating human) uses GitHub's review UI
3. Approves or requests changes via GitHub's built-in review system
4. Workflow detects review state and applies labels
5. Auto-merge proceeds if approved

### Integration with Copilot Assignment

The tech lead agents leverage the existing Copilot assignment system:
- Issues are assigned to Copilot every 15 minutes (via `copilot-graphql-assign.yml`)
- Agent matching determines which custom agent profile to use
- Tech lead agents monitor their assigned issues for PRs needing review
- They provide feedback directly on the issue or PR

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
- Processes review state changes (from GitHub review UI or manual label updates)
- Tech lead agents can also comment on PR directly
- Posts comments about tech lead review status

**Key Actions:**
- Apply tech lead labels (`tech-lead:*`, `needs-tech-lead-review`)
- Handle review approvals (add `tech-lead-approved` label)
- Handle change requests (add `tech-lead-changes-requested` label)
- Skip WIP PRs entirely

**Note:** Tech lead agents respond via:
1. Comments on linked issue (preferred - integrated with Copilot assignment)
2. GitHub's review UI (fallback - requires manual label application)
3. Direct PR comments (alternative)

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
- Tech lead reviews are processed promptly (agents check every 15 min)
- No complex triggers or race conditions
- Simple, predictable behavior

## Tech Lead Agent Review Flow

### Happy Path (Approved via Agent)
1. PR opened → Stage 1 analyzes → Needs tech lead review
2. Stage 2 applies labels
3. Tech lead agent (already assigned to linked issue) reviews
4. Agent comments "✅ APPROVED" on issue or PR
5. Human or workflow applies `tech-lead-approved` label
6. Next scheduled run: Stage 3 merges PR

### Change Request Path (Agent Requests Changes)
1. PR opened → Needs tech lead review (same as above)
2. Tech lead agent comments "🔄 CHANGES REQUESTED: [details]"
3. Human or workflow applies `tech-lead-changes-requested` label
4. Stage 3 blocks merge
5. PR author fixes issues, pushes to PR
6. Tech lead re-reviews and approves
7. Next scheduled run: Stage 3 merges

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

✅ **Agent-Friendly:** Tech lead agents integrate naturally with Copilot assignment

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
- Tech lead agents leverage existing Copilot assignment system

**Only difference:** 
- Schedule-based instead of event-triggered
- Runs every 15 minutes instead of immediately on events
- Slight delay (max 15 min) before detection, acceptable tradeoff for simplicity
- Tech lead agents (not humans) provide reviews via Copilot

## Testing

### Manual Testing
```bash
# Test specific PR
gh workflow run auto-review-merge.yml -f pr_number=123

# Check workflow runs
gh run list --workflow=auto-review-merge.yml

# View logs
gh run view <run_id> --log
```

### Test Scenarios
1. ✅ PR that needs tech lead review (modifies .github/workflows/)
2. ✅ PR that doesn't need tech lead review (small change)
3. ✅ Tech lead agent approves PR (via comment on issue)
4. ✅ Tech lead agent requests changes (via comment)
5. ✅ WIP PR (should be skipped)
6. ✅ Draft PR (should be skipped)

## Future Improvements

Possible enhancements (not implemented yet):

1. **Automated Label Application:** Workflow detects "✅ APPROVED" comments and auto-applies label
2. **Re-review Notifications:** Auto-notify tech lead when fixes are pushed
3. **Review SLA Tracking:** Track time to tech lead review
4. **Agent Response Parser:** Parse structured responses from tech lead agents

## Troubleshooting

### PR not being processed
- Check if PR is draft or has WIP marker
- Verify workflow is enabled
- Check workflow runs for errors

### Tech lead review not detected
- Wait up to 15 minutes for scheduled run
- Verify tech lead agent has commented with "✅ APPROVED" or "🔄 CHANGES REQUESTED"
- Check if labels are correct (may need manual application after agent comments)

### Agent not responding
- Check if issue is assigned to Copilot
- Verify Copilot assignment workflow is running
- Check if agent is mentioned with @agent-name in issue

## References

- **Workflow:** `.github/workflows/auto-review-merge.yml`
- **Tech Lead Matching:** `tools/match-pr-to-tech-lead.py`
- **Agent Matching:** `tools/match-issue-to-agent.py`
- **Label Setup:** `.github/workflows/setup-tech-lead-labels.yml`
- **Copilot Assignment:** `.github/workflows/copilot-graphql-assign.yml`

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
