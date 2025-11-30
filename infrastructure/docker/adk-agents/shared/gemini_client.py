"""
Unified Gemini Client for ADK Agents
====================================

This module provides a unified Gemini client that supports both authentication modes:

1. **Google AI Studio Mode** (API Key):
   - Uses `google-generativeai` library
   - Requires `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable
   - Calls `generativelanguage.googleapis.com`
   - Simpler setup, good for development

2. **Vertex AI Mode** (Application Default Credentials):
   - Uses `google-cloud-aiplatform` library
   - Uses ADC (service account on Cloud Run)
   - Requires `GOOGLE_CLOUD_PROJECT` environment variable
   - Calls `aiplatform.googleapis.com`
   - Recommended for production on GCP

The mode is selected based on the `USE_VERTEX_AI` environment variable.

Reference:
- Google AI Studio: https://aistudio.google.com/
- Vertex AI: https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal

**IMPORTANT**: This solves the "401 API keys are not supported by this API" error when
a Vertex AI/GCP API key is used with the Google AI Studio endpoint. When using GCP
credentials, you MUST use Vertex AI mode.
"""

import asyncio
import os
from typing import Any, Dict, Optional

# =============================================================================
# Configuration
# =============================================================================

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT_ID", ""))
USE_VERTEX_AI = os.getenv("USE_VERTEX_AI", "false").lower() in ("true", "1", "yes")

# Default model names for each mode
# Note: Model names differ between Google AI Studio and Vertex AI
DEFAULT_GENAI_MODEL = "gemini-1.5-flash"  # Google AI Studio model name
DEFAULT_VERTEX_MODEL = "gemini-2.0-flash"  # Vertex AI model name (stable, widely available)

# =============================================================================
# Availability Flags
# =============================================================================

# Check if google-generativeai is available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

# Check if google-cloud-aiplatform is available
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False
    vertexai = None
    GenerativeModel = None
    GenerationConfig = None


# =============================================================================
# Determine Active Mode
# =============================================================================

def get_active_mode() -> str:
    """
    Determine which Gemini mode to use.
    
    Returns:
        'vertex': Use Vertex AI with ADC
        'genai': Use Google AI Studio with API key
        'none': No Gemini available
    """
    # If USE_VERTEX_AI is explicitly set, prefer Vertex AI
    if USE_VERTEX_AI:
        if VERTEX_AVAILABLE and GOOGLE_CLOUD_PROJECT:
            return "vertex"
        # Fall through to check if genai is available as fallback
    
    # Check if Google AI Studio is available with API key
    if GENAI_AVAILABLE and (GEMINI_API_KEY or GOOGLE_API_KEY):
        return "genai"
    
    # Check Vertex AI as alternative
    if VERTEX_AVAILABLE and GOOGLE_CLOUD_PROJECT:
        return "vertex"
    
    return "none"


ACTIVE_MODE = get_active_mode()


# =============================================================================
# Initialize the appropriate library
# =============================================================================

_initialized = False

def _ensure_initialized():
    """Ensure the appropriate Gemini library is initialized."""
    global _initialized
    if _initialized:
        return
    
    if ACTIVE_MODE == "vertex":
        # Initialize Vertex AI
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=location)
        print(f"✅ Vertex AI initialized (project={GOOGLE_CLOUD_PROJECT}, location={location})")
        _initialized = True
        
    elif ACTIVE_MODE == "genai":
        # Initialize Google AI Studio
        api_key = GEMINI_API_KEY or GOOGLE_API_KEY
        genai.configure(api_key=api_key)
        print(f"✅ Google AI Studio initialized (API key: {api_key[:8]}...)")
        _initialized = True


# =============================================================================
# Unified Generation Function
# =============================================================================

async def generate_content(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: int = 2048,
    top_p: float = 0.9,
) -> Dict[str, Any]:
    """
    Generate content using Gemini (either Vertex AI or Google AI Studio).
    
    Args:
        prompt: The prompt to send to Gemini
        model: Optional model name override
        temperature: Temperature for generation (0.0-1.0)
        max_output_tokens: Maximum tokens in response
        top_p: Top-p sampling parameter
        
    Returns:
        Dict with:
            - text: Generated text
            - mode: 'vertex' or 'genai'
            - model: Model name used
            - usage: Token usage info (if available)
            
    Raises:
        GeminiUnavailableError: If Gemini is not configured
        GeminiError: If generation fails
    """
    _ensure_initialized()
    
    if ACTIVE_MODE == "none":
        raise GeminiUnavailableError(get_unavailable_error_message())
    
    if ACTIVE_MODE == "vertex":
        return await _generate_vertex(
            prompt=prompt,
            model=model or DEFAULT_VERTEX_MODEL,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
        )
    else:
        return await _generate_genai(
            prompt=prompt,
            model=model or DEFAULT_GENAI_MODEL,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
        )


