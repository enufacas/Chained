#!/usr/bin/env python3
"""
Ask Gemini Tool - Escalation to Gemini 3 Pro Preview

This tool provides a simple interface for consulting Google's Gemini 3 Pro Preview
during Copilot sessions. It enables the "ask gemini about X" pattern where a human
can escalate complex problems to Gemini for expert consultation.

**NEW: Code-Fixing Mode** - Specialized mode for getting actual code fixes instead
of just analysis. Use ask_gemini_fix_code() or --fix-code flag for concrete solutions.

⚠️ **CRITICAL LIMITATION**: The Gemini API has NO direct access to your repository.
   You MUST provide actual code and context in the function parameters. Use view()
   and bash() tools to gather context BEFORE calling Gemini.

Usage:
    # General consultation (include code in prompt)
    python3 ask_gemini.py "What are the security implications of using regex?" \\
        --context "Code: $(cat tools/validator.py)"
    
    # Code fixing mode (include actual code)
    python3 ask_gemini.py --fix-code "Auth allows expired tokens" \\
        --file tools/auth.py --code "$(cat tools/auth.py)"
    
    # As a Python module - gather context first
    from tools.ask_gemini import ask_gemini, ask_gemini_fix_code
    
    # Get general advice WITH code context
    code = view("src/api.py")  # Read actual code first
    response = ask_gemini(
        "How should I structure this API?",
        context=f"Current code:\\n{code}"  # Include code
    )
    
    # Get code fixes WITH actual code
    code = view("src/utils.py")  # Read actual code first
    fix = ask_gemini_fix_code(
        issue_description="Function crashes on None input",
        file_path="src/utils.py",
        code_snippet=code  # Must provide actual code
    )

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


def ask_gemini_fix_code(
    issue_description: str,
    file_path: Optional[str] = None,
    code_snippet: Optional[str] = None,
    model: str = "gemini-3-pro-preview",
    timeout_seconds: int = 30,
) -> str:
    """
    Consult Gemini specifically for code fixes.
    
    This specialized function emphasizes getting actual code implementations
    rather than just analysis. Use this when you need concrete fixes.
    
    **IMPORTANT:** Gemini API has NO direct access to your repository.
    You MUST provide the actual code in code_snippet, not just file paths.
    
    Args:
        issue_description: Description of the code issue/bug
        file_path: Optional path to the file (for reference in response)
        code_snippet: **REQUIRED** - The actual current code that needs fixing.
                     Read this with view() before calling. Don't just pass file path.
        model: Gemini model to use (default: gemini-3-pro-preview)
        timeout_seconds: Maximum time to wait for response (default: 30)
        
    Returns:
        Gemini's response with code fixes
        
    Raises:
        RuntimeError: If authentication is not configured or API call fails
    
    Example:
        # ❌ BAD - No actual code provided
        fix = ask_gemini_fix_code(
            issue_description="Fix auth bug",
            file_path="tools/auth.py"
        )
        
        # ✅ GOOD - Actual code included
        code = view("tools/auth.py")  # Get actual code first
        fix = ask_gemini_fix_code(
            issue_description="Fix expired token validation",
            file_path="tools/auth.py",
            code_snippet=code  # Pass actual code
        )
    """
    # Check authentication
    mode, error = get_auth_mode()
    if mode is None:
        raise RuntimeError(error)
    
    # Warn if no code snippet provided
    if not code_snippet:
        import sys
        print("⚠️  WARNING: No code_snippet provided. Gemini can't see your repository.", file=sys.stderr)
        print("    Use view() to read the file first, then pass the code.", file=sys.stderr)
    
    # Build specialized code-fixing prompt
    context_parts = []
    if file_path:
        context_parts.append(f"File: {file_path}")
    if code_snippet:
        context_parts.append(f"Current Code:\n```\n{code_snippet}\n```")
    
    context_str = "\n\n".join(context_parts) if context_parts else ""
    
    prompt = f"""You are Gemini 3 Pro Preview, consulted as a code-fixing expert by the Chained autonomous AI ecosystem.

TASK: Provide actual working code to fix the issue described below.

{context_str}

Issue Description:
{issue_description}

REQUIREMENTS FOR YOUR RESPONSE:
1. **Show the fixed code** - Provide the complete, corrected implementation
2. **Before/After comparison** - Show both the problematic code and the fix
3. **Specific location** - If file path provided, reference it with line numbers
4. **Implementation steps** - Number the exact steps to apply this fix
5. **Verification** - Provide the exact command to test the fix
6. **Brief explanation** - Explain why this fixes the issue (keep short)

FORMAT:
## Fix for {file_path or "the issue"}

**Before (Problematic Code):**
```
[current code]
```

**After (Fixed Code):**
```
[corrected code]
```

**What Changed:**
- [Specific change 1]
- [Specific change 2]

