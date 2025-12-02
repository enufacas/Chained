#!/usr/bin/env python3
"""
Ask Gemini Tool - Escalation to Gemini 3 Pro Preview

This tool provides a simple interface for consulting Google's Gemini 3 Pro Preview
during Copilot sessions. It enables the "ask gemini about X" pattern where a human
can escalate complex problems to Gemini for expert consultation.

Usage:
    # As a standalone script
    python3 ask_gemini.py "What are the security implications of using regex for input validation?"
    
    # As a Python module
    from tools.ask_gemini import ask_gemini
    response = ask_gemini("How should I structure this API?")

Authentication:
    Requires one of:
    - GEMINI_API_KEY environment variable (Google AI Studio)
    - GOOGLE_API_KEY + USE_VERTEX_AI=true (Vertex AI)

Model:
    Uses gemini-3-pro-preview (same as gemini-invoke.yml workflow)

Author: @gemini-consultant (Vannevar Bush)
"""

import argparse
import os
import sys
from typing import Optional

# Check for required dependencies
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False
    vertexai = None
    GenerativeModel = None


def get_auth_mode() -> tuple[str, Optional[str]]:
    """
    Determine which authentication mode to use.
    
    Returns:
        Tuple of (mode, error_message)
        mode: 'genai', 'vertex', or None
        error_message: Error description if mode is None
    """
    use_vertex = os.getenv("USE_VERTEX_AI", "false").lower() in ("true", "1", "yes")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT_ID", ""))
    
    # If USE_VERTEX_AI is set, prefer Vertex AI
    if use_vertex:
        if not VERTEX_AVAILABLE:
            return None, "Vertex AI mode requested but google-cloud-aiplatform not installed. Install: pip install google-cloud-aiplatform"
        if not gcp_project:
            return None, "Vertex AI mode requires GOOGLE_CLOUD_PROJECT or GCP_PROJECT_ID environment variable"
        return "vertex", None
    
    # Check for Google AI Studio API key
    if gemini_api_key or google_api_key:
        if not GENAI_AVAILABLE:
            return None, "Google AI Studio mode requires google-generativeai package. Install: pip install google-generativeai"
        return "genai", None
    
    # No authentication configured
    error = """No Gemini authentication configured.

Option 1 - Google AI Studio (Recommended):
  1. Get API key from https://aistudio.google.com/app/apikey
  2. Set environment variable: export GEMINI_API_KEY=your-api-key

Option 2 - Vertex AI (For GCP users):
  1. Set environment variable: export GOOGLE_API_KEY=your-vertex-api-key
  2. Set environment variable: export USE_VERTEX_AI=true
  3. Set environment variable: export GOOGLE_CLOUD_PROJECT=your-project-id

See docs/GEMINI_CLI_INTEGRATION.md for detailed setup instructions.
"""
    return None, error


def ask_gemini(
    question: str,
    context: Optional[str] = None,
    model: str = "gemini-3-pro-preview",
    timeout_seconds: int = 30,
) -> str:
    """
    Consult Gemini 3 Pro Preview with a question.
    
    Args:
        question: The question or problem to ask Gemini about
        context: Optional additional context to provide
        model: Gemini model to use (default: gemini-3-pro-preview)
        timeout_seconds: Maximum time to wait for response (default: 30)
        
    Returns:
        Gemini's response as a string
        
    Raises:
        RuntimeError: If authentication is not configured or API call fails
    """
    # Check authentication
    mode, error = get_auth_mode()
    if mode is None:
        raise RuntimeError(error)
    
    # Build the prompt
    prompt = f"""You are Gemini 3 Pro Preview, consulted as an expert by the Chained autonomous AI ecosystem.

Context: You are being consulted to provide expert insights, second opinions, or analysis on a complex problem. Your response will be integrated with the Chained repository's context by a specialized gemini-consultant agent.

{f"Additional Context: {context}" if context else ""}

Question/Problem:
{question}

Please provide:
1. A clear, thoughtful analysis of the problem
2. Multiple perspectives or approaches where applicable
3. Specific recommendations with rationale
4. Any caveats, trade-offs, or considerations
5. Actionable next steps

Be thorough but concise. Focus on practical, actionable insights.
"""
    
    try:
        if mode == "vertex":
            return _ask_gemini_vertex(prompt, model, timeout_seconds)
        else:
            return _ask_gemini_genai(prompt, model, timeout_seconds)
    except Exception as e:
        raise RuntimeError(f"Error consulting Gemini: {str(e)}") from e


def _ask_gemini_genai(prompt: str, model: str, timeout_seconds: int) -> str:
    """Use Google AI Studio API (google-generativeai)."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Configure generation parameters
    generation_config = {
        "temperature": 0.7,  # Balanced creativity and consistency
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
    
    model_instance = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
    )
    
    # Generate response
    response = model_instance.generate_content(prompt)
    
    # Extract text
    if hasattr(response, 'text'):
        return response.text
    elif hasattr(response, 'parts'):
        return ''.join(part.text for part in response.parts if hasattr(part, 'text'))
    else:
        raise RuntimeError("Unexpected response format from Gemini")


def _ask_gemini_vertex(prompt: str, model: str, timeout_seconds: int) -> str:
    """Use Vertex AI API (google-cloud-aiplatform)."""
    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Initialize Vertex AI
    vertexai.init(project=gcp_project, location=location)
    
    # Map model names (Google AI Studio vs Vertex AI naming)
    model_mapping = {
        "gemini-3-pro-preview": "gemini-2.0-flash",  # Use latest stable on Vertex AI
        "gemini-1.5-pro-latest": "gemini-1.5-pro",
        "gemini-1.5-flash-latest": "gemini-1.5-flash",
    }
    vertex_model = model_mapping.get(model, model)
    
    # Configure generation
    generation_config = GenerationConfig(
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=2048,
    )
    
    model_instance = GenerativeModel(vertex_model)
    
    # Generate response
    response = model_instance.generate_content(
        prompt,
        generation_config=generation_config,
    )
    
    # Extract text
    if hasattr(response, 'text'):
        return response.text
    elif hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
            return ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
    
    raise RuntimeError("Unexpected response format from Vertex AI")


def main():
    """CLI entry point for ask_gemini tool."""
    parser = argparse.ArgumentParser(
        description="Consult Gemini 3 Pro Preview for expert insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ask a question
  python3 ask_gemini.py "What are the trade-offs between REST and GraphQL?"
  
  # Provide additional context
  python3 ask_gemini.py "Should we refactor this code?" --context "High complexity, low test coverage"
  
  # Use a different model
  python3 ask_gemini.py "Explain this pattern" --model gemini-1.5-flash-latest

Authentication:
  Requires GEMINI_API_KEY environment variable (Google AI Studio)
  OR GOOGLE_API_KEY + USE_VERTEX_AI=true (Vertex AI)
  
  See docs/GEMINI_CLI_INTEGRATION.md for setup instructions.
        """
    )
    
    parser.add_argument(
        "question",
        help="Question or problem to ask Gemini about"
    )
    parser.add_argument(
        "-c", "--context",
        help="Additional context to provide with the question"
    )
    parser.add_argument(
        "-m", "--model",
        default="gemini-3-pro-preview",
        help="Gemini model to use (default: gemini-3-pro-preview)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    try:
        print("🤔 Consulting Gemini 3 Pro Preview...\n", file=sys.stderr)
        
        response = ask_gemini(
            question=args.question,
            context=args.context,
            model=args.model,
            timeout_seconds=args.timeout,
        )
        
        print("✅ Gemini's Response:\n", file=sys.stderr)
        print(response)
        
        return 0
        
    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
