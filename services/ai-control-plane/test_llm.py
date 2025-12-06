#!/usr/bin/env python3
"""
AI-Native Control Plane - LLM Integration Test

Tests the LLM integration module with real API calls to OpenAI or Gemini.
Demonstrates intent classification and plan generation capabilities.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_llm_configuration():
    """Test LLM configuration"""
    print("\n" + "=" * 60)
    print("LLM Configuration Test")
    print("=" * 60 + "\n")

    provider = os.getenv("LLM_PROVIDER", "gemini")
    print(f"Provider: {provider}")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        if api_key:
            print(f"✅ OpenAI API key configured")
            print(f"Model: {model}")
        else:
            print(f"❌ OPENAI_API_KEY not set")
            return False

    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if api_key:
            print(f"✅ Gemini API key configured")
            print(f"Model: {model}")
        else:
            print(f"❌ GEMINI_API_KEY not set")
            return False

    return True


def test_intent_classification():
    """Test intent classification with various requests"""
    print("\n" + "=" * 60)
    print("Intent Classification Test")
    print("=" * 60 + "\n")

    try:
        from llm import LLMClient

        client = LLMClient()

        # Test cases
        test_requests = [
            "Create a new blog website with React and TypeScript",
            "Deploy my application to production in us-central1",
            "Scale my API service to handle 1000 requests per second",
            "Delete the old test environment and all its resources",
            "What's the status of my blog deployment?",
            "Update my website to use the latest framework version",
            "Build a forum with user authentication",
        ]

        passed = 0
        failed = 0

        for request in test_requests:
            print(f"\n📝 Request: {request}")
            try:
                result = client.classify_intent(request)
                print(f"   Intent: {result.intent}")
                print(f"   Confidence: {result.confidence:.2f}")
                print(f"   Reasoning: {result.reasoning}")
                if result.extracted_entities:
                    print(f"   Entities: {result.extracted_entities}")
                passed += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1

        print(f"\n{'=' * 60}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'=' * 60}\n")

        return failed == 0

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_plan_generation():
    """Test plan generation"""
    print("\n" + "=" * 60)
    print("Plan Generation Test")
    print("=" * 60 + "\n")

    try:
        from llm import LLMClient

        client = LLMClient()

        # Test request
        request = "Create a blog website with user authentication, posts, comments, and admin panel"
        print(f"📝 Request: {request}\n")

        # Classify intent first
        classification = client.classify_intent(request)
        print(f"Intent: {classification.intent} (confidence: {classification.confidence})\n")

        # Generate plan
        context = {
            "available_regions": ["us-central1", "us-east1"],
            "user_policies": {
                "max_cost_usd_month": 100,
                "allowed_regions": ["us-central1"]
            }
        }

        plan = client.generate_plan(
            intent=classification.intent,
            user_request=request,
            context=context
        )

        print(f"📋 Generated Plan:\n")
        print(f"Estimated Duration: {plan.estimated_duration_seconds}s")
        print(f"Risk Level: {plan.risk_level}")
        print(f"\nRequired Resources:")
        for resource in plan.required_resources:
            print(f"  - {resource}")

        print(f"\nSteps:")
        for i, step in enumerate(plan.plan_steps, 1):
            print(f"  {i}. {step}")

        if plan.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in plan.warnings:
                print(f"  - {warning}")

        print(f"\n{'=' * 60}")
        print(f"✅ Plan generation successful")
        print(f"{'=' * 60}\n")

        return True

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("AI-Native Control Plane - LLM Integration Tests")
    print("=" * 60)

    # Check configuration
    if not test_llm_configuration():
        print("\n❌ LLM configuration invalid. Please set API keys.")
        print("\nFor OpenAI:")
        print("  export LLM_PROVIDER=openai")
        print("  export OPENAI_API_KEY=sk-...")
        print("\nFor Gemini:")
        print("  export LLM_PROVIDER=gemini")
        print("  export GEMINI_API_KEY=...")
        sys.exit(1)

    # Run tests
    tests = [
        ("Intent Classification", test_intent_classification),
        ("Plan Generation", test_plan_generation),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {e}")
            results[test_name] = False

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print()

    exit_code = 0 if passed == total else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
