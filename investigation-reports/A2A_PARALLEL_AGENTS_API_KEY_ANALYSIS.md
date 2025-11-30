# A2A Parallel Agents: API Key and Model Configuration Analysis

**Investigation Date**: 2025-11-30  
**Investigator**: @investigate-champion  
**Issue Context**: Understanding how the A2A parallel agents workflow handles GOOGLE_API_KEY, GEMINI_API_KEY, and model selection

## Executive Summary

The A2A parallel agents workflow (`a2a-parallel-agents.yml`) uses two different code paths for AI generation:

1. **GitHub Actions** (run-gemini-cli action) - Uses **Google AI Studio mode** with `GEMINI_API_KEY` by default
2. **Cloud Run ADK Agents** - Uses **Vertex AI mode** with Application Default Credentials (ADC)

The original "gemini-3-pro-preview" model name error only occurred in Cloud Run (Vertex AI) because:
- The workflow uses `GEMINI_API_KEY` in **Google AI Studio mode** where the model name is handled differently
- Cloud Run sets `USE_VERTEX_AI=true` which uses **Vertex AI mode** where the model name must be a valid Vertex AI model

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    A2A PARALLEL AGENTS WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GitHub Actions Runner                    GCP Cloud Run                     │
│  ┌───────────────────────┐               ┌────────────────────────────────┐ │
│  │ run-gemini-cli action │               │ ADK Agents (Python)            │ │
│  │                       │               │                                │ │
│  │ • GEMINI_API_KEY ✓    │               │ • USE_VERTEX_AI=true           │ │
│  │ • GOOGLE_API_KEY      │               │ • GOOGLE_CLOUD_PROJECT         │ │
│  │ • USE_VERTEX_AI=false │               │ • Service Account ADC          │ │
│  │                       │               │                                │ │
│  │ Mode: Google AI Studio│               │ Mode: Vertex AI                │ │
│  │ Model: Any name works │               │ Model: Must be valid VA name   │ │
│  │ (gemini-3-pro-preview)│               │ (gemini-2.0-flash)             │ │
│  └───────────────────────┘               └────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Two Authentication Modes

### 1. Google AI Studio Mode (GitHub Actions)

Used by: `google-github-actions/run-gemini-cli` in workflows

**Configuration (from actual workflow):**
```yaml
# Note: The '' is YAML's escape sequence for single quotes within single-quoted strings
with:
  gemini_api_key: '${{ secrets.GEMINI_API_KEY }}'
  google_api_key: '${{ secrets.GOOGLE_API_KEY }}'
  use_vertex_ai: '${{ vars.GOOGLE_GENAI_USE_VERTEXAI || ''false'' }}'  # Default: false
  gemini_model: '${{ vars.GEMINI_MODEL || ''gemini-3-pro-preview'' }}'
```

**Key Points:**
- Default mode when `USE_VERTEX_AI` is not set or `false`
- Uses `GEMINI_API_KEY` (from Google AI Studio at aistudio.google.com)
- Calls `generativelanguage.googleapis.com` endpoint
- Model names are more flexible - preview/experimental names work
- Simpler setup, good for development

### 2. Vertex AI Mode (Cloud Run)

Used by: ADK Agents deployed to Cloud Run

**Configuration (terraform):**
```hcl
env {
  name  = "USE_VERTEX_AI"
  value = "true"  # Explicitly enabled for production
}
env {
  name  = "GOOGLE_CLOUD_PROJECT"
  value = var.project_id
}
# Uses service account's Application Default Credentials (ADC)
```

**Key Points:**
- Enabled by setting `USE_VERTEX_AI=true`
- Uses Application Default Credentials (ADC) from service account
- Calls `aiplatform.googleapis.com` endpoint
- Model names MUST be valid Vertex AI model names
- Recommended for production on GCP

## Why the Model Name Error Only Affected Cloud Run

### Root Cause Analysis

1. **GitHub Actions workflow** uses `GEMINI_API_KEY` with Google AI Studio mode:
   - The `run-gemini-cli` action defaults to `use_vertex_ai: false`
   - Model name "gemini-3-pro-preview" passes through to Google AI Studio
   - Google AI Studio is more permissive with model name handling

2. **Cloud Run ADK Agents** use Vertex AI mode:
   - Terraform sets `USE_VERTEX_AI=true` for all Cloud Run services
   - `gemini_client.py` selects Vertex AI mode based on this environment variable
   - Vertex AI requires valid model names like "gemini-2.0-flash"
   - The old default "gemini-3-pro-preview" caused 404 errors

### The Fix

In `infrastructure/docker/adk-agents/shared/gemini_client.py`:

