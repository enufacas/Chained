# Merge Conflict Resolver Workflow

## Overview

The **Merge Conflict Resolver** workflow automatically detects merge conflicts in pull requests and reassigns GitHub Copilot to resolve them using intelligent agent matching.

## Workflow File

`.github/workflows/merge-conflict-resolver.yml`

## Triggers

The workflow runs in three scenarios:

### 1. PR Events (Real-time)
- **synchronize**: When new commits are pushed to a PR
- **opened**: When a PR is first created
- **reopened**: When a closed PR is reopened

### 2. Scheduled Checks (Backup)
- Runs every **30 minutes** to catch conflicts that might be missed
- Ensures no PR with conflicts goes unnoticed

### 3. Manual Dispatch
- Can be triggered manually via GitHub Actions UI
- Accepts optional `pr_number` parameter to check specific PR

## How It Works

### Detection Phase

1. **Get PRs to Check**
   - For PR events: checks the specific PR that triggered the workflow
   - For scheduled runs: checks all open PRs
   - For manual runs: checks specified PR or all open PRs

2. **Check Merge Status**
   - Uses GitHub API to get PR `mergeable` status
   - Identifies conflicts when `mergeable = "CONFLICTING"` or `mergeStateStatus = "DIRTY"`

### Resolution Phase

The workflow behaves differently based on the PR author:

#### For Trusted Sources

Trusted sources include:
- GitHub Actions bot (`github-actions[bot]`)
- Dependabot (`dependabot[bot]`)
- Copilot bots (`copilot*[bot]`, `app/copilot*`)
- Repository owner **with** `copilot` label

**Actions taken:**
1. ✅ Add `merge-conflict` label to PR
2. 🧠 Use intelligent agent matching to select appropriate custom agent
3. 🆕 Create an issue for Copilot with:
   - Detailed conflict information
   - Resolution steps
   - @agent-name mention for attribution
   - Link to the PR
4. 💬 Comment on PR about reassignment to **@agent-name**

#### For Untrusted Sources

For PRs from external contributors or without `copilot` label:

**Actions taken:**
1. ⚠️ Add `merge-conflict` label
2. 💬 Comment with manual resolution instructions
3. ❌ No automatic Copilot reassignment

### Intelligent Agent Matching

The workflow uses `tools/match-issue-to-agent.py` to intelligently match conflicts to the most appropriate custom agent:

- **Default**: `@troubleshoot-expert` (specialized in debugging and conflict resolution)
- **Analyzed**: PR title and body are analyzed for context
- **Confidence**: Reports matching confidence (high/medium/low)
- **Score**: Numeric score indicating match quality

## Features

### 🎯 Intelligent Assignment

- Analyzes PR content to select the best custom agent
- Uses existing agent matching infrastructure
- Defaults to `@troubleshoot-expert` for conflict resolution

### 🔄 Issue Creation

When conflicts are detected in trusted PRs:

1. **Check for existing issue**: Avoids duplicate issues
2. **Create new issue** with:
   - Clear title: "Resolve merge conflicts in PR #X"
   - Detailed description with resolution steps
   - Agent assignment with @mention
   - Labels: `merge-conflict`, `copilot`, `agent:agent-name`

3. **Update existing issue**: If issue already exists, adds update comment

### 💬 PR Comments

The workflow comments on PRs to:
- Notify about conflict detection
- Explain the reassignment process
- Provide manual resolution steps (for untrusted sources)
- Link to the resolution issue

### 🏷️ Labels

- `merge-conflict`: Added to all PRs with conflicts
- `copilot`: Added to resolution issues
- `agent:agent-name`: Specific agent label for attribution

## Examples

### Example 1: Copilot PR with Conflicts

```yaml
PR #123 created by copilot[bot]
↓
New commits pushed (synchronize event)
↓
Workflow detects CONFLICTING status
↓
Creates issue #456 assigned to @troubleshoot-expert
↓
Comments on PR #123 with reassignment details
```

### Example 2: Scheduled Check

```yaml
Scheduled run (30 minutes)
↓
Scans all open PRs
↓
Finds PR #789 with conflicts (from owner + copilot label)
↓
Creates issue #790 with @engineer-master assignment
↓
Comments on PR #789
```

### Example 3: External Contributor

```yaml
PR #234 from external contributor
↓
Push new commits (synchronize event)
↓
Workflow detects conflicts
↓
Adds merge-conflict label
↓
Comments with manual resolution instructions
↓
No automatic Copilot assignment
```

## Resolution Issue Format

When an issue is created, it includes:

