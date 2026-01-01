# Gemini API Key Fix - Implementation Summary

## Problem Description

The Gemini workflows were failing with this error:

```
API keys are not supported by this API. Expected OAuth2 access token or other authentication credentials that assert a principal.
```

**Root Cause**: The user created an API key from Google Cloud Platform Console (`https://console.cloud.google.com/marketplace/product/google/aiplatform.googleapis.com`), but the workflows were configured to use the Google AI Studio API (`generativelanguage.googleapis.com`), which requires a different type of API key.

## Solution Implemented

The workflows have been updated to support **both authentication methods**:

1. **Google AI Studio API Key** (original method)
2. **Vertex AI API Key** (NEW - what the user has)

## How to Use Your GCP Vertex AI API Key

Follow these steps to configure the repository to use your existing Vertex AI API key:

### Step 1: Add Your API Key as a Secret

1. Go to your repository's **Settings**
2. Navigate to **Secrets and variables > Actions**
3. Click **New repository secret**
4. Enter:
   - **Name**: `GOOGLE_API_KEY`
   - **Secret**: Paste your Vertex AI API key from GCP Console
5. Click **Add secret**

### Step 2: Enable Vertex AI Mode

1. While still in **Settings > Secrets and variables > Actions**
2. Click the **Variables** tab
3. Click **New repository variable**
4. Enter:
   - **Name**: `GOOGLE_GENAI_USE_VERTEXAI`
   - **Value**: `true`
5. Click **Add variable**

### Step 3: Test the Configuration

1. Go to any issue in your repository
2. Add a comment: `@gemini-cli help`
3. The workflow should trigger and respond without authentication errors

If it still fails, check the workflow logs for errors.

## What Changed

### Workflows Updated

All four Gemini workflows have been updated:

- ✅ `.github/workflows/gemini-fix.yml`
- ✅ `.github/workflows/gemini-invoke.yml`
- ✅ `.github/workflows/gemini-review.yml`
- ✅ `.github/workflows/gemini-triage.yml`

Each now includes:

```yaml
with:
  gemini_api_key: '${{ secrets.GEMINI_API_KEY }}'        # Google AI Studio (if set)
  google_api_key: '${{ secrets.GOOGLE_API_KEY }}'         # Vertex AI (if set)
  use_vertex_ai: '${{ vars.GOOGLE_GENAI_USE_VERTEXAI || false }}'
```

### Documentation Updated

- ✅ `docs/GEMINI_CLI_INTEGRATION.md` - Comprehensive guide with both authentication methods
- ✅ `README.md` - Quick setup instructions updated

## Authentication Decision Logic

The workflows now follow this logic:

1. **If** `GOOGLE_API_KEY` secret exists **AND** `GOOGLE_GENAI_USE_VERTEXAI=true` variable is set
   - → Use Vertex AI authentication (`aiplatform.googleapis.com`)

2. **Else If** `GEMINI_API_KEY` secret exists
   - → Use Google AI Studio authentication (`generativelanguage.googleapis.com`)

3. **Else**
   - → Fail with authentication error

## Benefits of This Approach

✅ **Backward Compatible**: Existing users with `GEMINI_API_KEY` continue to work  
✅ **Flexible**: Users can choose their preferred authentication method  
✅ **GCP Integration**: Vertex AI users can leverage their existing GCP projects  
✅ **Clear Documentation**: Both methods are clearly documented with setup steps  
✅ **Troubleshooting**: Common errors are documented with solutions

## Alternative: Switch to Google AI Studio

If you prefer the simpler setup, you can alternatively:

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Store it as `GEMINI_API_KEY` secret (instead of `GOOGLE_API_KEY`)
4. Do NOT set the `GOOGLE_GENAI_USE_VERTEXAI` variable

This method has:
- ✅ Simpler setup (no variable needed)
- ✅ Generous free tier
- ❌ No GCP project integration

## Testing Checklist

After configuration, verify:

- [ ] Secret `GOOGLE_API_KEY` is set
- [ ] Variable `GOOGLE_GENAI_USE_VERTEXAI` is set to `true`
- [ ] Test with `@gemini-cli help` on an issue
- [ ] Check workflow logs show no authentication errors
- [ ] Gemini responds successfully

## Troubleshooting

### Still Getting Authentication Errors?

1. **Check the secret name**: Must be exactly `GOOGLE_API_KEY` (not `GEMINI_API_KEY`)
2. **Check the variable name**: Must be exactly `GOOGLE_GENAI_USE_VERTEXAI`
3. **Check the variable value**: Must be `true` (lowercase)
4. **Verify your API key**: Ensure it's from GCP Console Vertex AI, not another service

### Need Help?

See the comprehensive troubleshooting section in `docs/GEMINI_CLI_INTEGRATION.md`

## References

- [Vertex AI API Keys Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys)
- [Google AI Studio](https://aistudio.google.com/app/apikey)
- [run-gemini-cli Action Documentation](https://github.com/google-github-actions/run-gemini-cli)
- [Gemini CLI Documentation](https://github.com/google-gemini/gemini-cli)

---

**Implementation Date**: 2025-11-25  
**PR**: [Link will be added when PR is created]  
**Issue**: [Original issue reference]