```python
# Before (invalid for Vertex AI)
DEFAULT_VERTEX_MODEL = "gemini-3-pro-preview"

# After (valid Vertex AI model)
DEFAULT_VERTEX_MODEL = "gemini-2.0-flash"
```

## gemini_client.py Mode Selection Logic

```python
def get_active_mode() -> str:
    """Determine which Gemini mode to use."""
    # If USE_VERTEX_AI is explicitly set, prefer Vertex AI
    if USE_VERTEX_AI:
        if VERTEX_AVAILABLE and GOOGLE_CLOUD_PROJECT:
            return "vertex"
    
    # Check if Google AI Studio is available with API key
    if GENAI_AVAILABLE and (GEMINI_API_KEY or GOOGLE_API_KEY):
        return "genai"
    
    # Check Vertex AI as alternative
    if VERTEX_AVAILABLE and GOOGLE_CLOUD_PROJECT:
        return "vertex"
    
    return "none"
```

## Configuration Matrix

| Component | USE_VERTEX_AI | API Key | Mode | Model Default |
|-----------|---------------|---------|------|---------------|
| GitHub Actions Workflow | false | GEMINI_API_KEY | Google AI Studio | gemini-3-pro-preview |
| Cloud Run (Academic Research) | true | ADC | Vertex AI | gemini-2.0-flash |
| Cloud Run (Blog Writer) | true | ADC | Vertex AI | gemini-2.0-flash |
| Cloud Run (Google Trends) | true | ADC | Vertex AI | gemini-2.0-flash |
| AG-UI Frontend | true | ADC | Vertex AI | gemini-2.0-flash |

## GOOGLE_API_KEY vs GEMINI_API_KEY

| Key Type | Source | When to Use | Notes |
|----------|--------|-------------|-------|
| `GEMINI_API_KEY` | Google AI Studio | GitHub Actions, Development | Free tier available |
| `GOOGLE_API_KEY` | Google Cloud Console | Vertex AI with API key | Requires billing |
| ADC (Service Account) | Cloud Run | Production on GCP | Most secure, recommended |

## Recommendations

### For GitHub Actions Workflows

1. **Keep using GEMINI_API_KEY** for Google AI Studio mode - it works well for CI/CD
2. **Consider setting `GEMINI_MODEL` repository variable** to a stable model name
3. If you want to use Vertex AI in workflows:
   - Set `GOOGLE_GENAI_USE_VERTEXAI` variable to `true`
   - Provide `GOOGLE_API_KEY` with appropriate permissions
   - Use valid Vertex AI model names

### For Cloud Run (ADK Agents)

1. **Continue using Vertex AI mode** - it's the recommended production setup
2. **Use ADC (service account credentials)** - no API key management needed
3. **Ensure DEFAULT_VERTEX_MODEL is always a valid Vertex AI model name**

### Model Name Best Practices

- **Google AI Studio**: Preview model names often work (flexible)
- **Vertex AI**: Use only stable, documented model names:
  - `gemini-2.0-flash` (current default, stable)
  - `gemini-2.0-flash-001` (version-pinned)
  - `gemini-2.5-flash` (newer)

## Files Analyzed

1. **Workflows:**
   - `.github/workflows/a2a-parallel-agents.yml` - Main A2A parallel workflow

2. **Infrastructure:**
   - `infrastructure/terraform/adk-agents.tf` - Cloud Run configuration
   - `infrastructure/docker/adk-agents/shared/gemini_client.py` - Unified Gemini client

3. **Frontend:**
   - `infrastructure/docker/ag-ui-frontend/src/app/api/copilotkit/route.ts`
   - `infrastructure/docker/ag-ui-frontend/src/app/api/debug/route.ts`

## Related Issues/PRs

- Original fix: Changed `DEFAULT_VERTEX_MODEL` from "gemini-3-pro-preview" to "gemini-2.0-flash"
- Context: The model name error caused 404s only in Cloud Run because Vertex AI validates model names strictly

## Conclusion

The A2A parallel agents system correctly uses two different authentication paths:

1. **GitHub Actions** → Google AI Studio (GEMINI_API_KEY) → Flexible model names
2. **Cloud Run** → Vertex AI (ADC) → Strict model name validation

The model name "gemini-3-pro-preview" worked in GitHub Actions but failed in Cloud Run because:
- GitHub Actions uses Google AI Studio mode by default
- Cloud Run explicitly sets `USE_VERTEX_AI=true` for production reliability
- Vertex AI requires valid model names, which "gemini-3-pro-preview" is not

This is the expected and correct architecture - the issue was simply an invalid default model name in the Vertex AI code path.
