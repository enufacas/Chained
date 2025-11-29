# Google Vertex AI Claude Setup Guide

This guide explains how to configure Google Vertex AI to serve Claude models for use in the Chained A2A orchestration pipeline.

## Overview

Google Vertex AI provides access to Claude models via OIDC authentication, which is useful when you want to:
- Avoid managing direct Anthropic API keys
- Use existing GCP infrastructure and billing
- Leverage GCP's security and access controls
- Use workload identity federation with GitHub Actions

## Quick Start (Copy-Paste Commands)

Run these commands in Google Cloud Shell or with `gcloud` CLI configured. This sets up everything for the `enufacas/Chained` repository.

```bash
# ============================================================
# QUICK START: Full setup for cogent-tine-479302-j0
# Run these commands in order in Google Cloud Shell
# ============================================================

# Set variables
export PROJECT_ID="cogent-tine-479302-j0"
export REPO="enufacas/Chained"
export SA_NAME="claude-a2a-coordinator"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. Enable required APIs
gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID
gcloud services enable iam.googleapis.com --project=$PROJECT_ID
gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID

# 2. Create service account
gcloud iam service-accounts create $SA_NAME \
  --description="Service account for Claude A2A coordinator in GitHub Actions" \
  --display-name="Claude A2A Coordinator" \
  --project=$PROJECT_ID

# 3. Grant Vertex AI permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user"

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --project=$PROJECT_ID \
  --role="roles/iam.serviceAccountTokenCreator" \
  --member="serviceAccount:${SA_EMAIL}"

# 4. Create workload identity pool
gcloud iam workload-identity-pools create "github-actions-pool" \
  --project=$PROJECT_ID \
  --location="global" \
  --description="Pool for GitHub Actions OIDC" \
  --display-name="GitHub Actions Pool"

# 5. Create workload identity provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-condition="assertion.repository=='${REPO}'"

# 6. Grant workload identity user access
export POOL_NAME="projects/${PROJECT_ID}/locations/global/workloadIdentityPools/github-actions-pool"

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/${REPO}"

# 7. Get the values you need for GitHub
echo ""
echo "============================================================"
echo "ADD THESE TO YOUR GITHUB REPOSITORY SETTINGS"
echo "============================================================"
echo ""
echo "SECRETS (Settings > Secrets and variables > Actions > Secrets):"
echo ""
echo "GCP_WORKLOAD_IDENTITY_PROVIDER:"
gcloud iam workload-identity-pools providers describe "github-provider" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --format="value(name)"
echo ""
echo "GCP_SERVICE_ACCOUNT:"
echo "$SA_EMAIL"
echo ""
echo "VARIABLES (Settings > Secrets and variables > Actions > Variables):"
echo ""
echo "ANTHROPIC_VERTEX_PROJECT_ID:"
echo "$PROJECT_ID"
echo ""
echo "CLOUD_ML_REGION:"
echo "us-east5"
echo ""
echo "CLAUDE_USE_VERTEX:"
echo "true"
echo ""
echo "============================================================"
echo "Setup complete! Add the above values to GitHub."
echo "============================================================"
```

After running the commands above, copy the output values and add them to your GitHub repository settings.

---

## Prerequisites

1. A Google Cloud Platform (GCP) project with billing enabled
2. Access to Vertex AI with Claude models (contact Google Cloud sales if not enabled)
3. GCP CLI (`gcloud`) installed locally or Cloud Shell access
4. Admin access to your GitHub repository for secrets configuration

## Step 1: Enable Required APIs

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Enable required APIs
gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID
gcloud services enable iam.googleapis.com --project=$PROJECT_ID
gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID
```

## Step 2: Create a Service Account

Create a dedicated service account for the Claude A2A coordinator:

```bash
# Create service account
gcloud iam service-accounts create claude-a2a-coordinator \
  --description="Service account for Claude A2A coordinator in GitHub Actions" \
  --display-name="Claude A2A Coordinator" \
  --project=$PROJECT_ID

# Get the full service account email
export SA_EMAIL="claude-a2a-coordinator@${PROJECT_ID}.iam.gserviceaccount.com"
echo "Service Account: $SA_EMAIL"
```

## Step 3: Grant Vertex AI Permissions

Grant the service account permission to use Vertex AI:

```bash
# Grant Vertex AI User role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user"

# Grant Service Account Token Creator for OIDC
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --project=$PROJECT_ID \
  --role="roles/iam.serviceAccountTokenCreator" \
  --member="serviceAccount:${SA_EMAIL}"
```

## Step 4: Configure Workload Identity Federation

Set up workload identity federation to allow GitHub Actions to authenticate:

```bash
# Create workload identity pool
gcloud iam workload-identity-pools create "github-actions-pool" \
  --project=$PROJECT_ID \
  --location="global" \
  --description="Pool for GitHub Actions OIDC" \
  --display-name="GitHub Actions Pool"

# Create workload identity provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-condition="assertion.repository=='YOUR_ORG/YOUR_REPO'"

# Replace YOUR_ORG/YOUR_REPO with your actual repository (e.g., enufacas/Chained)
```

## Step 5: Grant Service Account Access

Allow the GitHub provider to impersonate the service account:

```bash
# Get the pool name
export POOL_NAME="projects/${PROJECT_ID}/locations/global/workloadIdentityPools/github-actions-pool"

