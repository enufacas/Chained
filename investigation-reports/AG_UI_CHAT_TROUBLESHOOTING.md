# AG-UI Frontend Chat Troubleshooting Guide

## Overview

This document tracks the troubleshooting history for the AG-UI Frontend chat functionality deployed at:
- **URL**: https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/
- **Service**: `chained-ag-ui-frontend` on Cloud Run
- **Region**: `us-central1`

## Current Status (2025-11-30)

**Status**: 🟡 **FIX IN PROGRESS** - Model updated to `gemini-2.0-flash`

### Root Cause (Identified)
The Gemini model `gemini-1.5-flash` has been **deprecated on Vertex AI** as of late November 2025. All Gemini 1.x models are no longer available via Vertex AI API, resulting in persistent 404 errors regardless of correct IAM, billing, or API configuration.

### Fix Applied
Updated model from `gemini-1.5-flash` to `gemini-2.0-flash` in all relevant files:
- `src/lib/copilotkit-config.ts`
- `src/lib/adapters/vertex-ai-adapter.ts`
- `src/app/api/debug/route.ts`

### Evidence (Before Fix)
```json
// Debug endpoint output (POST /api/debug with {"test": "full"})
{
  "vertexTest": {
    "success": false,
    "details": {
      "code": "404",
      "httpStatus": 404,
      "httpStatusText": "Not Found"
    }
  },
  "config": {
    "modelName": "gemini-1.5-flash"  // ← DEPRECATED MODEL
  }
}
```

### Live Log Evidence (Cloud Run Logs)

**Timestamp**: 2025-11-30T07:55:37Z  
**User Input**: "Vvvv" (typed in chat)  
**Request URL**:
```
https://us-central1-aiplatform.googleapis.com/v1beta/projects/cogent-tine-479302-j0/locations/us-central1/publishers/google/models/gemini-1.5-flash:streamGenerateContent
```
**Response**: `404 Not Found`  
**Error**: Model `gemini-1.5-flash` not found (deprecated)

**Full Error Log**:
```
[07:55:37.498] ERROR:
  component: "Yoga GraphQL"
  err: {
    "type": "S",
    "message": "",
    "stack": "Error at v._request..."
  }
  code: '404',
  attemptNumber: 1,
  retriesLeft: 6
```

---

## Complete Commit History

The AG-UI Frontend chat functionality has evolved through multiple PRs. Here's the complete timeline:

### Commit Timeline (Newest First)

| Commit | Date | PR | Description |
|--------|------|-----|-------------|
| `56ce20f0` | 2025-11-30 02:29 | #3428 | ❌ Reverted to `gemini-1.5-flash` (now deprecated) |
| `e5c0bbaf` | 2025-11-30 01:50 | #3425 | ❌ Changed to `gemini-2.0-flash-001` (invalid name) |
| `b9e4c17a` | 2025-11-30 01:17 | #3423 | ✅ Added custom VertexAIAdapter with `platformType: "gcp"` |
| `e5110b93` | 2025-11-30 00:36 | #3422 | Fixed ESLint errors blocking deployment |
| `1489962e` | 2025-11-30 00:08 | #3420 | Documented gcloud-mcp server requirement |
| `23a47ff1` | 2025-11-29 15:27 | #3403 | ✅ Added Vertex AI ADC support |
| `54fb821b` | 2025-11-29 13:20 | #3393 | Simplified frontend with API key debugging |
| `bc6ed862` | 2025-11-29 12:35 | #3387 | Fixed chat not displaying on interactive page |
| `935ceb5a` | 2025-11-29 11:30 | #3384 | Investigated chat functionality issues |
| `4a066e0e` | 2025-11-29 01:48 | #3360 | ✅ Initial Gemini API support + A2A Pipeline |

---

## Timeline of Issues

### Session 3 - 2025-11-30 07:45 UTC (Current)
**Issue**: Chat still fails after PR #3428 was merged
**Investigator**: Copilot
**Finding**: 
- PR #3428 changed model from `gemini-2.0-flash-001` to `gemini-1.5-flash`
- **Both models are invalid** on Vertex AI:
  - `gemini-2.0-flash-001` - Never existed on Vertex AI (wrong naming convention)
  - `gemini-1.5-flash` - Deprecated in late November 2025