```markdown
## 🚨 Merge Conflict Resolution Required

PR #123 has merge conflicts that need to be resolved.

### PR Details
- Title: [PR title]
- Branch: `feature-branch`
- Author: copilot[bot]
- Mergeable Status: CONFLICTING

### 🤖 Agent Assignment

This issue has been assigned to **🔧 @troubleshoot-expert**

**@troubleshoot-expert** - Please resolve the merge conflicts...

**IMPORTANT**: Always mention **@troubleshoot-expert** by name...

### Resolution Steps
1. Checkout the branch
2. Merge the base branch
3. Resolve conflicts
4. Commit and push

### Context
- Agent: @troubleshoot-expert
- Confidence: high
- Score: 85
```

## Configuration

### Environment Variables

- `GH_TOKEN`: Uses `COPILOT_PAT` if available, falls back to `GITHUB_TOKEN`
  - `COPILOT_PAT` recommended for Copilot assignment
  - Requires `repo` scope

### Permissions

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

## Monitoring

### Workflow Logs

Each run produces detailed logs:
- PR scanning progress
- Conflict detection results
- Agent matching details
- Issue creation status
- Summary statistics

### Success Indicators

- ✅ No conflicts found
- ✅ Issue created for conflicts
- ✅ PR commented successfully
- ✅ Agent matched with high confidence

### Failure Indicators

- ⚠️ Failed to create issue
- ⚠️ Failed to comment on PR
- ⚠️ Agent matching failed (uses default)

## Integration with Existing Workflows

### Relationship to System Monitor

The repository already has merge conflict resolution in `system-monitor.yml`:
- Runs every **3 hours**
- **Attempts automatic resolution** with git merge strategies
- For **scheduled, bulk processing**

The new **merge-conflict-resolver.yml**:
- Runs **in real-time** on PR events
- **Reassigns Copilot** to resolve conflicts
- For **immediate, AI-driven resolution**

**They complement each other:**
1. `merge-conflict-resolver.yml` detects conflicts immediately and creates issues
2. Copilot works on the issue to resolve conflicts
3. If Copilot doesn't resolve it, `system-monitor.yml` attempts automatic resolution

### Integration with Copilot Assignment

When a conflict resolution issue is created:
1. `merge-conflict-resolver.yml` creates the issue with labels
2. `copilot-graphql-assign.yml` (runs every 15 minutes) detects the issue
3. Copilot is assigned via GraphQL API
4. Copilot works on resolving the conflict
5. `auto-review-merge.yml` handles PR merging once resolved

## Best Practices

### For Repository Maintainers

1. **Ensure COPILOT_PAT is configured** for proper Copilot assignment
2. **Monitor conflict resolution issues** to track Copilot effectiveness
3. **Review merge-conflict labels** to identify problematic PRs
4. **Adjust agent matching** if certain conflicts need specific agents

### For Custom Agents

When assigned to conflict resolution:

1. **Always use @agent-name** in all comments and commits
2. **Follow resolution steps** provided in the issue
3. **Update the PR** with conflict resolution
4. **Comment on progress** to keep stakeholders informed
5. **Close the issue** once PR is mergeable

### For Contributors

If your PR gets a conflict:

1. **Check for comment** from the workflow
2. **For trusted sources**: Wait for Copilot to resolve (issue will be created)
3. **For external contributors**: Follow manual resolution steps in comment
4. **Test locally** after resolving conflicts
5. **Push changes** to update the PR

## Troubleshooting

### Issue Not Created

**Possible causes:**
- Issue already exists (check for existing issues)
- GitHub API rate limit reached
- Missing permissions (check `GH_TOKEN` scope)

**Solution:**
- Check workflow logs for error messages
- Manually create issue if needed
- Verify repository permissions

### Agent Matching Failed

**Symptom:** Falls back to `@troubleshoot-expert`

**Possible causes:**
- `match-issue-to-agent.py` script error
- Missing Python dependencies
- Invalid PR title/body format

**Solution:**
- Check workflow logs for Python errors
- Verify script is executable
- Review agent matching logic

### PR Not Detected

**Symptom:** Workflow runs but doesn't detect conflict

**Possible causes:**
- GitHub API delay in updating `mergeable` status
- PR is closed
- Conflict was recently resolved

**Solution:**
- Wait a few minutes and check again
- Manually trigger workflow for specific PR
- Verify PR is still open

## Future Enhancements

Potential improvements:

1. **Conflict complexity analysis**: Determine if conflicts are simple or complex
2. **Multiple agent assignment**: For complex conflicts, assign multiple agents
3. **Resolution tracking**: Track time to resolve conflicts by agent
4. **Metrics dashboard**: Visualize conflict resolution statistics
5. **Auto-close issues**: Close issue when PR becomes mergeable

## Related Documentation

- [Agent System Quick Start](../AGENT_QUICKSTART.md)
- [Custom Agents Directory](../.github/agents/)
- [Copilot Assignment Workflow](./COPILOT_ASSIGNMENT.md)
- [Branch Protection Rules](../.github/instructions/branch-protection.instructions.md)

---

**Created by:** @troubleshoot-expert  
**Specialization:** CI/CD, GitHub Actions, Workflow Debugging  
**Timestamp:** 2025-11-14
