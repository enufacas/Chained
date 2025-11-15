# Autonomous Pipeline Troubleshooting Guide

## Overview

The `autonomous-pipeline.yml` workflow orchestrates the entire learning and mission creation cycle with **8 stages** including dedicated PR merge steps. This guide helps diagnose and fix common issues.

## Pipeline Stages

1. **Stage 1**: Learning Collection (parallel: TLDR, HN, GitHub)
2. **Stage 2**: Combine Learnings
3. **Stage 2.5**: Merge Learning PR ⚡
4. **Stage 3**: World Model Update
5. **Stage 3.5**: Merge World PR ⚡
6. **Stage 4**: Agent Missions
7. **Stage 4.5**: Merge Mission PR ⚡
8. **Stage 5**: Self-Reinforcement (optional)

## Quick Health Check

```bash
# View recent pipeline runs
gh run list --workflow=autonomous-pipeline.yml --limit 5

# View specific run details
gh run view <run-id> --log

# Check run status
gh run view <run-id>
```

## Common Issues

### 1. Pipeline Not Triggering on Schedule

**Symptoms:**
- No runs at scheduled times (8 AM, 8 PM UTC)
- Pipeline shows as "waiting" or doesn't appear

**Possible Causes:**
- Workflow file has syntax errors
- Schedule expression is incorrect
- Branch protection blocking workflow

**Solutions:**

```bash
# Check workflow syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/autonomous-pipeline.yml'))"

# Manually trigger to test
gh workflow run autonomous-pipeline.yml

# Check workflow status in GitHub UI
# Settings → Actions → Check if workflows are enabled
```

### 2. Stage 1 (Learning Collection) Failures

**Symptoms:**
- `learn-tldr`, `learn-hackernews`, or `learn-github-trending` jobs fail
- Error: "Failed to fetch content"
- Timeout errors

**Possible Causes:**
- External APIs (TLDR, HN, GitHub) are down
- Rate limiting from external services
- Network connectivity issues

**Solutions:**

```bash
# Check if individual workflows work
gh workflow run learn-from-tldr.yml
gh run watch

# View specific job logs
gh run view <run-id> --job=<job-id> --log

# The pipeline is designed to continue even if some sources fail
# Verify that at least one learning source succeeded
```

**Debug Steps:**
1. Check if external services are accessible:
   ```bash
   curl -I https://tldr.tech/api/rss/tech
   curl -I https://hacker-news.firebaseio.com/v0/topstories.json
   ```

2. Review rate limiting - pipeline runs twice daily to avoid limits

3. Check job artifacts to see what was collected:
   ```bash
   gh run view <run-id> --log | grep "Collected"
   ```

### 3. Stage 2 (Combine Learnings) Failures

**Symptoms:**
- Combine job fails with "No learnings found"
- Error downloading artifacts
- JSON parsing errors

**Possible Causes:**
- All Stage 1 jobs failed
- Artifact upload/download issues
- Corrupted learning data

**Solutions:**

```bash
# Check if artifacts were created
gh run view <run-id> --log | grep "Upload.*artifact"

# Verify artifact names match expectations
# Should see: tldr-learnings, hn-learnings, github-learnings

# Check if learning files exist locally
ls -la learnings/
```

**Debug Steps:**
1. Verify Stage 1 succeeded:
   ```bash
   gh run view <run-id> --log | grep "Stage 1"
   ```

2. Check artifact retention (7 days):
   ```bash
   # Artifacts older than 7 days are deleted
   # Ensure pipeline runs regularly
   ```

3. Validate JSON structure of learning files:
   ```bash
   python3 -c "import json; print(json.load(open('learnings/tldr_20250115.json')))"
   ```

### 4. Stage 3 (World Update) Failures

**Symptoms:**
- World update job fails
- Error: "File not found: world/world_state.json"
- Python script errors

**Possible Causes:**
- World state files missing or corrupted
- Python dependency issues
- Permission errors

**Solutions:**

```bash
# Check if world files exist
ls -la world/world_state.json world/knowledge.json

# Validate world state JSON
python3 -c "import json; json.load(open('world/world_state.json'))"

# Check Python dependencies
pip install -r requirements.txt

# Manually run world update scripts
python3 world/sync_agents_to_world.py
python3 world/sync_learnings_to_ideas.py
```

**Debug Steps:**
1. Verify world state structure:
   ```bash
   cat world/world_state.json | jq '.tick, .agents | length'
   ```

2. Check if scripts are executable:
   ```bash
   ls -la world/*.py scripts/*.py
   ```

3. Review world update logs for specific errors:
   ```bash
   gh run view <run-id> --log | grep -A10 "Stage 3"
   ```

### 5. Stage 4 (Agent Missions) Failures

**Symptoms:**
- Mission creation fails
- Error: "No recent ideas for missions"
- Issue creation fails