- **Correct model**: `gemini-2.0-flash` (no version suffix)
- Web search confirmed Gemini 1.x models deprecated across all Vertex AI accounts

### Session 2 - 2025-11-30 06:59 UTC (PR #3428)
**Issue**: Chat broken after commit `e5c0bbaf` changed model to `gemini-2.0-flash-001`
**Investigator**: Copilot
**Finding**: 
- Identified that `gemini-2.0-flash-001` doesn't exist on Vertex AI
- Reverted to `gemini-1.5-flash` (which was working previously)
- **Problem**: Unaware that 1.5 was also being deprecated at that time
- Files changed: `copilotkit-config.ts`, `vertex-ai-adapter.ts`, `debug/route.ts`
- Added test script: `scripts/test-chat-mock.js`

### Session 1 - 2025-11-30 01:50 UTC (PR #3425)
**Issue**: Copilot attempted to update deprecated model
**Change**: Model changed from `gemini-1.5-flash` to `gemini-2.0-flash-001`
**Result**: Broke chat immediately (404 errors)
**Root Cause**: Used Google AI Studio model naming (`gemini-2.0-flash-001`) instead of Vertex AI naming (`gemini-2.0-flash`)

### Initial Setup - 2025-11-29 (PR #3360, #3403, #3423)
**What worked**:
- PR #3360: Added Gemini API support with `gemini-1.5-flash`
- PR #3403: Added Vertex AI ADC authentication support
- PR #3423: Added custom `VertexAIAdapter` with proper `platformType: "gcp"`
- Chat was working with `gemini-1.5-flash` at this point

**When it stopped working**: Late November 2025 when Google deprecated Gemini 1.x models on Vertex AI

---

## Vertex AI Model Naming Reference

### Model Name Differences by Platform

| Platform | Correct Model Name | Notes |
|----------|-------------------|-------|
| **Vertex AI (ADC)** | `gemini-2.0-flash` | No version suffix! Uses `platformType: "gcp"` |
| **Google AI Studio** | `gemini-2.0-flash-001`, `gemini-2.5-flash` | Different API, different naming |

### Currently Available Models on Vertex AI (November 2025)
- ✅ `gemini-2.0-flash` - Recommended for high-volume tasks
- ✅ `gemini-2.0-flash-lite` - Ultra-fast, cost-effective
- ✅ `gemini-2.5-pro` - Advanced reasoning
- ✅ `gemini-2.5-flash` - Best price-performance
- ❌ `gemini-1.5-flash` - **DEPRECATED**
- ❌ `gemini-1.5-pro` - **DEPRECATED**
- ❌ `gemini-2.0-flash-001` - **NEVER EXISTED ON VERTEX AI**

---

## Files That Control Model Configuration

| File | Purpose | Model Variable |
|------|---------|----------------|
| `src/lib/copilotkit-config.ts` | Creates service adapter for CopilotKit | `model: "gemini-X.X-flash"` |
| `src/lib/adapters/vertex-ai-adapter.ts` | Custom Vertex AI adapter | Default in constructor |
| `src/app/api/debug/route.ts` | Debug/test endpoint | `modelName` variable |

### Required Change
Update all files from:
```typescript
model: "gemini-1.5-flash"
```
To:
```typescript
model: "gemini-2.0-flash"
```

---

## Debug Endpoints

### GET /api/debug
Returns environment configuration without testing.

```bash
curl -s "https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug"
```

### POST /api/debug
Run specific tests:

```bash
# Full diagnostic
curl -s -X POST "https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug" \
  -H "Content-Type: application/json" \
  -d '{"test": "full"}'

# Auth only
curl -s -X POST "https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug" \
  -H "Content-Type: application/json" \
  -d '{"test": "auth"}'

# Vertex AI only
curl -s -X POST "https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug" \
  -H "Content-Type: application/json" \
  -d '{"test": "vertex"}'
```

### GET /api/copilotkit
Returns CopilotKit provider status:

```bash
curl -s "https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/copilotkit"
```

---

## Cloud Run Log Commands

### Get Recent Errors
```bash
gcloud logging read 'resource.type="cloud_run_revision" resource.labels.service_name="chained-ag-ui-frontend" severity>=ERROR' --limit=10 --format='table(timestamp,textPayload)'
```

