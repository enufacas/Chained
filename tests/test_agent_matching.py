#!/usr/bin/env python3
"""
Test suite for the intelligent agent matching system.
Validates that issues are correctly matched to specialized agents.
"""

import sys
import json
import subprocess
from pathlib import Path

# Test cases: (title, body, expected_agent, min_score)
TEST_CASES = [
    # Bug-related issues
    ("Fix crash in login module", "Users experiencing crashes when logging in", "bug-hunter", 3),
    ("Error handling broken", "Exceptions are not being caught properly", "bug-hunter", 3),
    
    # Feature-related issues
    ("Add user profile feature", "Implement user profile pages with avatars", "feature-architect", 3),
    ("Create dashboard", "Build a new analytics dashboard", "feature-architect", 3),
    ("New capability needed", "We need to add export functionality", "feature-architect", 3),
    
    # Documentation issues
    ("Update README", "The installation guide needs improvement", "doc-master", 3),
    ("Add API documentation", "Document all API endpoints", "doc-master", 3),
    ("Write tutorial", "Create a getting started guide", "doc-master", 3),
    
    # Testing issues
    ("Improve test coverage", "Add unit tests for auth module", "test-champion", 3),
    ("Write integration tests", "We need e2e tests for checkout flow", "test-champion", 3),
    
    # Performance issues
    ("Slow page load", "Dashboard takes 10 seconds to load", "performance-optimizer", 3),
    ("Optimize database queries", "Queries are causing bottlenecks", "performance-optimizer", 3),
    
    # Security issues
    ("Security vulnerability", "XSS possible in comment form", "security-guardian", 3),
    ("Fix SQL injection", "User input not sanitized in search", "security-guardian", 3),
    
    # Code quality issues
    ("Refactor handlers", "Too much duplicate code in handlers", "refactor-wizard", 3),
    ("Clean up code", "Code needs better formatting and style", "code-poet", 2),
    
    # Integration issues
    ("Add Stripe integration", "Integrate payment processing", "integration-specialist", 3),
    ("Connect to external API", "We need to call third-party service", "integration-specialist", 3),
    
    # UX issues
    ("Improve UI design", "The interface needs better colors", "ux-enhancer", 3),
    ("Accessibility issues", "Screen readers can't navigate site", "ux-enhancer", 3),
]

def run_matching(title, body):
    """Run the matching script and return parsed result."""
    try:
        result = subprocess.run(
            ['python3', 'tools/match-issue-to-agent.py', title, body],
            capture_output=True,
            text=True,
            check=True,
            cwd='.'
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running matching script: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Output was: {result.stdout if 'result' in locals() else 'N/A'}")
        return None

def test_matching():
    """Run all test cases and report results."""
    print("🧪 Testing Intelligent Agent Matching System")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    for title, body, expected_agent, min_score in TEST_CASES:
        result = run_matching(title, body)
        
        if result is None:
            print(f"❌ FAILED: {title}")
            print(f"   Could not run matching")
            failed += 1
            continue
        
        matched_agent = result.get('agent')
        score = result.get('score', 0)
        
        # Check if matched agent is correct
        if matched_agent == expected_agent and score >= min_score:
            print(f"✅ PASSED: {title}")
            print(f"   → Matched: {matched_agent} (score: {score})")
            passed += 1
        else:
            print(f"❌ FAILED: {title}")
            print(f"   → Expected: {expected_agent} (min score: {min_score})")
            print(f"   → Got: {matched_agent} (score: {score})")
            print(f"   → All scores: {result.get('all_scores', {})}")
            failed += 1
        
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1

def main():
    """Main entry point."""
    # Change to repo root
    repo_root = Path(__file__).parent
    import os
    os.chdir(repo_root)
    
    print(f"Working directory: {os.getcwd()}")
    
    return test_matching()

if __name__ == "__main__":
    sys.exit(main())
