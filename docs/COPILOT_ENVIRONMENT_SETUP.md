# GitHub Copilot Environment Setup Guide

## Overview

This guide explains how to configure the GitHub Copilot execution environment to provide wide access for agents like `@meta-coordinator-system` that need elevated permissions.

## The Problem

When GitHub Copilot is assigned to an issue, it runs in a special execution environment powered by GitHub Actions. By default:
- Copilot has access to a standard `GITHUB_TOKEN` with limited permissions
- Repository secrets are NOT automatically available to Copilot
- Agents requiring wide permissions (create issues, merge PRs, etc.) cannot function without proper configuration

## The Solution

GitHub provides a way to pass secrets and configure the Copilot environment using the **`copilot` environment** in GitHub Actions.

### Step 1: Create the Copilot Environment

1. Navigate to your repository on GitHub
2. Click **Settings** (gear icon in the top menu)
3. In the left sidebar, click **Environments**
4. Click **New environment**
5. Name it exactly `copilot` (lowercase, no spaces)
6. Click **Configure environment**

### Step 2: Add Required Secrets

In the `copilot` environment configuration:

1. Scroll to **Environment secrets**
2. Click **Add secret**

#### COPILOT_PAT Secret

**Name:** `COPILOT_PAT`  
**Value:** A Personal Access Token (PAT) with the following scopes:
- `repo` (full control of private repositories)
- `workflow` (update GitHub Action workflows)

