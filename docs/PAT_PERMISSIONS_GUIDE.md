# GitHub Personal Access Token (PAT) Permissions Guide

This document outlines the required permissions for the Personal Access Token (PAT) used by the Chained autonomous system, particularly for the dynamic workflow orchestrator and enhanced API access.

## Overview

The Chained system uses GitHub Personal Access Tokens for:
1. **Copilot Assignment** - Assigning issues to GitHub Copilot
2. **API Access** - Enhanced rate limits for monitoring and operations
3. **Dynamic Orchestration** - Adjusting workflows based on usage
4. **Learning & Idea Generation** - Fetching data and creating issues/PRs

## Token Types

### Standard Token (GITHUB_TOKEN)
- **Type**: Automatic token provided by GitHub Actions
- **Limitations**: 
  - Cannot assign to Copilot
  - Lower rate limits (1,000 requests/hour for authenticated)
  - Limited to repository scope
- **Use**: Sufficient for basic operations but not for full autonomy

### Enhanced Token (COPILOT_PAT)
- **Type**: Personal Access Token (fine-grained or classic)
- **Purpose**: Full autonomous operation with enhanced capabilities
- **Required**: For production use with dynamic scheduling

## Required Permissions

### For Fine-Grained Personal Access Token (Recommended)

Create at: https://github.com/settings/personal-access-tokens/new

#### Repository Permissions (Select your repository)

| Permission | Access Level | Purpose |
|------------|-------------|----------|
| **Actions** | Read and write | Trigger and manage workflow runs |
| **Contents** | Read and write | Read files, create branches, commit changes |
| **Issues** | Read and write | Create issues, assign to users/Copilot, manage labels |
| **Pull Requests** | Read and write | Create PRs, auto-review, auto-merge |
| **Metadata** | Read | Access repository metadata (always included) |
| **Workflows** | Read and write | Update workflow files dynamically |

#### Account Permissions (Optional but Recommended)

| Permission | Access Level | Purpose |
|------------|-------------|----------|
| **Copilot** | Read | Monitor Copilot usage (if API available) |

### For Classic Personal Access Token

Create at: https://github.com/settings/tokens/new

Select these scopes:

- [x] **repo** (Full control of private repositories)
  - [x] repo:status
  - [x] repo_deployment
  - [x] public_repo
  - [x] repo:invite
  - [x] security_events
- [x] **workflow** (Update GitHub Action workflows)
- [ ] admin:org (Not required unless using organization features)
- [ ] admin:public_key (Not required)
- [ ] admin:repo_hook (Not required)
- [ ] admin:org_hook (Not required)
- [ ] gist (Not required)
- [ ] notifications (Optional - for notification management)
- [ ] user (Not required)
- [ ] delete_repo (Not required - dangerous)

## Setup Instructions

### Step 1: Create the Token

#### Option A: Fine-Grained Token (Recommended)

