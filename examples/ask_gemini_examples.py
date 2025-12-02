#!/usr/bin/env python3
"""
Example: Using ask_gemini in different ways

This script demonstrates the various ways to use the ask_gemini tool
for consulting Gemini 3 Pro Preview from Python code.
"""

import os
import sys

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.ask_gemini import ask_gemini, get_auth_mode


def example_1_basic_usage():
    """Example 1: Basic usage without API key (shows error handling)"""
    print("=" * 70)
    print("Example 1: Basic usage (auth check)")
    print("=" * 70)
    
    mode, error = get_auth_mode()
    
    if mode:
        print(f"✅ Authentication mode: {mode}")
    else:
        print(f"❌ No authentication configured:")
        print(error)
    
    print()


def example_2_with_mock_key():
    """Example 2: Show what happens with a configured API key (mocked)"""
    print("=" * 70)
    print("Example 2: With API key configured (simulated)")
    print("=" * 70)
    
    # Simulate having an API key
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'mock-key-for-demo'
    
    mode, error = get_auth_mode()
    
    if mode:
        print(f"✅ Authentication mode: {mode}")
        print(f"✅ Ready to call ask_gemini()")
        print()
        print("Example call:")
        print('  response = ask_gemini("What are REST API best practices?")')
        print()
        print("This would:")
        print("  1. Authenticate with Gemini API")
        print("  2. Send the question with context")
        print("  3. Wait for Gemini's response")
        print("  4. Return expert analysis and recommendations")
    else:
        print(f"❌ Error: {error}")
    
    # Restore original
    if original_key:
        os.environ['GEMINI_API_KEY'] = original_key
    else:
        os.environ.pop('GEMINI_API_KEY', None)
    
    print()


def example_3_python_api():
    """Example 3: Python API usage patterns"""
    print("=" * 70)
    print("Example 3: Python API usage patterns")
    print("=" * 70)
    
    print("""
# Pattern 1: Simple question
response = ask_gemini("What are the benefits of type hints in Python?")

# Pattern 2: With additional context
response = ask_gemini(
    question="Should we add caching to this API endpoint?",
    context="Current response time: 200ms, Cache hit rate: 80%"
)

# Pattern 3: Custom model
response = ask_gemini(
    question="Explain event-driven architecture",
    model="gemini-1.5-flash-latest"
)

# Pattern 4: Custom timeout
response = ask_gemini(
    question="Complex architectural analysis needed",
    timeout_seconds=60
)
    """)
    
    print()


def example_4_cli_usage():
    """Example 4: Command-line usage patterns"""
    print("=" * 70)
    print("Example 4: Command-line usage patterns")
    print("=" * 70)
    
    print("""
# Basic question
$ python3 tools/ask_gemini.py "What are the trade-offs between REST and GraphQL?"

# With context
$ python3 tools/ask_gemini.py \
    "Should we refactor this code?" \
    --context "High complexity, low test coverage"

# Different model
$ python3 tools/ask_gemini.py \
    "Explain this pattern" \
    --model gemini-1.5-flash-latest

# Custom timeout
$ python3 tools/ask_gemini.py \
    "Complex question" \
    --timeout 60
    """)
    
    print()


def example_5_copilot_integration():
    """Example 5: How it works in Copilot sessions"""
    print("=" * 70)
    print("Example 5: Integration with GitHub Copilot")
    print("=" * 70)
    
    print("""
During a GitHub Copilot session, a human can say:

  "ask gemini about whether we should use microservices or monolithic"

What happens behind the scenes:

  1. Copilot recognizes "ask gemini" trigger
  2. Invokes @gemini-consultant agent
  3. Agent calls: ask_gemini(
       question="Should we use microservices or monolithic?",
       context="<repository context gathered by agent>"
     )
  4. Gemini 3 Pro Preview analyzes the question
  5. Returns expert insights and recommendations
  6. Agent synthesizes with repository knowledge
  7. Human receives comprehensive guidance

Alternative: Explicit agent mention:

  "@gemini-consultant what are the security implications of this approach?"

Result: Same flow, but more explicit invocation.
    """)
    
    print()


def example_6_use_cases():
    """Example 6: Common use cases"""
    print("=" * 70)
    print("Example 6: Common use cases")
    print("=" * 70)
    
    use_cases = [
        ("Architectural Decisions", 
         '"ask gemini about REST vs GraphQL for agent APIs"'),
        
        ("Security Analysis",
         '"ask gemini about security implications of storing JWTs in localStorage"'),
        
        ("Performance Trade-offs",
         '"ask gemini about caching strategies for this API endpoint"'),
        
        ("Complex Refactoring",
         '"ask gemini about how to refactor this 1000-line function"'),
        
        ("Unknown Domains",
         '"ask gemini about WebAssembly performance characteristics"'),
        
        ("Second Opinions",
         '"ask gemini to validate this API design"'),
    ]
    
    for category, example in use_cases:
        print(f"\n{category}:")
        print(f"  {example}")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print(" Ask Gemini Tool - Usage Examples")
    print("=" * 70 + "\n")
    
    example_1_basic_usage()
    example_2_with_mock_key()
    example_3_python_api()
    example_4_cli_usage()
    example_5_copilot_integration()
    example_6_use_cases()
    
    print("=" * 70)
    print(" Setup Instructions")
    print("=" * 70)
    print("""
To use ask_gemini, configure authentication:

Option A: Google AI Studio (Recommended)
  1. Get API key from https://aistudio.google.com/app/apikey
  2. Set environment variable:
     export GEMINI_API_KEY="your-api-key"

Option B: Vertex AI (For GCP users)
  1. Get Vertex AI API key from Google Cloud Console
  2. Set environment variables:
     export GOOGLE_API_KEY="your-vertex-api-key"
     export USE_VERTEX_AI=true
     export GOOGLE_CLOUD_PROJECT="your-project-id"

For complete documentation, see:
  docs/guides/ASK_GEMINI.md
    """)
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