**How to create a PAT:**
1. Go to GitHub Settings (your profile, not repository)
2. Navigate to **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Click **Generate new token (classic)**
4. Give it a descriptive name: "Copilot Wide Access Token"
5. Select scopes: `repo`, `workflow`
6. Set expiration (recommend 90 days with calendar reminder to renew)
7. Click **Generate token**
8. **IMPORTANT:** Copy the token immediately (you won't be able to see it again)
9. Add it as the `COPILOT_PAT` secret in the `copilot` environment

### Step 3: Verify copilot-setup-steps.yml

Ensure your `.github/workflows/copilot-setup-steps.yml` file includes:

```yaml
jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    
    # CRITICAL: Reference the copilot environment
    environment: copilot
    
    permissions:
      contents: read
    
    steps:
      # Your setup steps here
```

**Key requirement:** The `environment: copilot` line tells GitHub Actions to make environment secrets available.

### Step 4: Test the Configuration

1. Trigger a workflow that creates and assigns a Copilot issue (e.g., meta-coordinator)
2. Monitor the Copilot session logs
3. Check for:
   - ✅ "COPILOT_PAT secret is available"
   - ✅ "Using COPILOT_PAT for wide access"
   
If you see warnings about COPILOT_PAT not being available, double-check:
- Environment is named exactly `copilot`
- Secret is named exactly `COPILOT_PAT`
- copilot-setup-steps.yml references `environment: copilot`

## How It Works

### 1. Workflow Creates Issue
```yaml
# meta-coordinator.yml
- name: Create coordination issue
  env:
    GH_TOKEN: ${{ secrets.COPILOT_PAT || secrets.GITHUB_TOKEN }}
  run: |
    gh issue create --title "..." --body "..."
```

### 2. Issue Assigned to Copilot
```bash
# Copilot gets assigned via GraphQL API
./tools/assign-copilot-to-issue.sh
```

### 3. GitHub Triggers Copilot Environment
- Runs `.github/workflows/copilot-setup-steps.yml`
- Loads secrets from `copilot` environment
- Makes `COPILOT_PAT` available to Copilot agent

### 4. Copilot Agent Uses Wide Access
```bash
# In Copilot execution environment
export GH_TOKEN="${COPILOT_PAT}"
gh pr merge 123 --squash
gh issue create --title "Feedback" --body "..."
```

## Agents Requiring Wide Access

### @meta-coordinator-system
**Needs:**
- `contents: write` - Create branches, push changes
- `issues: write` - Create, manage, close issues
- `pull-requests: write` - Merge PRs, apply labels
- `actions: read` - Read workflow status

**Why:**
- Creates feedback issues when tech leads request changes
- Assigns agents to issues
- Auto-merges approved PRs
- Manages labels across system

### Future Agents

When creating new agents that need wide permissions:
1. Document required permissions in agent definition
2. Add permission checks in agent code
3. Provide graceful fallback behavior
4. Test with both COPILOT_PAT and GITHUB_TOKEN

## Security Considerations

### Why Not Just Use GITHUB_TOKEN?

The standard `GITHUB_TOKEN` has intentional limitations:
- Cannot trigger workflows
- Cannot assign Copilot to issues
- Limited write permissions
- Restricted by repository settings

### PAT Security Best Practices

1. **Use classic PATs** (not fine-grained) for Copilot
2. **Set expiration** - 90 days with renewal reminders
3. **Limit scope** - Only `repo` and `workflow` if needed
4. **Rotate regularly** - Update token every 90 days
5. **Monitor usage** - Check audit logs periodically
6. **Use environment** - Don't add PAT as repository secret directly

### Why Use the Copilot Environment?

The `copilot` environment provides:
- **Isolation** - Only available to Copilot sessions
- **Audit trail** - Environment secret usage is logged
- **Access control** - Can require approval for environment
- **Rotation** - Update secret without changing workflows

## Troubleshooting

### "COPILOT_PAT not configured" Warning

**Cause:** Secret not accessible in copilot environment

**Solutions:**
1. Verify environment named exactly `copilot`
2. Check secret exists in environment (not repository secrets)
3. Ensure copilot-setup-steps.yml has `environment: copilot`
4. Check PAT hasn't expired

### "Permission denied" Errors

**Cause:** PAT has insufficient scopes

**Solutions:**
1. Regenerate PAT with correct scopes (`repo`, `workflow`)
2. Update COPILOT_PAT secret in copilot environment
3. Wait ~5 minutes for GitHub to propagate changes

### Copilot Session Fails Immediately

**Cause:** copilot-setup-steps.yml has errors

**Solutions:**
1. Test workflow manually: Actions tab → Copilot Setup Steps → Run workflow
2. Check for YAML syntax errors
3. Verify all steps complete successfully
4. Review setup step logs for failures

## Maintenance

### Regular Tasks

**Monthly:**
- Check PAT expiration date
- Review Copilot session logs for issues
- Verify environment secrets still configured

**Per Session:**
- Monitor Copilot for permission warnings
- Check if operations complete successfully
- Review any degraded mode messages

### Token Renewal

When PAT expires:
1. Generate new PAT with same scopes
2. Update COPILOT_PAT in copilot environment
3. Test with a manual Copilot invocation
4. Set calendar reminder for next expiration

## Documentation References

- [GitHub Copilot Agent Environment Customization](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/customize-the-agent-environment)
- [GitHub Actions Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## Quick Reference

### Configuration Checklist

- [ ] Created `copilot` environment in repository settings
- [ ] Added `COPILOT_PAT` secret to copilot environment
- [ ] PAT has `repo` and `workflow` scopes
- [ ] copilot-setup-steps.yml includes `environment: copilot`
- [ ] Set PAT expiration reminder
- [ ] Tested with manual workflow run
- [ ] Verified Copilot can access secret

### Testing Commands

```bash
# Test setup workflow
gh workflow run copilot-setup-steps.yml

# Create test issue for Copilot
gh issue create --title "Test Copilot Access" --body "Test"

# Assign to Copilot
./tools/assign-copilot-to-issue.sh

# Monitor Copilot session
gh run list --workflow="Copilot Session"
```

---

**Created:** 2025-11-23  
**Last Updated:** 2025-11-23  
**Maintained by:** @workflows-tech-lead, @agents-tech-lead