1. Go to https://github.com/settings/personal-access-tokens/new
2. **Token name**: `Chained-Orchestrator-PAT`
3. **Expiration**: Choose based on your security policy (90 days recommended)
4. **Description**: "Enhanced PAT for Chained autonomous system with dynamic workflow orchestration"
5. **Repository access**: Select "Only select repositories" → Choose your Chained repository
6. **Permissions**: Set as specified in the table above
7. Click "Generate token"
8. **Copy the token immediately** (you won't see it again)

#### Option B: Classic Token

1. Go to https://github.com/settings/tokens/new
2. **Note**: `Chained-Orchestrator-PAT`
3. **Expiration**: Choose based on your security policy (90 days recommended)
4. **Select scopes**: Check boxes as specified above
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

### Step 2: Add Token to Repository

1. Go to your repository settings: `https://github.com/YOUR_USERNAME/Chained/settings/secrets/actions`
2. Click "New repository secret"
3. **Name**: `COPILOT_PAT`
4. **Value**: Paste your token
5. Click "Add secret"

### Step 3: Configure Usage Variables

Add these repository variables for accurate tracking:

1. Go to: `https://github.com/YOUR_USERNAME/Chained/settings/variables/actions`
2. Create the following variables:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `COPILOT_MONTHLY_QUOTA` | `1500` | Your monthly Copilot API quota (Pro+ = 1500) |
| `COPILOT_REQUESTS_USED` | `300` | Current requests used (update manually or via workflow) |
| `COPILOT_RESET_DAY` | `1` | Day of month when quota resets |

### Step 4: Verify Setup

Run the verification workflow:

```bash
# Manual trigger
gh workflow run dynamic-orchestrator.yml

# Or via Actions UI
# Go to Actions → "Orchestrator: Dynamic Scheduling" → Run workflow
```

## Usage Monitoring

### View Current Usage

```bash
# From repository root
cd tools
python3 copilot-usage-tracker.py
```

### Update Usage Count

When you want to manually update the usage:

```bash
# Update to 450 requests used
python3 copilot-usage-tracker.py --used 450
```

### Trigger Orchestration

```bash
# Let system determine mode
gh workflow run dynamic-orchestrator.yml

# Force aggressive mode
gh workflow run dynamic-orchestrator.yml -f mode=aggressive

# Force conservative mode with updated usage
gh workflow run dynamic-orchestrator.yml -f mode=conservative -f update_usage=500
```

## Security Best Practices

### Token Security

1. **Never commit tokens** to the repository
2. **Use repository secrets** for storage
3. **Set expiration dates** - rotate regularly
4. **Use fine-grained tokens** when possible (more secure)
5. **Limit repository access** to only what's needed
6. **Monitor token usage** in GitHub settings

### Token Rotation

Recommended rotation schedule:
- **Production**: Every 90 days
- **Development**: Every 30-60 days
- **Immediately if**: Token is compromised or suspicious activity detected

### Revoking a Token

If you need to revoke a token:

1. Go to https://github.com/settings/tokens (classic) or https://github.com/settings/personal-access-tokens (fine-grained)
2. Find the token
3. Click "Delete" or "Revoke"
4. Create a new token following the steps above
5. Update the `COPILOT_PAT` secret in your repository

## Troubleshooting

### "Bad credentials" Error

- **Cause**: Token is invalid, expired, or not set
- **Solution**: 
  1. Verify token exists in repository secrets
  2. Check token hasn't expired
  3. Regenerate if necessary

### "Resource not accessible by integration" Error

- **Cause**: Token lacks required permissions
- **Solution**: 
  1. Review permissions table above
  2. Update token permissions in GitHub settings
  3. May need to recreate token with correct permissions

### Workflows Not Updating

- **Cause**: Token lacks workflow write permission
- **Solution**: 
  1. Ensure "workflow" scope (classic) or "Workflows: Read and write" (fine-grained)
  2. Check token hasn't expired

### Rate Limit Issues

- **Cause**: Using GITHUB_TOKEN instead of COPILOT_PAT
- **Solution**: 
  1. Verify COPILOT_PAT secret exists
  2. Check workflows use `${{ secrets.COPILOT_PAT || secrets.GITHUB_TOKEN }}`

## API Rate Limits

### With GITHUB_TOKEN
- **Authenticated**: 1,000 requests/hour
- **Per repository**: 1,000 requests/hour

### With Personal Access Token (COPILOT_PAT)
- **Authenticated**: 5,000 requests/hour
- **Per repository**: 5,000 requests/hour
- **Copilot Premium**: 1,500 requests/month (separate quota)

### Checking Rate Limit

```bash
# Via API
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit

# Via tool
python3 tools/copilot-usage-tracker.py --json | jq '.stats'
```

## Advanced Configuration

### Environment Variables

The system respects these environment variables:

```bash
# Token (checked in order)
COPILOT_PAT=ghp_xxxxxxxxxxxx
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GH_TOKEN=ghp_xxxxxxxxxxxx

# Usage tracking
COPILOT_MONTHLY_QUOTA=1500
COPILOT_REQUESTS_USED=300
COPILOT_RESET_DAY=1
```

### Custom Scheduling Modes

Edit `tools/copilot-usage-tracker.py` to customize mode frequencies:

```python
frequencies = {
    'aggressive': {
        'learn-tldr': '0 */3 * * *',      # Every 3 hours
        'learn-hn': '0 */2 * * *',        # Every 2 hours
        # ... customize as needed
    },
    # ...
}
```

## Support

For issues or questions:
1. Check [FAQ.md](../FAQ.md)
2. Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. Open an issue with label `orchestrator` or `security`

## References

- [GitHub Personal Access Tokens Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Fine-grained PAT Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-fine-grained-personal-access-token)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [Repository Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
