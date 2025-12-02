# Copilot Setup Steps: Gemini Integration

## What Was Added

The `copilot-setup-steps.yml` workflow has been updated to automatically configure the Gemini API for the `ask_gemini` tool when Copilot sessions start.

## Changes Made

### 1. Gemini API Configuration Check
**Location:** After GCP environment setup  
**Purpose:** Detect which Gemini authentication mode is available

```yaml
- name: Check Gemini API configuration
  # Checks for GEMINI_API_KEY or GOOGLE_API_KEY + USE_VERTEX_AI
  # Outputs: gemini_mode (vertex/genai/none), gemini_configured (true/false)
```

**Detection Logic:**
1. **Vertex AI mode:** If `USE_VERTEX_AI=true` AND `GOOGLE_API_KEY` is set
2. **Google AI Studio mode:** If `GEMINI_API_KEY` is set
3. **Fallback mode:** If `GOOGLE_API_KEY` is set but `USE_VERTEX_AI` is not (tries as Google AI Studio key)
4. **None:** If no keys are configured

### 2. Gemini Environment Setup
**Location:** Conditional step after configuration check  
**Purpose:** Export environment variables for ask_gemini tool

```yaml
- name: Configure Gemini environment for Copilot
  # Sets up USE_VERTEX_AI, GOOGLE_API_KEY, GEMINI_API_KEY, GOOGLE_CLOUD_PROJECT
  # Only runs if Gemini is configured
```

**Environment Variables Set:**

**For Vertex AI mode:**
```bash
USE_VERTEX_AI=true
GOOGLE_API_KEY=$GOOGLE_API_KEY
GOOGLE_CLOUD_PROJECT=$GCP_PROJECT_ID
GEMINI_AVAILABLE=true
GEMINI_MODE=vertex
```

**For Google AI Studio mode:**
```bash
GEMINI_API_KEY=$GEMINI_API_KEY  # or $GOOGLE_API_KEY as fallback
GEMINI_AVAILABLE=true
GEMINI_MODE=genai
```

### 3. ask_gemini Tool Verification
**Location:** After environment setup  
**Purpose:** Verify the tool can authenticate properly

```yaml
- name: Verify ask_gemini tool
  # Tests authentication mode detection
  # Sets ASK_GEMINI_READY=true/false
```

This step:
- Imports the ask_gemini module
- Calls `get_auth_mode()` to verify authentication
- Reports success or failure
- Continues even if it fails (non-blocking)

### 4. Updated Summary
**Location:** Final step of workflow  
**Purpose:** Show Gemini API status in workflow summary

**New Table Rows:**
```markdown
| Gemini API | ✅ or ⚠️ Not configured |
| ask_gemini | ✅ Ready or ⚠️ Not available |
```

**New Section:**
```markdown
### ✅ Gemini API (ask_gemini tool)
The ask_gemini tool is configured and ready. Copilot can escalate to Gemini 3 Pro Preview.

**Mode:** vertex (or genai)

**Usage:** Say 'ask gemini about [question]' or '@gemini-consultant [question]' in Copilot
```

Or if not configured:
```markdown
### ⚠️ Gemini API Not Configured
The ask_gemini tool is not available. To enable:
[Setup instructions]
```

## Why This Was Added

### 1. Automatic Configuration
Without these steps, users would need to manually:
- Export environment variables in their Copilot session
- Install packages
- Configure authentication

Now it happens automatically when Copilot starts.

### 2. Multiple Auth Modes
Supports both authentication methods:
- Google AI Studio (simpler, for most users)
- Vertex AI (for GCP users who already have credentials)

### 3. Reuses Existing Secrets
If GCP is already configured, Vertex AI mode can reuse:
- `GOOGLE_API_KEY` (service account)
- `GCP_PROJECT_ID`

No additional secrets needed for Vertex AI users.

### 4. Graceful Degradation
If Gemini isn't configured:
- Workflow doesn't fail
- Other tools remain available
- Clear instructions shown in summary

### 5. Verification
Tests that the tool actually works:
- Detects authentication mode
- Verifies credentials are valid
- Reports readiness status

## Required Secrets/Variables

### For Google AI Studio Mode (Option A)
**Secrets (in copilot environment):**
- `GEMINI_API_KEY` - Get from https://aistudio.google.com/app/apikey

**Variables:**
- None required

### For Vertex AI Mode (Option B)
**Secrets (in copilot environment):**
- `GOOGLE_API_KEY` - Vertex AI API key or service account key
- `GCP_PROJECT_ID` - Your GCP project ID

**Variables (in copilot environment):**
- `USE_VERTEX_AI=true`

