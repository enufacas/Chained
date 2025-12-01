# A2A Parallel Agents: API Key and Model Configuration Analysis

**Investigation Date**: 2025-12-01 (Corrected)  
**Investigator**: @investigate-champion  
**Issue Context**: Understanding how the A2A parallel agents workflow handles GOOGLE_API_KEY, GEMINI_API_KEY, and model selection

## Executive Summary (Corrected)

After examining actual workflow logs from [run #19788906972](https://github.com/enufacas/Chained/actions/runs/19788906972), both the GitHub Actions workflow AND Cloud Run ADK agents use **Vertex AI mode**:

| Component | USE_VERTEX_AI | API Key | Model |
|-----------|---------------|---------|-------|
| GitHub Actions (run-gemini-cli) | **true** | GOOGLE_API_KEY | gemini-3-pro-preview |
| Cloud Run ADK Agents | **true** | ADC (Service Account) | gemini-2.0-flash |

**Both use Vertex AI, but with different authentication mechanisms.** The key difference that explains why the workflow worked while Cloud Run failed is:

1. **GitHub Actions**: Uses `GOOGLE_API_KEY` (API key authentication) with Gemini CLI
2. **Cloud Run**: Uses ADC (Application Default Credentials from service account)

The Gemini CLI (`run-gemini-cli` action) handles model names differently than the Python `vertexai` SDK used by ADK agents.

## Architecture Overview (Corrected)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    A2A PARALLEL AGENTS WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GitHub Actions Runner                    GCP Cloud Run                     │
│  ┌───────────────────────┐               ┌────────────────────────────────┐ │
│  │ run-gemini-cli action │               │ ADK Agents (Python)            │ │
│  │                       │               │                                │ │
│  │ • GOOGLE_GENAI_USE_   │               │ • USE_VERTEX_AI=true           │ │
│  │   VERTEXAI=true       │               │ • GOOGLE_CLOUD_PROJECT         │ │
│  │ • GOOGLE_API_KEY ✓    │               │ • Service Account ADC          │ │
│  │                       │               │                                │ │
│  │ Tool: Gemini CLI      │               │ Tool: vertexai Python SDK      │ │
│  │ (Node.js)             │               │ (google-cloud-aiplatform)      │ │
│  │ Model handling: ✓     │               │ Model handling: Strict         │ │
│  │ (gemini-3-pro-preview)│               │ (gemini-2.0-flash required)    │ │
│  └───────────────────────┘               └────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Evidence from Workflow Logs

From the [actual workflow run](https://github.com/enufacas/Chained/actions/runs/19788906972), job `agent (create-guru, gemini)`:

```
env:
  GOOGLE_GENAI_USE_VERTEXAI: true   # ✓ Vertex AI mode IS enabled
  GOOGLE_API_KEY: ***                # ✓ Using GOOGLE_API_KEY (not GEMINI_API_KEY)
  GEMINI_MODEL: gemini-3-pro-preview # Model name passed to Gemini CLI
  GEMINI_API_KEY:                    # Empty (not using AI Studio key)
  GOOGLE_CLOUD_PROJECT:              # Empty (using API key instead of ADC)
```

This proves:
1. **GOOGLE_GENAI_USE_VERTEXAI is set to `true`** in the workflow
2. **GOOGLE_API_KEY is being used** (not GEMINI_API_KEY)
3. **gemini-3-pro-preview** is passed as the model name

## Why the Same Model Works in Workflow But Not Cloud Run

### Key Difference: The Tool/SDK Used

| Environment | Tool | Authentication | Model Handling |
|-------------|------|----------------|----------------|
| GitHub Actions | Gemini CLI (@google/gemini-cli) | GOOGLE_API_KEY | More lenient |
| Cloud Run | Python vertexai SDK | Service Account ADC | Strict validation |

### Hypothesis

The **Gemini CLI** (used by `run-gemini-cli` action) appears to handle model name resolution differently than the **Python vertexai SDK**:

1. **Gemini CLI**: May perform model name translation, aliasing, or use a different API path that accepts "gemini-3-pro-preview"
2. **Python vertexai SDK**: Directly calls Vertex AI endpoints which require exact model names like "gemini-2.0-flash"

### Questions for Further Investigation

1. Does Gemini CLI translate model names internally?
2. Does `GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=true` route to a different endpoint than ADC?
3. Is there a model name aliasing layer in the Gemini CLI that doesn't exist in the Python SDK?

## Configuration Details

### GitHub Actions Workflow Configuration

From `a2a-parallel-agents.yml`:
```yaml
with:
  gemini_api_key: '${{ secrets.GEMINI_API_KEY }}'
  google_api_key: '${{ secrets.GOOGLE_API_KEY }}'
  use_vertex_ai: '${{ vars.GOOGLE_GENAI_USE_VERTEXAI || ''false'' }}'
  gemini_model: '${{ vars.GEMINI_MODEL || ''gemini-3-pro-preview'' }}'
```

With repository variable `GOOGLE_GENAI_USE_VERTEXAI=true`, this results in:
- `GOOGLE_GENAI_USE_VERTEXAI: true`
- `GOOGLE_API_KEY: ***` (from secrets)
- `GEMINI_MODEL: gemini-3-pro-preview`

### Cloud Run Configuration (Terraform)

From `adk-agents.tf`:
```hcl
env {
  name  = "USE_VERTEX_AI"
  value = "true"
}
env {
  name  = "GOOGLE_CLOUD_PROJECT"
  value = var.project_id
}
# Uses service account's Application Default Credentials (ADC)
service_account = google_service_account.adk_agents.email
```

### ADK Agents Python Code

From `gemini_client.py`:
```python
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").lower() in ("true", "1", "yes")
DEFAULT_VERTEX_MODEL = "gemini-2.0-flash"  # Fixed after investigation

# When USE_VERTEX_AI=true and GOOGLE_CLOUD_PROJECT is set:
# Uses vertexai.generative_models.GenerativeModel(model_name)
# This requires exact Vertex AI model names
```

## GOOGLE_API_KEY vs ADC Authentication

| Method | Used By | How It Works |
|--------|---------|--------------|
| GOOGLE_API_KEY | GitHub Actions (Gemini CLI) | API key passed in requests |
| ADC (Service Account) | Cloud Run | OAuth2 from metadata server |

Both work with Vertex AI, but may have different:
- Rate limits
- Model availability
- Name resolution behavior

## The Fix That Was Applied

Changed `DEFAULT_VERTEX_MODEL` in `gemini_client.py`:
```python
# Before
DEFAULT_VERTEX_MODEL = "gemini-3-pro-preview"

# After
DEFAULT_VERTEX_MODEL = "gemini-2.0-flash"
```

This fixed Cloud Run but doesn't explain why the workflow works with "gemini-3-pro-preview".

## Recommendations

### Immediate Actions

1. **Align model names** - Consider updating `GEMINI_MODEL` repository variable to `gemini-2.0-flash` for consistency
2. **Document the difference** - The Gemini CLI appears to have different model handling than the Python SDK

### For Investigation

1. Check Gemini CLI source code for model name handling
2. Compare API calls made by Gemini CLI vs Python vertexai SDK
3. Test if model name aliases exist in one but not the other

## Files Analyzed

1. **Workflows:**
   - `.github/workflows/a2a-parallel-agents.yml`

2. **Infrastructure:**
   - `infrastructure/terraform/adk-agents.tf`
   - `infrastructure/docker/adk-agents/shared/gemini_client.py`

3. **Workflow Logs:**
   - [Run #19788906972](https://github.com/enufacas/Chained/actions/runs/19788906972) - Job logs examined

## Conclusion (Corrected)

**Previous conclusion was incorrect.** Both systems use Vertex AI mode (`GOOGLE_GENAI_USE_VERTEXAI=true`), but:

1. **GitHub Actions** uses Gemini CLI with GOOGLE_API_KEY authentication
2. **Cloud Run** uses Python vertexai SDK with Service Account ADC

The difference in behavior with model name "gemini-3-pro-preview" appears to be due to:
- Different tools (Gemini CLI vs Python SDK)
- Potentially different model name resolution/aliasing
- Different authentication mechanisms (API key vs ADC)

Further investigation is needed to understand exactly why the Gemini CLI accepts "gemini-3-pro-preview" while the Python SDK requires exact model names.