**Possible Causes:**
- No new learning ideas in world model
- GitHub API rate limiting
- Label creation failures
- `create_mission_issues.py` tool missing or failing

**Solutions:**

```bash
# Check if recent ideas exist
cat world/knowledge.json | jq '.ideas | map(select(.source == "learning_analysis")) | length'

# Test label creation
gh label list | grep -E 'learning|agent-mission|ai-generated'

# Manually create labels if needed
gh label create "agent-mission" --color "D93F0B" --description "Agent mission"

# Check if mission tool exists
ls -la tools/create_mission_issues.py

# Test mission creation script
python3 tools/create_mission_issues.py
```

**Debug Steps:**
1. Verify world has recent ideas:
   ```bash
   cat world/knowledge.json | jq '.ideas | length'
   ```

2. Check GitHub API rate limits:
   ```bash
   gh api rate_limit
   ```

3. Review mission creation logs:
   ```bash
   gh run view <run-id> --log | grep -A20 "Creating agent missions"
   ```

### 6. Pipeline Stalls or Hangs

**Symptoms:**
- Pipeline shows "In progress" for extended time
- Specific stage never completes
- No error messages

**Possible Causes:**
- Job waiting for manual approval (shouldn't happen)
- Resource exhaustion
- GitHub Actions infrastructure issues

**Solutions:**

```bash
# Check current status
gh run view <run-id>

# Cancel stuck run
gh run cancel <run-id>

# Re-run pipeline
gh workflow run autonomous-pipeline.yml

# Check GitHub Actions status
curl https://www.githubstatus.com/api/v2/status.json
```

### 7. PR Creation Failures

**Symptoms:**
- Stage completes but no PR created
- Error: "Failed to create pull request"
- Branch conflicts

**Possible Causes:**
- No changes to commit
- Branch protection rules blocking PR
- Insufficient permissions
- Branch name conflicts

**Solutions:**

```bash
# Check if changes exist
git status

# View PR creation logs
gh run view <run-id> --log | grep "Create PR"

# Check GitHub permissions
# Workflow needs: contents: write, pull-requests: write, issues: write

# List existing PRs to check for conflicts
gh pr list --label pipeline
```

**Debug Steps:**
1. Verify git configuration in workflow logs
2. Check if branch was created:
   ```bash
   git branch -r | grep pipeline
   ```
3. Review PR creation command in logs

### 8. Merge Stage Failures (Stages 2.5, 3.5, 4.5)

**Symptoms:**
- Merge stage (2.5, 3.5, or 4.5) fails
- Error: "Failed to merge PR"
- PR stuck in "OPEN" state
- Next stage doesn't have updated data from main

**Possible Causes:**
- Branch protection rules require specific checks
- Auto-merge not enabled on repository
- Insufficient admin permissions for `--admin` merge
- PR has merge conflicts
- Required reviews not satisfied

**Solutions:**

```bash
# Check PR status
gh pr view <pr-number>

# Check if auto-merge is enabled on repo
# Settings → General → Pull Requests → Allow auto-merge

# Manually approve and merge the PR to unblock pipeline
gh pr review <pr-number> --approve
gh pr merge <pr-number> --squash

# Check branch protection settings
gh api repos/{owner}/{repo}/branches/main/protection
```

**Debug Steps:**

1. **Identify which merge stage failed:**
   ```bash
   gh run view <run-id> --log | grep -A10 "Stage.*Merge"
   ```

2. **Get PR number from logs:**
   ```bash
   PR_NUM=$(gh run view <run-id> --log | grep "Created PR #" | tail -1 | grep -oE '#[0-9]+' | tr -d '#')
   gh pr view $PR_NUM --json state,mergeable,mergeStateStatus
   ```

3. **Check what's blocking the merge:**
   ```bash
   gh pr checks $PR_NUM
   gh pr view $PR_NUM --json reviewDecision,statusCheckRollup
   ```

4. **Manual merge if needed:**
   ```bash
   # Approve the PR
   gh pr review $PR_NUM --approve --body "Manual approval after merge stage timeout"
   
   # Try merge with squash
   gh pr merge $PR_NUM --squash || gh pr merge $PR_NUM --squash --admin
   ```

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| "Auto-merge not available" | Repository setting disabled | Settings → Pull Requests → ✅ Allow auto-merge |
| "Required reviews not satisfied" | Branch protection requires reviews | Add bypass for admins or disable for `pipeline` label |
| "Merge conflict detected" | Concurrent changes | Manually resolve conflicts, rebase branch |
| "Timeout waiting for merge" | Checks taking &gt;2 minutes | Optimize checks or increase timeout in workflow |
| "Admin merge failed" | Token lacks admin access | Use PAT with admin access or adjust protection rules |

**Best Practices:**

1. **Enable auto-merge:**
   ```
   Settings → General → Pull Requests → ✅ Allow auto-merge
   ```

2. **Configure branch protection for pipeline:**
   - Option A: Exempt PRs with `auto-merge` label from required checks
   - Option B: Allow admins to bypass protection rules
   - Option C: Use `CODEOWNERS` to auto-approve pipeline PRs

3. **Monitor merge success:**
   ```bash
   # Check last 10 merge stage results
   gh run list --workflow=autonomous-pipeline.yml --limit 10 --json conclusion,name | \
     jq -r '.[] | select(.name | contains("Merge")) | "\(.name): \(.conclusion)"'
   ```

## Pipeline Configuration Issues

### Skipping Stages

If you need to skip stages for testing:

```bash
# Skip learning collection
gh workflow run autonomous-pipeline.yml -f skip_learning=true

# Skip world update
gh workflow run autonomous-pipeline.yml -f skip_world_update=true

# Skip missions
gh workflow run autonomous-pipeline.yml -f skip_missions=true

# Include self-reinforcement
gh workflow run autonomous-pipeline.yml -f include_self_reinforcement=true
```

### Testing Individual Stages

To test stages independently:

```bash
# Test learning collection
gh workflow run learn-from-tldr.yml
gh workflow run learn-from-hackernews.yml

# Test world update (requires learning data)
gh workflow run world-update.yml

# Test mission creation (requires updated world)
gh workflow run agent-missions.yml
```

## Monitoring Pipeline Health

### Key Metrics to Track

1. **Success Rate:**
   ```bash
   gh run list --workflow=autonomous-pipeline.yml --limit 20 --json conclusion
   ```

2. **Average Duration:**
   ```bash
   gh run list --workflow=autonomous-pipeline.yml --limit 10 --json createdAt,updatedAt
   ```

3. **Stage Failure Patterns:**
   ```bash
   # Check which stages fail most often
   gh run list --workflow=autonomous-pipeline.yml --limit 20 --json conclusion,name
   ```

### Setting Up Alerts

Monitor for:
- ✅ Pipeline hasn't run in 24 hours
- ✅ More than 2 consecutive failures
- ✅ Stage 1 has zero learnings collected
- ✅ World tick hasn't incremented in 48 hours

### Recovery Procedures

#### If Pipeline is Completely Broken

1. **Revert to individual workflows:**
   ```bash
   # Temporarily re-enable schedules on individual workflows
   # Edit workflow files to add back schedule triggers
   ```

2. **Manual intervention:**
   ```bash
   # Manually run each stage in order
   gh workflow run learn-from-tldr.yml && sleep 60
   gh workflow run learn-from-hackernews.yml && sleep 60
   gh workflow run combined-learning.yml && sleep 60
   gh workflow run world-update.yml && sleep 60
   gh workflow run agent-missions.yml
   ```

3. **Emergency fixes:**
   ```bash
   # Create emergency PR to fix pipeline
   git checkout -b hotfix/pipeline-repair
   # Make fixes
   git commit -m "fix: emergency pipeline repair"
   git push origin hotfix/pipeline-repair
   gh pr create --title "Emergency: Fix Pipeline" --body "Critical fix"
   ```

## Advanced Debugging

### Enable Debug Logging

Add to workflow run:
```bash
# Set secret ACTIONS_STEP_DEBUG=true in repo settings
# Then view enhanced logs
gh run view <run-id> --log --verbose
```

### Inspect Artifacts

```bash
# Download artifacts for inspection
gh run download <run-id>

# View artifact contents
cd <artifact-name>
cat *.json | jq .
```

### Check Workflow File Changes

```bash
# See recent changes to pipeline workflow
git log --oneline .github/workflows/autonomous-pipeline.yml

# Compare with previous version
git diff HEAD~1 .github/workflows/autonomous-pipeline.yml
```

## Getting Help

### Resources

- **Pipeline Overview:** `docs/WORKING_WITH_SYSTEM.md`
- **Agent System:** `docs/AGENT_QUICKSTART.md`
- **Original Workflows:** `.github/workflows/learn-*.yml`

### Support Channels

1. **Check workflow logs** - Most issues have clear error messages
2. **Review this guide** - Common issues are documented
3. **Test individual stages** - Isolate the problem
4. **Create issue** - If problem persists, open GitHub issue with:
   - Pipeline run ID
   - Full error logs
   - Steps to reproduce

### Useful Commands

```bash
# Complete pipeline health check
echo "=== Pipeline Health Check ==="
echo "Last 5 runs:"
gh run list --workflow=autonomous-pipeline.yml --limit 5
echo ""
echo "World state:"
cat world/world_state.json | jq '{tick, agent_count: .agents|length}'
echo ""
echo "Recent learnings:"
ls -lht learnings/ | head -5
echo ""
echo "Open missions:"
gh issue list --label agent-mission
```

---

**Remember:** The pipeline is designed to be resilient. If one stage fails, examine logs, fix the issue, and re-run. Most issues are self-healing on the next run.
