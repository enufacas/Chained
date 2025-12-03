# Error Observer Secrets Setup Guide

This guide explains how to configure the GitHub repository secrets and GCP Secret Manager secrets required for the error observer agent to function properly.

## Overview

The error observer agent requires a GitHub Personal Access Token (PAT) to dispatch error events to GitHub, which then triggers automated issue creation through the `handle-cloudrun-errors.yml` workflow.

## Required Secrets

### 1. GitHub PAT (Personal Access Token)

**Purpose:** Allows the error observer agent to call GitHub's `repository_dispatch` API to create error notification events.

**Required Permissions:**

For **public repositories** (like enufacas/Chained):
- Classic PAT: `public_repo` scope (access to public repositories)
- Fine-grained PAT: `contents: write` permission

For **private repositories**:
- Classic PAT: `repo` scope (full control of private repositories)
- Fine-grained PAT: `contents: write` permission

**Recommended:** Use `public_repo` scope for public repos to follow least privilege principle.

**Where it's used:**
- Error observer agent reads it as `GITHUB_PAT` environment variable
- Used to authenticate GitHub API calls to `/repos/{owner}/{repo}/dispatches`

## Setup Instructions

### Step 1: Create GitHub Personal Access Token

#### Option A: Classic Token (Recommended for simplicity)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - URL: https://github.com/settings/tokens

2. Click "Generate new token" → "Generate new token (classic)"

3. Configure the token:
   - **Note**: `Chained Error Observer Agent`
   - **Expiration**: Recommended 90 days (set reminder to rotate)
   - **Scopes**: 
     - For **public repositories** (like enufacas/Chained): Select `public_repo` (Access public repositories)
     - For **private repositories**: Select `repo` (Full control of private repositories)

4. Click "Generate token"

5. **IMPORTANT**: Copy the token immediately (starts with `ghp_`)
   - You won't be able to see it again!
   - Example format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### Option B: Fine-grained Token (More secure, repository-specific)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - URL: https://github.com/settings/tokens?type=beta

2. Click "Generate new token"

3. Configure the token:
   - **Token name**: `Chained Error Observer Agent`
   - **Expiration**: Recommended 90 days
   - **Repository access**: Select "Only select repositories" → Choose `enufacas/Chained`
   - **Repository permissions**:
     - Contents: **Read and write** (required for repository_dispatch)

4. Click "Generate token"

5. **IMPORTANT**: Copy the token immediately (starts with `github_pat_`)
   - You won't be able to see it again!
   - Example format: `github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Recommendation:** Use Option B (fine-grained token) for better security - it's scoped to a specific repository with minimal permissions.

### Step 2: Store Token in GCP Secret Manager

The error observer agent running on Cloud Run retrieves the GitHub PAT from GCP Secret Manager for security.

#### Option A: Using gcloud CLI

```bash
# Set your GCP project ID
export GCP_PROJECT_ID="your-project-id"

# Create the secret in Secret Manager
echo -n "ghp_YOUR_ACTUAL_TOKEN_HERE" | gcloud secrets create github-pat \
  --project="${GCP_PROJECT_ID}" \
  --data-file=- \
  --replication-policy="automatic"

# Grant the ADK agents service account access to the secret
gcloud secrets add-iam-policy-binding github-pat \
  --project="${GCP_PROJECT_ID}" \
  --member="serviceAccount:chained-adk-agents@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Verify the secret was created
gcloud secrets describe github-pat --project="${GCP_PROJECT_ID}"
```

#### Option B: Using Google Cloud Console

1. Navigate to Secret Manager in Google Cloud Console
   - URL: https://console.cloud.google.com/security/secret-manager

2. Click "CREATE SECRET"

3. Configure:
   - **Name**: `github-pat`
   - **Secret value**: Paste your GitHub PAT (e.g., `ghp_xxxx...`)
   - **Replication**: Automatic (recommended) or Regional
   - **Rotation**: Optional (recommended to set up rotation reminders)

4. Click "CREATE SECRET"

5. Grant service account access:
   - Open the `github-pat` secret
   - Click "PERMISSIONS" tab
   - Click "GRANT ACCESS"
   - Add principal: `chained-adk-agents@YOUR_PROJECT_ID.iam.gserviceaccount.com`
   - Role: "Secret Manager Secret Accessor"
   - Click "SAVE"

### Step 3: Verify Configuration

After Terraform deployment, verify the error observer can access the secret:

```bash
# Check that the secret exists and has proper IAM bindings
gcloud secrets get-iam-policy github-pat --project="${GCP_PROJECT_ID}"

# The output should include:
# - member: serviceAccount:chained-adk-agents@PROJECT_ID.iam.gserviceaccount.com
# - role: roles/secretmanager.secretAccessor

# Test the error observer agent (after deployment)
curl -X GET https://chained-error-observer-PROJECT_NUMBER.REGION.run.app/health

# Should return: {"status": "healthy", "agent": "error-observer"}
```

### Step 4: Test Error Flow End-to-End

1. Trigger a test error from any agent or UI
2. Check error observer logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-error-observer" \
     --limit 50 \
     --format json \
     --project="${GCP_PROJECT_ID}"
   ```