**Why This Fixes It:**
[Brief explanation]

**Implementation Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Test Command:**
```bash
[command to verify fix]
```

IMPORTANT: Focus on WORKING CODE first. The user needs an actual implementation, not analysis.
"""
    
    try:
        if mode == "vertex":
            return _ask_gemini_vertex(prompt, model, timeout_seconds)
        else:
            return _ask_gemini_genai(prompt, model, timeout_seconds)
    except Exception as e:
        raise RuntimeError(f"Error consulting Gemini for code fix: {str(e)}") from e


def ask_gemini(
    question: str,
    context: Optional[str] = None,
    model: str = "gemini-3-pro-preview",
    timeout_seconds: int = 30,
) -> str:
    """
    Consult Gemini 3 Pro Preview with a question.
    
    **IMPORTANT:** Gemini API has NO direct access to your repository.
    You MUST provide code/context in the 'context' parameter, not just descriptions.
    
    Args:
        question: The question or problem to ask Gemini about
        context: **CRITICAL** - Repository context including actual code, not just descriptions.
                Use view() and bash() to gather this BEFORE calling.
        model: Gemini model to use (default: gemini-3-pro-preview)
        timeout_seconds: Maximum time to wait for response (default: 30)
        
    Returns:
        Gemini's response as a string
        
    Raises:
        RuntimeError: If authentication is not configured or API call fails
    
    Example:
        # ❌ BAD - No repository context
        response = ask_gemini("How to fix auth?")
        
        # ✅ GOOD - Include actual code context
        code = view("tools/auth.py")
        tests = view("tests/test_auth.py")
        context = f"Current auth code:\\n{code}\\n\\nTests:\\n{tests}"
        response = ask_gemini(
            "How to add expiration checking?",
            context=context
        )
    """
    # Check authentication
    mode, error = get_auth_mode()
    if mode is None:
        raise RuntimeError(error)
    
    # Build the prompt
    prompt = f"""You are Gemini 3 Pro Preview, consulted as an expert by the Chained autonomous AI ecosystem.

Context: You are being consulted to provide ACTIONABLE solutions, not just analysis. Your response should prioritize:
1. ACTUAL CODE FIXES when the question involves code issues
2. SPECIFIC FILE LOCATIONS (path/to/file.py:line_number) where changes are needed
3. BEFORE/AFTER code examples showing exact changes
4. CONCRETE IMPLEMENTATION STEPS that can be executed immediately
5. TEST COMMANDS to verify the fix works

Your response will be integrated with the Chained repository's context by a specialized gemini-consultant agent.

{f"Additional Context: {context}" if context else ""}

Question/Problem:
{question}

Please provide:
1. **If this is a code issue:** Show the actual code fix with before/after examples
2. **Identify exact locations:** Specify file paths and line numbers  
3. **Implementation steps:** Clear, numbered steps to apply the solution
4. **Verification:** How to test that the fix works
5. **Explanation:** Why this solution works (AFTER showing the code)

IMPORTANT: Prioritize showing code and solutions FIRST, explanations SECOND.
Be thorough but focus on ACTIONABLE, IMPLEMENTABLE solutions.
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
  # Ask a general question
  python3 ask_gemini.py "What are the trade-offs between REST and GraphQL?"
  
  # Get a code fix
  python3 ask_gemini.py --fix-code "Authentication allows expired tokens" \\
    --file tools/auth.py --code "def validate_token(token): return jwt.decode(token, KEY)"
  
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
        nargs='?',
        help="Question or problem to ask Gemini about"
    )
    parser.add_argument(
        "-c", "--context",
        help="Additional context to provide with the question"
    )
    parser.add_argument(
        "--fix-code",
        help="Use code-fixing mode: provide issue description for code fix"
    )
    parser.add_argument(
        "--file",
        help="File path where the code issue is located (for --fix-code mode)"
    )
    parser.add_argument(
        "--code",
        help="Current code snippet that needs fixing (for --fix-code mode)"
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
    
    # Validate arguments
    if args.fix_code:
        if not args.fix_code:
            parser.error("--fix-code requires an issue description")
        mode = "fix-code"
        question_text = args.fix_code
    elif args.question:
        mode = "general"
        question_text = args.question
    else:
        parser.error("Either provide a question or use --fix-code mode")
    
    try:
        if mode == "fix-code":
            print("🔧 Consulting Gemini for code fix...\n", file=sys.stderr)
            
            response = ask_gemini_fix_code(
                issue_description=question_text,
                file_path=args.file,
                code_snippet=args.code,
                model=args.model,
                timeout_seconds=args.timeout,
            )
        else:
            print("🤔 Consulting Gemini 3 Pro Preview...\n", file=sys.stderr)
            
            response = ask_gemini(
                question=question_text,
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
