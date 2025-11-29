# AG-UI Frontend Troubleshooting Guide

> **Running Document** - A comprehensive troubleshooting guide for the AG-UI Frontend service, including common issues, diagnostic commands, and the history of fixes.

**URL:** https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/  
**Last Updated:** 2025-11-29

---

## Table of Contents

1. [Quick Status Check](#quick-status-check)
2. [Current Configuration](#current-configuration)
3. [Understanding the Logs](#understanding-the-logs)
4. [Common Issues & Solutions](#common-issues--solutions)
5. [Diagnostic Commands](#diagnostic-commands)
6. [Authentication Modes](#authentication-modes)
7. [Change History](#change-history)
8. [Architecture Overview](#architecture-overview)
9. [Related Files](#related-files)

---

## Quick Status Check

### API Health Check

```bash
# Check the API status endpoint
curl -s https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/copilotkit | jq
```

**Healthy Response (Vertex AI mode):**
```json
{
  "provider": "vertex-ai",
  "model": "gemini-1.5-flash",
  "available": true,
  "authMode": "adc",
  "debug": {
    "timestamp": "2025-11-29T20:48:01.115Z",
    "hasGeminiApiKey": false,
    "hasOpenAIApiKey": false,
    "useVertexAI": true,
    "geminiKeyPrefix": null,
    "openaiKeyPrefix": null,
    "nodeEnv": "production"
  }
}
```

### What to Look For

| Field | Expected Value | Meaning |
|-------|---------------|---------|
| `provider` | `vertex-ai`, `gemini`, or `openai` | Which LLM provider is configured |
| `available` | `true` | LLM is ready to handle requests |
| `authMode` | `adc` (Vertex AI) or `api-key` | Authentication method being used |
| `useVertexAI` | `true` on Cloud Run | Using service account credentials |

---

## Current Configuration

### Environment Variables

| Variable | Purpose | Priority |
|----------|---------|----------|
| `USE_VERTEX_AI=true` | Enable Vertex AI with ADC (Application Default Credentials) | 1st (Cloud Run default) |
| `GOOGLE_GENAI_USE_VERTEXAI=true` | Alternative for enabling Vertex AI | 1st |
| `GEMINI_API_KEY` | Google AI Studio API key (starts with `AIza...`) | 2nd |
| `OPENAI_API_KEY` | OpenAI fallback | 3rd |

### Provider Priority

1. **Vertex AI (Cloud Run)** - If `USE_VERTEX_AI=true`, uses Application Default Credentials from the service account
2. **Google AI Studio** - If `GEMINI_API_KEY` is set, uses API key authentication
3. **OpenAI** - If only `OPENAI_API_KEY` is set, uses OpenAI

---

## Understanding the Logs

### Startup Logs (Normal)

```
[timestamp] [CopilotKit Config] Initializing CopilotKit configuration {
  "useVertexAI": true,
  "hasGeminiApiKey": false,
  "hasOriginalGoogleApiKey": false,
  "hasOpenAIApiKey": false,
  "useGemini": true,
  "useOpenAI": false,
  "nodeEnv": "production"
}
[timestamp] [CopilotKit Config] Using Vertex AI with Application Default Credentials (ADC)
```

### API Status Check Logs

```
[timestamp] Starting API status check...
[timestamp] Checking /api/copilotkit (GET)...
[timestamp] GET response: HTTP 200
[timestamp] Provider info: {"provider":"vertex-ai","model":"gemini-1.5-flash","available":true,...}
[timestamp] ✅ Using vertex-ai (gemini-1.5-flash)
```

### Chat Request Logs (Normal)

```
[timestamp] [CopilotKit API] POST request received
[timestamp] [CopilotKit API] Authentication check { hasGeminiAuth: true, hasOpenAIKey: false, ... }
[timestamp] [CopilotKit API] Creating service adapter...
[timestamp] [CopilotKit Config] Creating GoogleGenerativeAIAdapter { useVertexAI: true, hasGeminiApiKey: false }
[timestamp] [CopilotKit Config] Cleared GOOGLE_API_KEY to enable ADC for Vertex AI
[timestamp] [CopilotKit Config] GoogleGenerativeAIAdapter created successfully
[timestamp] [CopilotKit API] Service adapter created successfully
[timestamp] [CopilotKit API] Handling request...
[timestamp] [CopilotKit API] Request handled successfully { status: 200 }
```

### Error Logs (Common Issues)

**No Authentication Configured:**
```
[timestamp] [CopilotKit Config] WARNING: No LLM authentication configured. Set USE_VERTEX_AI=true (for Cloud Run), GEMINI_API_KEY, or OPENAI_API_KEY.
[timestamp] [CopilotKit API] ERROR: No LLM authentication configured
```

**Vertex AI Permission Error:**
```
[timestamp] [CopilotKit API] ERROR in request handling {
  "message": "Error: Permission denied for resource...",
  "stack": "..."
}
```

---

## Common Issues & Solutions

### Issue 1: Chat Shows "..." Indefinitely (No Response)

**Symptoms:**
- User sends a message
- Shows "..." loading indicator
- No response ever appears

**Possible Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| No LLM authentication | Check `/api/copilotkit` returns `available: true` |
| Vertex AI permissions | Ensure service account has `Vertex AI User` role |
| OAuth2 vs API key mismatch | Previously fixed in PR #3403 - if reverted, ensure using `GoogleGenerativeAIAdapter` with ADC |
| Network timeout | Check Cloud Run logs for timeout errors |

**Diagnostic Steps:**
```bash
# 1. Check API status
curl -s https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/copilotkit | jq

# 2. Check Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-ag-ui-frontend" --limit 50 --format="table(timestamp, jsonPayload.message)"
```

### Issue 2: 503 Error - No LLM Authentication

**Symptoms:**
- Chat returns 503 error
- Status shows `provider: "none"` and `available: false`

**Solution:**
1. Check that `USE_VERTEX_AI=true` is set in Cloud Run environment
2. Or provide `GEMINI_API_KEY` for Google AI Studio
3. Redeploy if environment variables changed

```bash
# Verify environment variables
gcloud run services describe chained-ag-ui-frontend --region us-central1 --format='yaml(spec.template.spec.containers.env)'
```

### Issue 3: 401 Unauthorized - API Keys Not Supported

**Error Message:**
```
[GoogleGenerativeAI Error]: API keys are not supported by this API. 
Expected OAuth2 access token or other authentication credentials that assert a principal.
```

**Cause:** Using `GOOGLE_API_KEY` or `GEMINI_API_KEY` when Vertex AI mode expects OAuth2 credentials.

**Solution:** This was the ROOT CAUSE fixed in PR #3403. The solution:
- When `USE_VERTEX_AI=true`, the code now CLEARS `GOOGLE_API_KEY` to force ADC
- ADC automatically uses the Cloud Run service account's OAuth2 tokens
- No API key needed when running on Cloud Run

### Issue 4: A2A Agents Not Available

**Symptoms:**
- Chat works for basic queries
- "⚠️ A2A agents not available" message in UI
- A2A orchestration features disabled

**Solution:**
1. Check if A2A backend services are deployed:
```bash
gcloud run services list --region us-central1 | grep -E "academic-research|google-trends|blog-writer|adk-api-server"
```

2. Verify DNS resolution:
```bash
curl -s https://chained-academic-research-sguacxy5gq-uc.a.run.app/health
```

3. Check IAM permissions for service-to-service calls

### Issue 5: "Unable to detect a Project Id" Error (NEW - 2025-11-29)

**Symptoms:**
- API status shows healthy (`available: true`, `authMode: adc`)
- User sends message, gets error popup:
  ```
  Copilot Cloud Error: INTERNAL_SERVER_ERROR
  Unable to detect a Project Id in the current environment.
  ```
- No response appears in chat

**Screenshot:**
![Project ID Error](https://github.com/user-attachments/assets/c2d74d62-d631-4de5-94d2-c0ff283075fb)

**Root Cause:**
When using Vertex AI with ADC, the `@langchain/google-gauth` library requires a Google Cloud Project ID to be set. On Cloud Run, this is usually auto-detected from the environment, but may fail if:
1. The service account doesn't have proper metadata access
2. `GOOGLE_CLOUD_PROJECT` environment variable is not set
3. The Cloud Run instance metadata service is not accessible

**Solution:**
1. **Set GOOGLE_CLOUD_PROJECT explicitly:**
   ```bash
   gcloud run services update chained-ag-ui-frontend \
     --update-env-vars GOOGLE_CLOUD_PROJECT=your-project-id \
     --region us-central1
   ```

2. **Verify the project ID is set:**
   ```bash
   gcloud run services describe chained-ag-ui-frontend \
     --region us-central1 \
     --format='yaml(spec.template.spec.containers[0].env)' | grep GOOGLE_CLOUD_PROJECT
   ```

3. **Alternative: Use GEMINI_API_KEY instead of Vertex AI:**
   If you have a Google AI Studio API key, you can use that instead:
   ```bash
   gcloud run services update chained-ag-ui-frontend \
     --update-env-vars GEMINI_API_KEY=AIza... \
     --remove-env-vars USE_VERTEX_AI \
     --region us-central1
   ```

**Note:** This error only displays during local development but the same underlying issue can cause silent failures in production.

---

## Diagnostic Commands

### Cloud Run Service Status

```bash
# List all Chained services
gcloud run services list --region us-central1 --filter="metadata.name~chained"

# Get service details
gcloud run services describe chained-ag-ui-frontend --region us-central1

# Get service URL
gcloud run services describe chained-ag-ui-frontend --region us-central1 --format='value(status.url)'
```

### View Logs

```bash
# Recent logs (last 50)
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-ag-ui-frontend" --limit 50

# Filtered for errors
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-ag-ui-frontend AND severity>=ERROR" --limit 20

# Specific time range
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-ag-ui-frontend AND timestamp>=\"2025-11-29T20:00:00Z\"" --limit 100
```

### Check Environment Variables

```bash
# View current env vars
gcloud run services describe chained-ag-ui-frontend --region us-central1 --format='yaml(spec.template.spec.containers[0].env)'

# Update env var
gcloud run services update chained-ag-ui-frontend \
  --update-env-vars USE_VERTEX_AI=true \
  --region us-central1
```

### Health Checks

```bash
# API status
curl -s https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/copilotkit | jq

# Test chat endpoint (will fail without auth)
curl -X POST https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/copilotkit \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"hello"}]}'
```

---

## Authentication Modes

### Mode 1: Vertex AI with ADC (Recommended for Cloud Run)

**Configuration:**
- Set `USE_VERTEX_AI=true` or `GOOGLE_GENAI_USE_VERTEXAI=true`
- No API key needed

**How It Works:**
1. `GoogleGenerativeAIAdapter` internally uses `@langchain/google-gauth`
2. When `USE_VERTEX_AI=true`, we clear `GOOGLE_API_KEY` from process.env
3. `@langchain/google-gauth` then uses Application Default Credentials (ADC)
4. ADC on Cloud Run automatically gets OAuth2 tokens from the service account

**Requirements:**
- Cloud Run service account needs `Vertex AI User` role
- `aiplatform.googleapis.com` API must be enabled

### Mode 2: Google AI Studio (API Key)

**Configuration:**
- Set `GEMINI_API_KEY=AIza...` (Google AI Studio API key)
- Don't set `USE_VERTEX_AI`

**How It Works:**
1. Code copies `GEMINI_API_KEY` to `GOOGLE_API_KEY`
2. `@langchain/google-gauth` reads `GOOGLE_API_KEY` from environment
3. Simple API key authentication with Google AI Studio

### Mode 3: OpenAI (Fallback)

**Configuration:**
- Set `OPENAI_API_KEY=sk-...`
- Don't set `GEMINI_API_KEY` or `USE_VERTEX_AI`

**How It Works:**
- Uses `OpenAIAdapter` with standard OpenAI API
- Falls back when no Gemini authentication available

---

## Change History

### 2025-11-29

| PR | Issue | Change | Impact |
|----|-------|--------|--------|
| #3403 | Chat not responding | Added Vertex AI ADC support; clear `GOOGLE_API_KEY` when using ADC | **FIXED** chat indefinitely showing "..." |
| #3401 | Missing API key | Pass `google_api_key_secret` to Terraform | API key available in Cloud Run |
| #3396 | Terraform config | Add `GOOGLE_API_KEY` env var to AG-UI Frontend | Infrastructure fix |
| #3393 | UI consolidation | Simplified UI with enhanced logging | Better debugging |
| #3387 | Chat not displaying | Parallel API health checks, removed blocking state | Chat shows immediately |
| #3384 | Investigation | Root cause analysis and documentation | Identified 3 issues |

### Previous Fixes

- **PR #3366**: Terraform 409 conflict, Secret Manager configuration
- **PR #3360**: Added Gemini API support for CopilotKit
- **PR #3359**: Fixed 403 error by adding IAM member resources

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AG-UI Frontend (Next.js)                     │
│                                                                 │
│  ┌─────────────────────┐    ┌───────────────────────────────┐  │
│  │   Main Page (/)     │    │   API Routes                  │  │
│  │   - Dashboard       │    │   - /api/copilotkit (chat)    │  │
│  │   - Status panel    │    │   - /api/copilotkit-a2a       │  │
│  └─────────────────────┘    └───────────────────────────────┘  │
│                                          │                      │
│  ┌─────────────────────┐                 │                      │
│  │   copilotkit-config │◄────────────────┘                      │
│  │   - createAdapter() │                                        │
│  │   - getLLMInfo()    │                                        │
│  └─────────────────────┘                                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                  ┌─────────────────────────────┐
                  │   @copilotkit/runtime       │
                  │   GoogleGenerativeAIAdapter │
                  └─────────────┬───────────────┘
                                │
                                ▼
                  ┌─────────────────────────────┐
                  │   @langchain/google-gauth   │
                  │   - Reads GOOGLE_API_KEY    │
                  │   - Falls back to ADC       │
                  └─────────────┬───────────────┘
                                │
          ┌─────────────────────┴─────────────────────┐
          │                                           │
          ▼                                           ▼
┌───────────────────────┐               ┌───────────────────────┐
│  Vertex AI (ADC)      │               │  Google AI Studio     │
│  - OAuth2 tokens      │               │  - API key auth       │
│  - Service account    │               │  - AIza... format     │
└───────────────────────┘               └───────────────────────┘
```

---

## Related Files

### Frontend Code

| File | Purpose |
|------|---------|
| `infrastructure/docker/ag-ui-frontend/src/lib/copilotkit-config.ts` | LLM adapter configuration |
| `infrastructure/docker/ag-ui-frontend/src/app/api/copilotkit/route.ts` | Chat API endpoint |
| `infrastructure/docker/ag-ui-frontend/src/app/api/copilotkit-a2a/route.ts` | A2A API endpoint |
| `infrastructure/docker/ag-ui-frontend/src/app/page.tsx` | Main page |

### Infrastructure

| File | Purpose |
|------|---------|
| `infrastructure/terraform/adk-agents.tf` | Cloud Run service definitions |
| `infrastructure/terraform/variables.tf` | Terraform variables including secrets |
| `.github/workflows/deploy-gcp-infrastructure.yml` | Deployment workflow |

### Documentation

| File | Purpose |
|------|---------|
| `docs/investigations/AG_UI_CHAT_INVESTIGATION_2025-11-29.md` | Initial investigation |
| `docs/AG_UI_TROUBLESHOOTING_GUIDE.md` | This document |
| `infrastructure/docker/ag-ui-frontend/README.md` | Frontend README |

---

## Quick Reference Commands

```bash
# Check status
curl -s https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/copilotkit | jq

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chained-ag-ui-frontend" --limit 20 --format="table(timestamp, jsonPayload.message)"

# Check env vars
gcloud run services describe chained-ag-ui-frontend --region us-central1 --format='yaml(spec.template.spec.containers[0].env)'

# Redeploy with new env
gcloud run services update chained-ag-ui-frontend \
  --update-env-vars USE_VERTEX_AI=true \
  --region us-central1
```

---

## Notes for Future Troubleshooting

1. **Always check `/api/copilotkit` first** - It shows the current provider status
2. **Look at the `authMode` field** - Should be `adc` on Cloud Run
3. **Check if `useVertexAI` is true** - Required for Cloud Run without API keys
4. **Service account needs Vertex AI permissions** - `roles/aiplatform.user`
5. **The main page uses sample data** - Only `/interactive` connects to real LLM

---

*Last Updated: 2025-11-29 by @investigate-champion*
*Based on investigation of PR #3403 and related fixes*