# Grant workload identity user access
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/YOUR_ORG/YOUR_REPO"
```

## Step 6: Get Workload Identity Provider Name

Get the full provider name for GitHub Actions configuration:

```bash
# Get the provider resource name
gcloud iam workload-identity-pools providers describe "github-provider" \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --format="value(name)"

# Output format: projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider
```

## Step 7: Configure GitHub Repository

Add the following secrets and variables to your GitHub repository:

### Repository Secrets

1. **GCP_WORKLOAD_IDENTITY_PROVIDER**
   - Value: The full provider name from Step 6
   - Example: `projects/123456789/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider`

2. **GCP_SERVICE_ACCOUNT**
   - Value: The service account email
   - Example: `claude-a2a-coordinator@your-project.iam.gserviceaccount.com`

### Repository Variables

1. **ANTHROPIC_VERTEX_PROJECT_ID**
   - Value: Your GCP project ID
   - Example: `your-gcp-project-id`

2. **CLOUD_ML_REGION**
   - Value: The GCP region for Vertex AI
   - Example: `us-east5` (recommended for Claude)

3. **CLAUDE_USE_VERTEX** (optional)
   - Value: `true` to use Vertex AI by default
   - If not set, users can still use `vertex` flag in commands

## Step 8: Test the Configuration

### Test Locally (with gcloud)

```bash
# Authenticate with gcloud
gcloud auth application-default login

# Test the Claude API via Python
python3 << 'EOF'
from anthropic import AnthropicVertex
import os

os.environ['ANTHROPIC_VERTEX_PROJECT_ID'] = 'your-project-id'
os.environ['CLOUD_ML_REGION'] = 'us-east5'

client = AnthropicVertex(
    project_id=os.environ['ANTHROPIC_VERTEX_PROJECT_ID'],
    region=os.environ['CLOUD_ML_REGION']
)

response = client.messages.create(
    model="claude-sonnet-4@20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say 'Hello from Vertex AI!'"}]
)

print(response.content[0].text)
EOF
```

### Test via GitHub Actions

Trigger the Claude A2A coordinator workflow:

1. Go to Actions → "Claude: 🎯 A2A Coordinator"
2. Click "Run workflow"
3. Enter an issue number
4. Set `use_vertex` to `true`
5. Click "Run workflow"

Or comment on an issue:
```
@claude-a2a-coordinator vertex
```

## Supported Regions

Claude models on Vertex AI are available in these regions:

| Region | Location |
|--------|----------|
| us-east5 | Columbus, Ohio (recommended) |
| europe-west1 | Belgium |
| asia-southeast1 | Singapore |

## Model Names

When using Vertex AI, model names use a different format:

| Direct API | Vertex AI |
|------------|-----------|
| claude-sonnet-4-20250514 | claude-sonnet-4@20250514 |
| claude-3-5-sonnet-20241022 | claude-3-5-sonnet@20241022 |
| claude-3-5-haiku-20241022 | claude-3-5-haiku@20241022 |

The Claude executor automatically converts model names when using Vertex AI.

## Troubleshooting

### Error: "Permission denied" or "403"

1. Check that the service account has `roles/aiplatform.user`
2. Verify workload identity federation is configured correctly
3. Ensure the `attribute-condition` matches your repository

### Error: "Could not authenticate"

1. Verify `GCP_WORKLOAD_IDENTITY_PROVIDER` secret is correct
2. Check `GCP_SERVICE_ACCOUNT` secret matches your service account
3. Ensure `id-token: write` permission is set in workflow

### Error: "Model not found"

1. Verify Claude models are enabled in your GCP project
2. Check the region supports the model you're using
3. Ensure model name uses Vertex AI format (with `@`)

### Error: "Project not found"

1. Verify `ANTHROPIC_VERTEX_PROJECT_ID` is set correctly
2. Check that the service account belongs to the project
3. Ensure Vertex AI API is enabled

## Cost Considerations

Using Claude via Vertex AI:
- You pay through GCP billing
- Pricing may differ from direct Anthropic API
- Use GCP budget alerts to monitor costs
- Consider using `claude-3-5-haiku` for cost-sensitive tasks

## Security Best Practices

1. **Minimize permissions**: Only grant `aiplatform.user`, not admin roles
2. **Scope workload identity**: Use `attribute-condition` to restrict to your repository
3. **Rotate credentials**: Periodically review and rotate service accounts
4. **Monitor usage**: Enable GCP audit logging for Vertex AI
5. **Use private networking**: Consider VPC Service Controls for production

## Alternative: Direct Anthropic API

If you prefer to use the direct Anthropic API instead:

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Add `ANTHROPIC_API_KEY` as a repository secret
3. Don't set `CLAUDE_USE_VERTEX` or leave it as `false`

The workflow will automatically use the direct API when Vertex AI is not configured.

## Related Documentation

- [Anthropic Vertex AI Documentation](https://docs.anthropic.com/en/docs/claude-code/github-actions#using-with-google-vertex-ai)
- [GCP Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [Vertex AI Claude Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/claude)
- [GitHub OIDC with GCP](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform)

---

**Created by**: @cloud-architect  
**Last Updated**: 2025-11-29
