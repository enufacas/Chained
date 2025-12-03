# GitHub Repository Variable Setup for Error Observer

## Overview

The error-observer agent requires a GitHub repository variable `GIT_REPO` to forward errors to GitHub Actions via `repository_dispatch` events. This guide explains how to set up this variable.

## Required Variable

### Variable Name
```
GIT_REPO
```

### Format
```
owner/repository
```

### Examples
- `enufacas/Chained`
- `your-username/your-repo`

## How to Set Up

### Step 1: Navigate to Repository Settings

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, navigate to **Secrets and variables** → **Actions**
4. Click on the **Variables** tab (not Secrets)

### Step 2: Create the Variable

1. Click **New repository variable**
2. Enter the following:
   - **Name**: `GIT_REPO`
   - **Value**: `owner/repository` (e.g., `enufacas/Chained`)
3. Click **Add variable**

### Step 3: Verify Configuration

The variable will be automatically used by:
- `.github/workflows/deploy-adk-agents.yml` - Passes it to Terraform
- `infrastructure/terraform/adk-agents.tf` - Configures error-observer agent

## What This Variable Does

The `GIT_REPO` variable tells the error-observer agent which GitHub repository to send error events to via `repository_dispatch`. This enables:

1. **Automated Error Triage**: Errors from Cloud Run services are automatically forwarded to GitHub
2. **Copilot-Driven Issue Creation**: GitHub Actions can create issues from error events
3. **Centralized Error Management**: All A2A system errors flow through one pipeline

## Fallback Behavior

If `GIT_REPO` is not set:
- Terraform will use the default value: `"enufacas/Chained"`
- The error-observer will still function, but errors will be sent to the default repository

## Testing

After setting the variable:

1. Trigger a deployment: Go to Actions → Deploy: ADK Agents → Run workflow
2. Check Terraform logs to verify the variable is being used
3. Verify the error-observer receives the correct `GIT_REPO` environment variable:
   ```bash
   gcloud run services describe chained-error-observer \
     --region=us-central1 \
     --format="value(spec.template.spec.containers[0].env)"
   ```

## Troubleshooting

### Variable Not Found
- Make sure you're on the **Variables** tab, not **Secrets**
- Variables are repository-scoped and visible to all Actions workflows

### Wrong Repository Receiving Errors
- Check the value of `GIT_REPO` variable (should be `owner/repository` format)
- Redeploy after changing the variable value

### Error Observer Not Starting
- Verify the `GITHUB_PAT` secret is also configured (required for authentication)
- Check Cloud Run logs: `gcloud run logs read chained-error-observer --region=us-central1`

## Related Documentation

- [Error Observer Agent](../a2a-agents/ERROR_OBSERVER.md)
- [Infrastructure README](../../infrastructure/README.md)
- [Deploy ADK Agents Workflow](../../.github/workflows/deploy-adk-agents.yml)

## Security Notes

- This variable is **not sensitive** - it only contains the repository name
- The actual authentication uses `GITHUB_PAT` secret (separate configuration)
- Repository variables are visible to anyone with repository access
