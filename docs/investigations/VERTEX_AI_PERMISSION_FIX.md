# Vertex AI Permission Error - Troubleshooting Guide

## Problem Encountered

**Workflow Run:** https://github.com/enufacas/Chained/actions/runs/19687918620/job/56397845838

**Error Message:**
```
Permission 'aiplatform.endpoints.predict' denied on resource 
'//aiplatform.googleapis.com/projects/923717154172/locations/us-central1/publishers/google/models/gemini-2.0-flash' 
(or it may not exist).
```

## Root Cause Analysis

The error occurs when:
1. ✅ `GOOGLE_GENAI_USE_VERTEXAI` variable is set to `true`
2. ✅ `GOOGLE_API_KEY` secret exists (passes validation)
3. ❌ The API key lacks the `aiplatform.endpoints.predict` permission

**Why This Happens:**
- The validation step only checks if the secret exists, not if it has proper permissions
- The actual error occurs when the Gemini CLI tries to use the Vertex AI API
- The API key needs specific permissions to access Vertex AI resources

## Solution Implemented

### 1. Enhanced Validation Warning

Added a warning message when using Vertex AI mode:

```yaml
echo "⚠️  Warning: Using Vertex AI mode. Ensure your API key has 'aiplatform.endpoints.predict' permission."
echo "   If you encounter permission errors, see troubleshooting guide in workflow logs."
```

This alerts users upfront about permission requirements.

### 2. Intelligent Error Detection

Added a new step that runs after Gemini CLI failures:

```yaml
- name: 'Diagnose Vertex AI Permission Errors'
  if: failure() && steps.run_gemini.conclusion == 'failure'
```

This step:
- Detects Vertex AI permission errors by parsing error output
- Provides clear, actionable solutions
- Distinguishes between different types of permission errors
- Links to comprehensive documentation

### 3. Comprehensive Documentation

Updated `docs/GEMINI_CLI_INTEGRATION.md` with:

#### Solution 1: Enable Vertex AI API for Your API Key
Step-by-step instructions for:
- Navigating to GCP Console
- Editing API key restrictions
- Enabling Vertex AI API
- Enabling billing (required for Vertex AI)
- Waiting for permission propagation

#### Solution 2: Use Service Account with IAM Roles
Enterprise-grade setup:
- Creating a service account
- Granting `Vertex AI User` role
- Generating and configuring keys
- Understanding required permissions

#### Solution 3: Switch to Google AI Studio
Simpler alternative:
- No GCP project required
- No billing required
- Generous free tier
- Easier setup

## How to Fix This Error

### Quick Fix (Recommended for Most Users)

**Switch to Google AI Studio:**

1. Get API key from https://aistudio.google.com/app/apikey
2. Go to repository: Settings → Secrets and variables → Actions
3. Delete `GOOGLE_API_KEY` secret
4. Create new secret `GEMINI_API_KEY` with your Google AI Studio key
5. Set variable `GOOGLE_GENAI_USE_VERTEXAI` to `false`
6. Re-run the workflow

### Advanced Fix (For Vertex AI Users)

**Enable Vertex AI permissions for your API key:**

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com/apis/credentials

2. **Find and edit your API key:**
   - Click on the key you stored as `GOOGLE_API_KEY`

3. **Configure API restrictions:**
   - Select "Restrict key"
   - Search for "Vertex AI API"
   - Check the box to enable it
   - Click "Save"

4. **Enable Vertex AI API for your project:**
   - https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
   - Click "Enable" if not already enabled

5. **Ensure billing is enabled:**
   - https://console.cloud.google.com/billing
   - Link a billing account to your project
   - Note: Vertex AI has a free tier, but billing must be enabled

6. **Wait 2-3 minutes for changes to propagate**

7. **Re-run the workflow**

## Files Modified

All four Gemini workflows enhanced with error handling:
- ✅ `.github/workflows/gemini-fix.yml`
- ✅ `.github/workflows/gemini-invoke.yml`
- ✅ `.github/workflows/gemini-review.yml`
- ✅ `.github/workflows/gemini-triage.yml`

Documentation updated with comprehensive troubleshooting:
- ✅ `docs/GEMINI_CLI_INTEGRATION.md`

## Benefits

### For Users
- **Clear error messages**: No more cryptic API errors
- **Multiple solutions**: Choose what works best for your setup
- **Step-by-step guidance**: Easy to follow instructions
- **Quick escape hatch**: Can switch to simpler Google AI Studio setup

### For Maintainers
- **Fewer support questions**: Self-service troubleshooting
- **Better diagnostics**: Errors are detected and categorized
- **Comprehensive docs**: All information in one place

## Testing

### Test Case 1: Vertex AI without permissions
**Before:** Generic API error, user confused
**After:** Clear permission error with 3 solution options

### Test Case 2: Google AI Studio setup
**Before:** Works fine (no change)
**After:** Still works fine, no impact

### Test Case 3: Vertex AI with proper permissions
**Before:** Works fine (no change)
**After:** Shows warning but works, no impact

## Related Resources

- **Troubleshooting Guide:** [docs/GEMINI_CLI_INTEGRATION.md](docs/GEMINI_CLI_INTEGRATION.md#error-permission-aiplatformendpointspredict-denied)
- **Vertex AI API Keys:** https://cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys
- **Google AI Studio:** https://aistudio.google.com/app/apikey
- **Original Error:** https://github.com/enufacas/Chained/actions/runs/19687918620/job/56397845838

## Summary

This fix transforms a cryptic API permission error into a clear, actionable troubleshooting experience. Users now get:

1. ⚠️ **Upfront warning** about permission requirements
2. 🔍 **Intelligent detection** of permission errors
3. 📋 **Three clear solutions** to choose from
4. 📚 **Comprehensive documentation** with all details
5. ✅ **Quick escape hatch** to simpler setup if needed

The error that was confusing and hard to debug is now self-explanatory with multiple paths to resolution.
