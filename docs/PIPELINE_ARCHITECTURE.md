# Autonomous Pipeline Architecture

## Overview

The `autonomous-pipeline.yml` workflow implements a multi-stage progressive pipeline that consolidates all autonomous learning and mission creation activities into a single coordinated execution.

## 8-Stage Architecture

### Stage Flow

```
Learning Collection (Parallel) → Combine → Merge → World Update → Merge → Missions → Merge → Self-Reinforce
```

### Detailed Stage Breakdown

#### Stage 1: Learning Collection (Parallel)
- **Jobs:** `learn-tldr`, `learn-hackernews`, `learn-github-trending`
- **Execution:** All 3 jobs run in parallel
- **Purpose:** Collect learning data from multiple sources
- **Outputs:** Learning count, learning files (as artifacts)
- **Duration:** ~2-5 minutes

#### Stage 2: Combine Learnings
- **Job:** `combine-learnings`
- **Dependencies:** All Stage 1 jobs must complete
- **Purpose:** Merge all learning sources into unified analysis
- **Actions:**
  - Download artifacts from Stage 1
  - Combine JSON data
  - Analyze patterns
  - Create PR with combined learnings
- **Outputs:** `pr_number`, `pr_created`, `total_learnings`
- **Duration:** ~1-2 minutes

#### Stage 2.5: Merge Learning PR ⚡
- **Job:** `merge-learning-pr`
- **Dependencies:** `combine-learnings`
- **Purpose:** Auto-merge learning PR to main
- **Actions:**
  - Receive PR number from Stage 2
  - Auto-approve PR
  - Enable auto-merge
  - Wait for merge (2 min timeout)
  - Fallback to direct merge if needed
- **Duration:** ~10-30 seconds (or up to 2 minutes with checks)

#### Stage 3: World Model Update
- **Job:** `world-update`
- **Dependencies:** `combine-learnings`, `merge-learning-pr`
- **Purpose:** Integrate learnings into world model
- **Actions:**
  - Checkout main (has fresh learnings)
  - Sync agents from registry
  - Integrate learning ideas
  - Increment world tick
  - Update GitHub Pages data
  - Create PR with world updates
- **Outputs:** `pr_number`, `pr_created`, `world_tick`
- **Duration:** ~2-3 minutes

#### Stage 3.5: Merge World PR ⚡
- **Job:** `merge-world-pr`
- **Dependencies:** `world-update`
- **Purpose:** Auto-merge world PR to main
- **Actions:** Same as Stage 2.5
- **Duration:** ~10-30 seconds

#### Stage 4: Agent Missions
- **Job:** `agent-missions`
- **Dependencies:** `world-update`, `merge-world-pr`
- **Purpose:** Create missions for agents
- **Actions:**
  - Checkout main (has fresh world state)
  - Ensure required labels exist
  - Score agents for mission relevance
  - Select top 10 agents per mission
  - Create GitHub issues
  - Update agent positions
  - Create PR with mission data
- **Outputs:** `pr_number`, `pr_created`, `mission_count`
- **Duration:** ~2-4 minutes

#### Stage 4.5: Merge Mission PR ⚡
- **Job:** `merge-mission-pr`
- **Dependencies:** `agent-missions`
- **Purpose:** Auto-merge mission PR to complete cycle
- **Actions:** Same as Stage 2.5
- **Duration:** ~10-30 seconds

#### Stage 5: Self-Reinforcement (Optional)
- **Job:** `self-reinforcement`
- **Dependencies:** `agent-missions`, `merge-mission-pr`
- **Purpose:** Extract insights from completed work
- **Trigger:** Only runs when `include_self_reinforcement=true`
- **Actions:**
  - Collect insights from closed PRs
  - Extract learnings
  - Feed back to learning cycle
- **Duration:** ~1-2 minutes (when enabled)

### Pipeline Summary
- **Job:** `pipeline-summary`
- **Dependencies:** All stages (optional)
- **Purpose:** Log complete pipeline results
- **Actions:** Display stage results and overall status

## Total Pipeline Duration

**Typical run:** 12-20 minutes
- Stage 1: 3-5 min (parallel)
- Stage 2: 1-2 min
- Stage 2.5: 10-30 sec
- Stage 3: 2-3 min
- Stage 3.5: 10-30 sec
- Stage 4: 2-4 min
- Stage 4.5: 10-30 sec
- Stage 5: 0 min (optional)

## Design Principles

