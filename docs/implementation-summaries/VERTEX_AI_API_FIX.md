# Vertex AI API Fix - Implementation Summary

**Date**: 2025-12-03  
**Issue**: Cloud Run services failing with "Invalid resource requested: 'projects/***' does not exist"  
**GitHub Actions Run**: [#19879294311](https://github.com/enufacas/Chained/actions/runs/19879294311)

## Problem Description

Multiple Cloud Run services (blog-writer, code-reviewer, data-analyst, image-generator, error-observer, log-consumer) were failing to start with the error:

```
Error waiting for Updating Service: Error code 9, message: The user-provided container failed the configured startup probe checks.
```

The Cloud Run logs showed:
```
Invalid resource requested: "projects/***" does not exist.
```

## Root Cause Analysis

The ADK agents were configured to use Google's Vertex AI for Gemini model access:

1. **Configuration Present**: All agents had `USE_VERTEX_AI=true` environment variable set
2. **Permissions Present**: Service account `chained-adk-agents` had `roles/aiplatform.user` role
3. **API Missing**: The Vertex AI API (`aiplatform.googleapis.com`) was **NOT** enabled in the GCP project

When the containers started, they attempted to authenticate with Vertex AI using Application Default Credentials (ADC), but the API wasn't enabled, causing authentication to fail with "project does not exist" error.

## Solution

Added `aiplatform.googleapis.com` to the list of required GCP APIs in the Terraform configuration:

**File**: `infrastructure/terraform/main.tf`

```terraform
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "pubsub.googleapis.com",
    "firestore.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",  # Required for Vertex AI (Gemini models) <-- ADDED
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
```

## Impact

### Services Fixed
- `chained-blog-writer`
- `chained-code-reviewer`
- `chained-data-analyst`
- `chained-image-generator`
- `chained-error-observer`
- `chained-log-consumer`
- `chained-academic-research`
- `chained-google-trends`

### Deployment Changes
Once the Terraform applies:
1. Vertex AI API will be enabled in the GCP project
2. ADK agents can successfully authenticate with Vertex AI using ADC
3. Cloud Run containers will pass startup probe checks
4. Services will become available

## Why This Happened

The Vertex AI configuration (`USE_VERTEX_AI=true`) and IAM permissions (`roles/aiplatform.user`) were added to the ADK agents, but the corresponding API enablement was missed in the Terraform configuration. This is a common oversight when adding new GCP service integrations.

## Prevention

When adding new GCP service integrations in the future:

1. ✅ Set environment variables (e.g., `USE_VERTEX_AI=true`)
2. ✅ Grant IAM permissions (e.g., `roles/aiplatform.user`)
3. ✅ **Enable the API** (e.g., `aiplatform.googleapis.com`) ← Don't forget this step!

## Verification

To verify the fix is working:

1. Check that Terraform applies successfully without errors
2. Verify Cloud Run services reach "ready" state
3. Check service health endpoints return HTTP 200
4. Test agent functionality (e.g., call `/a2a/tasks` endpoint)

## Related Files

- `infrastructure/terraform/main.tf` - API enablement configuration
- `infrastructure/terraform/adk-agents.tf` - Agent service definitions with Vertex AI config
- `.github/workflows/deploy-gcp-infrastructure.yml` - Deployment workflow

## References

- [Vertex AI API Documentation](https://cloud.google.com/vertex-ai/docs/reference)
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