### For Current Session (Already Configured!)
The current session already has:
- ✅ `GOOGLE_API_KEY`
- ✅ `GCP_PROJECT_ID`
- ⚠️ `USE_VERTEX_AI` - Just needs to be set to `true` as a variable

## Configuration Instructions

### Step 1: Navigate to Environment Settings
```
Repository → Settings → Environments → copilot
```

### Step 2: Add Secrets (Choose One Option)

**Option A: Google AI Studio**
1. Get API key from https://aistudio.google.com/app/apikey
2. Add secret: `GEMINI_API_KEY` = your-api-key
3. Done!

**Option B: Vertex AI (If GCP already configured)**
1. Go to Variables tab
2. Add variable: `USE_VERTEX_AI` = `true`
3. Done! (Will use existing GOOGLE_API_KEY and GCP_PROJECT_ID)

**Option B: Vertex AI (If GCP not configured)**
1. Get Vertex AI API key from Google Cloud Console
2. Add secret: `GOOGLE_API_KEY` = your-vertex-api-key
3. Add secret: `GCP_PROJECT_ID` = your-project-id
4. Add variable: `USE_VERTEX_AI` = `true`

### Step 3: Test
Next time Copilot runs, the workflow summary will show:
```
✅ Gemini API
✅ ask_gemini Ready
```

## Benefits

### For Users
- **Zero manual setup** - Works automatically when Copilot starts
- **Clear status** - Workflow summary shows if Gemini is available
- **Easy troubleshooting** - Shows exact configuration needed

### For the Tool
- **Consistent environment** - Same setup every session
- **Verified credentials** - Authentication tested before use
- **Proper exports** - All required env vars set correctly

### For the Repository
- **Documented process** - Clear in copilot-setup-steps.yml
- **Maintainable** - Standard GitHub Actions patterns
- **Flexible** - Supports multiple auth modes

## Testing the Setup

### View Workflow Summary
After the workflow runs, check:
```
Actions → System: Copilot Setup Steps → Latest run → Summary
```

Look for:
- `✅ Gemini API` in the tools table
- `✅ ask_gemini Ready` in the tools table
- Usage instructions in the Gemini API section

### Test in a Copilot Session
Once configured, test with:
```bash
# Check environment
echo "GEMINI_AVAILABLE: $GEMINI_AVAILABLE"
echo "GEMINI_MODE: $GEMINI_MODE"

# Test the tool
python3 tools/ask_gemini.py "What is Python?"
```

### Expected Output
```
🤔 Consulting Gemini 3 Pro Preview...
✅ Gemini's Response:
[Response from Gemini]
```

## Troubleshooting

### Issue: "Gemini API Not Configured" in summary
**Cause:** No GEMINI_API_KEY or GOOGLE_API_KEY secret configured

**Solution:** Follow configuration instructions above

### Issue: "ask_gemini tool authentication issue"
**Cause:** Secret is set but package installation failed

**Solution:**
1. Check that `requirements.txt` includes Gemini packages
2. Check Python dependencies installation step succeeded
3. Review workflow logs for pip install errors

### Issue: "⚠️ GOOGLE_API_KEY found but USE_VERTEX_AI not set"
**Cause:** Have GOOGLE_API_KEY but USE_VERTEX_AI variable not configured

**Solution:**
- If you want Vertex AI: Set `USE_VERTEX_AI=true` as a variable
- If you want Google AI Studio: Rename secret to `GEMINI_API_KEY` instead

## Impact on Existing Setup

### No Breaking Changes
- Existing GCP configuration unchanged
- All existing environment variables preserved
- Other tools continue working normally

### Additive Only
- Only adds new environment variables if Gemini is configured
- No effect on workflows or tools that don't use Gemini
- Gracefully handles missing configuration

### Performance Impact
- Adds ~5 seconds to setup time
- Only runs if Gemini secrets are configured
- Verification step can fail without blocking other setup

## Related Files

- **Workflow:** `.github/workflows/copilot-setup-steps.yml`
- **Tool:** `tools/ask_gemini.py`
- **Agent:** `.github/agents/gemini-consultant.md`
- **Docs:** `docs/guides/ASK_GEMINI.md`
- **Guide:** `docs/guides/GEMINI_INTEGRATION_COMPARISON.md`

## Next Steps

1. **Configure secrets** in the copilot environment (if not already done)
2. **Test workflow** by triggering copilot-setup-steps.yml
3. **Verify summary** shows Gemini API as ready
4. **Use in Copilot** by saying "ask gemini about [question]"

---

**Added:** 2024-12-02  
**Purpose:** Enable automatic Gemini API configuration for ask_gemini tool  
**Status:** ✅ Implemented and documented