### Get Application Debug Logs
```bash
gcloud logging read 'resource.type="cloud_run_revision" resource.labels.service_name="chained-ag-ui-frontend" textPayload:("Debug API" OR "VertexAIAdapter" OR "CopilotKit")' --limit=20 --format='table(timestamp,textPayload)'
```

### Get Vertex AI Request Details
```bash
gcloud logging read 'resource.type="cloud_run_revision" resource.labels.service_name="chained-ag-ui-frontend" textPayload:"aiplatform.googleapis.com"' --limit=10 --format='table(timestamp,textPayload)'
```

### Get Logs Around a Specific Time
```bash
gcloud logging read 'resource.type="cloud_run_revision" resource.labels.service_name="chained-ag-ui-frontend" timestamp>="2025-11-30T07:55:00Z" timestamp<="2025-11-30T07:56:00Z"' --limit=50 --format='table(timestamp,textPayload)'
```

---

## Interpreting Error Codes

| HTTP Code | Meaning | Likely Cause |
|-----------|---------|--------------|
| **404** | Model not found | Invalid or deprecated model name |
| **403** | Permission denied | Missing "Vertex AI User" role on service account |
| **401** | Unauthorized | ADC not configured or expired credentials |
| **503** | Service unavailable | Vertex AI service issue or quota exceeded |

### 404 Error Troubleshooting
1. Check model name is valid (see table above)
2. Verify model is available in your region
3. Check Google's model deprecation announcements

### 403 Error Troubleshooting
1. Verify service account has `roles/aiplatform.user`
2. Check project has Vertex AI API enabled
3. Verify billing is active

---

## Deployment Workflow

After code changes:
1. Commit and push to branch
2. Create PR targeting `main`
3. Merge PR
4. Cloud Run automatically redeploys from `main`
5. Verify with debug endpoints

### Checking Current Deployment
```bash
# Check which revision is running
curl -s "https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug" | jq '.environment.K_REVISION'

# Example output: "chained-ag-ui-frontend-00029-7s7"
```

---

## Related PRs and Issues

| PR | Date | Description | Result |
|-----|------|-------------|--------|
| #3360 | 2025-11-29 01:48 | Initial Gemini API support + A2A Pipeline | ✅ Working |
| #3384 | 2025-11-29 11:30 | Investigate chat functionality issues | ✅ Diagnostic |
| #3387 | 2025-11-29 12:35 | Fix chat not displaying on interactive page | ✅ Fixed |
| #3393 | 2025-11-29 13:20 | Simplify frontend with API key debugging | ✅ Improved |
| #3403 | 2025-11-29 15:27 | Vertex AI ADC authentication support | ✅ Working |
| #3420 | 2025-11-30 00:08 | Document gcloud-mcp server requirement | ✅ Docs |
| #3422 | 2025-11-30 00:36 | Fix ESLint errors blocking deployment | ✅ Fixed |
| #3423 | 2025-11-30 01:17 | Custom VertexAIAdapter with platformType | ✅ Working |
| #3425 | 2025-11-30 01:50 | Changed to `gemini-2.0-flash-001` | ❌ Broke chat (invalid model name) |
| #3428 | 2025-11-30 02:29 | Reverted to `gemini-1.5-flash` | ❌ Still broken (deprecated model) |
| #TBD | 2025-11-30 | Update to `gemini-2.0-flash` | 🔄 In progress |

---

## Key Learnings

1. **Vertex AI and Google AI Studio use different model names** - Don't assume model names are interchangeable
2. **Google deprecates models without much notice** - Check model availability before deploying
3. **Debug endpoints are essential** - The `/api/debug` endpoint saved significant troubleshooting time
4. **Document across sessions** - This document helps future Copilot sessions understand history

---

## How to Use This Document

When troubleshooting AG-UI chat issues:

1. **First**: Run `curl -s "https://chained-ag-ui-frontend-sguacxy5gq-uc.a.run.app/api/debug"` to check current config
2. **Then**: Run `POST /api/debug` with `{"test": "full"}` to see what's failing
3. **Check**: Compare the `modelName` in config against the "Currently Available Models" table above
4. **Reference**: Check the Timeline section for similar past issues

---

## Contact

For questions about this document or the AG-UI frontend:
- Repository: https://github.com/enufacas/Chained
- Frontend Code: `infrastructure/docker/ag-ui-frontend/`

---

*Last Updated: 2025-11-30 by Copilot*