### 1. Separation of Concerns
- **Work stages** (2, 3, 4): Focus on creating changes
- **Merge stages** (2.5, 3.5, 4.5): Focus on integration

### 2. Fresh Data Guarantee
Each work stage checks out `main` after the previous merge stage, ensuring:
- Stage 3 sees merged learnings
- Stage 4 sees merged world state
- No race conditions or stale data

### 3. Fail Loudly
If a merge stage fails:
- Pipeline stops immediately
- Error is clearly visible
- Dependent stages don't run with stale data

### 4. Audit Trail
Every change goes through a PR:
- Full commit history preserved
- PR descriptions document changes
- Can review pipeline history via PR list

### 5. Retry Logic
Merge stages implement sophisticated retry:
1. Try GitHub auto-merge (preferred)
2. Wait up to 2 minutes
3. Fallback to direct merge with admin
4. Fail if impossible

## Dependency Graph

```
learn-tldr ─┐
learn-hackernews ─┼─→ combine-learnings ─→ merge-learning-pr ─→ world-update ─→ merge-world-pr ─→ agent-missions ─→ merge-mission-pr ─→ self-reinforcement
learn-github-trending ─┘                                            ↑                                      ↑
                                                                     │                                      │
                                                                     └──────────────────────────────────────┘
                                                                   (needs merge-learning-pr)          (needs merge-world-pr)
```

## Configuration

### Schedule
- **Cron:** `0 8,20 * * *` (8 AM and 8 PM UTC)
- **Frequency:** Twice daily

### Manual Trigger
```bash
gh workflow run autonomous-pipeline.yml
```

### Skip Options
```bash
gh workflow run autonomous-pipeline.yml \
  -f skip_learning=true \
  -f skip_world_update=true \
  -f skip_missions=true \
  -f include_self_reinforcement=true
```

### Required Permissions
```yaml
permissions:
  contents: write
  issues: write
  pull-requests: write
  actions: write
```

## Branch Protection Requirements

For merge stages to work optimally:

1. **Enable auto-merge:** Settings → Pull Requests → ✅ Allow auto-merge
2. **Branch protection:** 
   - Allow admins to bypass (for `--admin` merge)
   - OR: Exempt PRs with `auto-merge` label from checks

## Troubleshooting

See [PIPELINE_TROUBLESHOOTING.md](PIPELINE_TROUBLESHOOTING.md) for detailed debugging steps.

### Quick Checks

**Pipeline stuck?**
```bash
gh run view <run-id>
gh run list --workflow=autonomous-pipeline.yml
```

**Merge stage failed?**
```bash
# Get PR from logs
gh run view <run-id> --log | grep "Created PR #"

# Check PR status
gh pr view <pr-number>

# Manually merge
gh pr merge <pr-number> --squash --admin
```

**Stage skipped?**
- Check `if:` conditions in workflow
- Verify previous stage outputs
- Review dependencies

## Migration from Individual Workflows

Individual workflows (`learn-from-*.yml`, etc.) are now:
- ❌ **No longer scheduled** (removed cron triggers)
- ✅ Available for manual testing
- ✅ Can be called by other workflows
- ✅ Maintained for backward compatibility

Only `autonomous-pipeline.yml` runs on schedule.

## Benefits Over Previous Architecture

| Aspect | Before (Separate Workflows) | After (Unified Pipeline) |
|--------|----------------------------|--------------------------|
| Visibility | Scattered across multiple runs | Single workflow run |
| Dependencies | Loose coupling via `gh workflow run` | Proper `needs:` dependencies |
| Error Handling | Downstream runs even if upstream fails | Failed stage stops pipeline |
| Data Flow | Race conditions possible | Guaranteed fresh data via merge stages |
| Debugging | Check multiple workflow runs | Single workflow log |
| Audit Trail | Implicit via workflow runs | Explicit via PRs + workflow run |
| Resource Control | Uncoordinated | Controlled parallelization |

## Future Enhancements

Possible improvements:
- Add retry logic for merge stages (currently 1 attempt)
- Implement progressive timeouts (shorter for merge stages)
- Add Slack/Discord notifications for merge failures
- Create dashboard showing pipeline health metrics
- Add stage-level caching for faster reruns
- Implement partial pipeline reruns from specific stage

## Related Documentation

- [WORKING_WITH_SYSTEM.md](WORKING_WITH_SYSTEM.md) - User guide
- [PIPELINE_TROUBLESHOOTING.md](PIPELINE_TROUBLESHOOTING.md) - Debugging guide
- [README.md](../README.md) - Project overview