async def _generate_vertex(
    prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
    top_p: float,
) -> Dict[str, Any]:
    """Generate content using Vertex AI."""
    try:
        vertex_model = GenerativeModel(model)
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
        )
        
        # Vertex AI's generate_content is synchronous, run in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: vertex_model.generate_content(
                prompt,
                generation_config=generation_config,
            )
        )
        
        text = ""
        if response.candidates:
            for part in response.candidates[0].content.parts:
                text += part.text
        
        return {
            "text": text,
            "mode": "vertex",
            "model": model,
            "usage": {
                "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', None),
                "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', None),
            } if hasattr(response, 'usage_metadata') else {},
        }
        
    except Exception as e:
        raise GeminiError(f"Vertex AI generation failed: {e}") from e


async def _generate_genai(
    prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
    top_p: float,
) -> Dict[str, Any]:
    """Generate content using Google AI Studio."""
    try:
        genai_model = genai.GenerativeModel(model)
        
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
        )
        
        # google-generativeai's generate_content is synchronous
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: genai_model.generate_content(
                prompt,
                generation_config=generation_config,
            )
        )
        
        return {
            "text": response.text if response.text else "",
            "mode": "genai",
            "model": model,
            "usage": {},  # Google AI Studio doesn't provide token counts in SDK
        }
        
    except Exception as e:
        raise GeminiError(f"Google AI Studio generation failed: {e}") from e


# =============================================================================
# Error Classes
# =============================================================================

class GeminiError(Exception):
    """Base exception for Gemini errors."""
    pass


class GeminiUnavailableError(GeminiError):
    """Raised when Gemini is not available (no credentials configured)."""
    pass


# =============================================================================
# Helper Functions
# =============================================================================

def is_available() -> bool:
    """Check if Gemini is available in any mode."""
    return ACTIVE_MODE != "none"


def get_mode() -> str:
    """Get the active Gemini mode ('vertex', 'genai', or 'none')."""
    return ACTIVE_MODE


def get_unavailable_error_message(agent_name: str = "Agent") -> str:
    """
    Build a descriptive error message when Gemini is unavailable.
    
    Args:
        agent_name: Name of the agent for the error message
        
    Returns:
        A descriptive error message explaining what's missing
    """
    parts = [f"{agent_name}: Gemini AI is required but not available."]
    
    if USE_VERTEX_AI:
        parts.append("USE_VERTEX_AI=true is set, but:")
        if not VERTEX_AVAILABLE:
            parts.append("  - google-cloud-aiplatform package is not installed")
        if not GOOGLE_CLOUD_PROJECT:
            parts.append("  - GOOGLE_CLOUD_PROJECT environment variable is not set")
    else:
        if not GENAI_AVAILABLE:
            parts.append("  - google-generativeai package is not installed")
        if not (GEMINI_API_KEY or GOOGLE_API_KEY):
            parts.append("  - No API key found in GEMINI_API_KEY or GOOGLE_API_KEY")
    
    parts.append("")
    parts.append("To fix this, either:")
    parts.append("  1. Set USE_VERTEX_AI=true and ensure GOOGLE_CLOUD_PROJECT is set (for GCP deployment)")
    parts.append("  2. Set GEMINI_API_KEY with a Google AI Studio API key (for local development)")
    
    return "\n".join(parts)


def get_config_info() -> Dict[str, Any]:
    """Get current configuration information for debugging."""
    return {
        "active_mode": ACTIVE_MODE,
        "use_vertex_ai_env": USE_VERTEX_AI,
        "genai_available": GENAI_AVAILABLE,
        "vertex_available": VERTEX_AVAILABLE,
        "has_api_key": bool(GEMINI_API_KEY or GOOGLE_API_KEY),
        "has_project_id": bool(GOOGLE_CLOUD_PROJECT),
        "default_vertex_model": DEFAULT_VERTEX_MODEL,
        "default_genai_model": DEFAULT_GENAI_MODEL,
    }