3. Verify a GitHub issue was created with label `cloud-run-error`

## GitHub Repository Secret (Optional)

If you want to use the GitHub PAT directly in GitHub Actions workflows (not recommended for Cloud Run), you can also store it as a GitHub repository secret:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `ERROR_OBSERVER_GITHUB_PAT`
4. Value: Your GitHub PAT
5. Click "Add secret"

**Note:** The error observer agent does NOT use GitHub repository secrets. It only uses GCP Secret Manager. This is optional for workflow-level operations.

## Security Best Practices

### Token Security

1. **Never commit tokens to source code**
   - Always use Secret Manager or GitHub Secrets
   - Never hardcode in Terraform files

2. **Use least privilege**
   - For **public repositories**: Use `public_repo` scope (classic) or fine-grained token with `contents: write`
   - For **private repositories**: Use `repo` scope (classic) or fine-grained token with `contents: write`
   - **Best practice**: Use fine-grained tokens scoped to specific repository

3. **Rotate regularly**
   - Set token expiration to 90 days
   - Set calendar reminders to rotate before expiration
   - Update Secret Manager when rotating

4. **Monitor usage**
   - Check GitHub settings for token usage/activity
   - Review error observer logs for authentication failures

### Secret Manager Security

1. **Audit access**
   ```bash
   gcloud secrets get-iam-policy github-pat --project="${GCP_PROJECT_ID}"
   ```

2. **Enable audit logging**
   - Secret Manager access is logged in Cloud Audit Logs
   - Review logs for unexpected access

3. **Use secret versions**
   - When rotating, create new version instead of deleting
   - Allows rollback if new token has issues
   
   ```bash
   echo -n "ghp_NEW_TOKEN" | gcloud secrets versions add github-pat \
     --project="${GCP_PROJECT_ID}" \
     --data-file=-
   ```

## Troubleshooting

### Error Observer Returns 500 Error

**Symptom:** Error observer agent fails to dispatch events to GitHub

**Cause:** GitHub PAT not configured or invalid

**Solution:**
1. Check Cloud Run logs for error messages
2. Verify secret exists: `gcloud secrets describe github-pat`
3. Verify IAM binding exists (see Step 3)
4. Check token hasn't expired in GitHub settings

### Permission Denied Error

**Symptom:** Error observer logs show "permission denied" when accessing secret

**Cause:** Service account doesn't have Secret Accessor role

**Solution:**
```bash
gcloud secrets add-iam-policy-binding github-pat \
  --project="${GCP_PROJECT_ID}" \
  --member="serviceAccount:chained-adk-agents@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### GitHub API Rate Limit Exceeded

**Symptom:** Error observer returns 403 errors from GitHub API

**Cause:** Too many API calls or token lacks proper permissions

**Solution:**
1. Check rate limits: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit`
2. Verify token has `repo` scope in GitHub settings
3. Consider implementing rate limiting in error observer (future enhancement)

## Configuration Reference

### Terraform Configuration

The error observer service is configured in `infrastructure/terraform/adk-agents.tf`:

```terraform
resource "google_cloud_run_v2_service" "error_observer" {
  name     = "chained-error-observer"
  location = var.region

  template {
    containers {
      # GitHub PAT from Secret Manager
      env {
        name  = "GITHUB_PAT"
        value_source {
          secret_key_ref {
            secret  = "github-pat"        # Secret Manager secret name
            version = "latest"            # Always use latest version
          }
        }
      }

      # Repository for dispatches
      env {
        name  = "GITHUB_REPO"
        value = "enufacas/Chained"       # Can be configured per environment
      }
    }
  }
}
```

### Agent Code Reference

The error observer reads the secret in `infrastructure/docker/adk-agents/error-observer/agent.py`:

```python
# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_PAT") or os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "enufacas/Chained")
GITHUB_API_URL = "https://api.github.com"
```

## Summary

**Required:**
1. ✅ Create GitHub PAT:
   - **Public repo**: `public_repo` scope (classic) OR fine-grained token with `contents: write`
   - **Private repo**: `repo` scope (classic) OR fine-grained token with `contents: write`
   - **Recommended**: Fine-grained token for better security
2. ✅ Store in GCP Secret Manager as `github-pat`
3. ✅ Grant service account `roles/secretmanager.secretAccessor`
4. ✅ Deploy via Terraform (reads from Secret Manager automatically)

**Optional:**
- Store PAT as GitHub repository secret (for workflow use)

**Security:**
- Never commit tokens to source code
- Rotate tokens every 90 days
- Monitor usage and audit logs
- Use least privilege principle

---

**Document Version:** 1.1  
**Last Updated:** 2025-12-03  
**Changelog:**
- v1.1 (2025-12-03): Added fine-grained token option, clarified public_repo vs repo scope
- v1.0 (2025-12-02): Initial version

**Related Files:**
- `infrastructure/terraform/adk-agents.tf` - Terraform configuration
- `infrastructure/docker/adk-agents/error-observer/agent.py` - Agent implementation
- `.github/workflows/handle-cloudrun-errors.yml` - Workflow triggered by dispatches
