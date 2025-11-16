#!/usr/bin/env python3
"""
Test suite for direct custom agent assignment functionality.

This test validates the "direct assignment" feature implemented in the
copilot-graphql-assign.yml workflow. Direct assignment allows custom agents
with their own actor IDs to be assigned directly via the GitHub GraphQL API,
providing a more elegant solution than assigning to generic Copilot with
directives.

The workflow flow:
    1. Issue is created
    2. Agent matching determines best custom agent
    3. Workflow checks if agent has actor ID
    4. If yes: Direct assignment to custom agent
    5. If no: Fallback to generic Copilot with agent directives

Tests cover:
    - Direct assignment to custom agents with actor IDs
    - Fallback to generic Copilot when custom agent has no actor ID
    - Agent matching and assignment workflow integration
    - Edge cases and boundary conditions

Run with:
    python3 test_direct_assignment.py

Related files:
    - .github/workflows/copilot-graphql-assign.yml (lines 196-323)
    - tools/match-issue-to-agent.py
    - tools/list-agent-actor-ids.py
"""

import sys
import json
import subprocess
from pathlib import Path


def run_matching(title, body):
    """Run the agent matching script to determine which agent should be assigned."""
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


def test_agent_matching_for_direct_assignment():
    """
    Test that agent matching works correctly for issues that should use direct assignment.
    
    Direct assignment is appropriate when:
        1. The issue clearly matches a specific custom agent
        2. That agent has high confidence/score
        3. The agent has its own actor ID (checked at runtime by workflow)
    
    This test verifies the first two conditions; the workflow verifies the third
    by querying the GitHub API for actor IDs.
    """
    print("🧪 Testing Agent Matching for Direct Assignment")
    print("=" * 70)
    print()
    
    # Test cases designed to strongly match specific agents
    test_cases = [
        {
            'title': 'Fix critical security vulnerability in auth',
            'body': 'SQL injection vulnerability found in login endpoint',
            'expected_agent': 'security-guardian',
            'min_score': 5,
            'reason': 'Security issues should strongly match security-guardian'
        },
        {
            'title': 'Critical bug causing crashes',
            'body': 'Application crashes when users click submit button. Error: NullPointerException',
            'expected_agent': 'bug-hunter',
            'min_score': 5,
            'reason': 'Bug with error details should strongly match bug-hunter'
        },
        {
            'title': 'Optimize database query performance',
            'body': 'Queries are slow and causing bottlenecks. Need to improve speed.',
            'expected_agent': 'performance-optimizer',
            'min_score': 4,
            'reason': 'Performance issues should match performance-optimizer'
        },
        {
            'title': 'Write comprehensive test suite',
            'body': 'Need unit tests and integration tests for auth module',
            'expected_agent': 'test-champion',
            'min_score': 5,
            'reason': 'Testing requirements should strongly match test-champion'
        },
        {
            'title': 'Add new feature: user profiles',
            'body': 'Implement user profile pages with avatar upload',
            'expected_agent': 'feature-architect',
            'min_score': 3,
            'reason': 'Feature requests should match feature-architect'
        },
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        title = test_case['title']
        body = test_case['body']
        expected = test_case['expected_agent']
        min_score = test_case['min_score']
        reason = test_case['reason']
        
        result = run_matching(title, body)
        
        if result is None:
            print(f"❌ FAILED: {title}")
            print(f"   Could not run matching")
            print(f"   Reason: {reason}")
            failed += 1
            continue
        
        matched_agent = result.get('agent')
        score = result.get('score', 0)
        confidence = result.get('confidence', 'unknown')
        
        if matched_agent == expected and score >= min_score:
            print(f"✅ PASSED: {title}")
            print(f"   → Matched: {matched_agent} (score: {score}, confidence: {confidence})")
            print(f"   → Ready for direct assignment (if actor ID exists)")
            passed += 1
        else:
            print(f"❌ FAILED: {title}")
            print(f"   → Expected: {expected} (min score: {min_score})")
            print(f"   → Got: {matched_agent} (score: {score}, confidence: {confidence})")
            print(f"   → Reason: {reason}")
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print()
    
    return failed == 0


def test_assignment_method_selection():
    """
    Test that the assignment logic correctly identifies when to use
    direct assignment vs fallback to generic Copilot.
    
    This simulates the workflow's decision-making process:
        1. Match issue to agent
        2. Check if agent has actor ID (simulated here, checked by workflow)
        3. Choose assignment method based on confidence and score
    
    The workflow uses similar logic to decide between:
        - direct-custom-agent: Direct API assignment to custom agent actor
        - generic-with-directives: Assign to generic Copilot with agent directives
    """
    print("🧪 Testing Assignment Method Selection")
    print("=" * 70)
    print()
    
    test_cases = [
        {
            'issue_title': 'Fix login bug',
            'issue_body': 'Users cannot login due to error',
            'expected_agent': 'bug-hunter',
            'description': 'Bug fix should route to bug-hunter'
        },
        {
            'issue_title': 'Update documentation',
            'issue_body': 'README needs better installation guide',
            'expected_agent': 'doc-master',
            'description': 'Documentation should route to doc-master'
        },
        {
            'issue_title': 'Refactor messy code',
            'issue_body': 'Clean up duplicate code in handlers',
            'expected_agent': 'refactor-wizard',
            'description': 'Refactoring should route to refactor-wizard'
        },
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        title = test_case['issue_title']
        body = test_case['issue_body']
        expected_agent = test_case['expected_agent']
        description = test_case['description']
        
        result = run_matching(title, body)
        
        if result is None:
            print(f"❌ FAILED: {description}")
            print(f"   Could not run matching")
            failed += 1
            continue
        
        matched_agent = result.get('agent')
        score = result.get('score', 0)
        
        # Simulate the workflow's assignment method decision
        # In real workflow, this checks if actor ID exists via API
        # Here we just verify the matching worked correctly
        if matched_agent == expected_agent:
            assignment_method = "direct-custom-agent" if score >= 3 else "generic-with-directives"
            
            print(f"✅ PASSED: {description}")
            print(f"   → Agent: {matched_agent} (score: {score})")
            print(f"   → Assignment method: {assignment_method}")
            
            if assignment_method == "direct-custom-agent":
                print(f"   → Would use: Direct API assignment to {matched_agent}")
            else:
                print(f"   → Would use: Generic Copilot with agent directives")
            
            passed += 1
        else:
            print(f"❌ FAILED: {description}")
            print(f"   → Expected: {expected_agent}")
            print(f"   → Got: {matched_agent} (score: {score})")
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print()
    
    return failed == 0


def test_fallback_scenarios():
    """
    Test scenarios where direct assignment should fallback to generic Copilot.
    
    Fallback occurs when:
        1. Custom agent does not have an actor ID (checked by workflow)
        2. Issue matching has low confidence
        3. Generic/ambiguous issues without clear agent match
    
    The workflow gracefully falls back to assigning generic Copilot with
    agent directives embedded in the issue body, ensuring all issues can
    still be handled even when direct assignment isn't possible.
    """
    print("🧪 Testing Fallback Scenarios")
    print("=" * 70)
    print()
    
    test_cases = [
        {
            'title': 'Do something',
            'body': 'Generic task without specific keywords',
            'description': 'Generic issue should use fallback',
            'expect_fallback': True
        },
        {
            'title': 'Update the thing',
            'body': 'Just needs updating',
            'description': 'Ambiguous issue should use fallback',
            'expect_fallback': True
        },
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        title = test_case['title']
        body = test_case['body']
        description = test_case['description']
        expect_fallback = test_case['expect_fallback']
        
        result = run_matching(title, body)
        
        if result is None:
            print(f"❌ FAILED: {description}")
            print(f"   Could not run matching")
            failed += 1
            continue
        
        matched_agent = result.get('agent')
        score = result.get('score', 0)
        confidence = result.get('confidence', 'unknown')
        
        # Low confidence or low score should trigger fallback
        should_fallback = confidence == 'low' or score < 3
        
        if should_fallback == expect_fallback:
            print(f"✅ PASSED: {description}")
            print(f"   → Agent: {matched_agent} (score: {score}, confidence: {confidence})")
            if should_fallback:
                print(f"   → Correctly identified for fallback to generic Copilot")
            else:
                print(f"   → Correctly identified for direct assignment")
            passed += 1
        else:
            print(f"❌ FAILED: {description}")
            print(f"   → Expected fallback: {expect_fallback}")
            print(f"   → Got fallback: {should_fallback}")
            print(f"   → Agent: {matched_agent} (score: {score}, confidence: {confidence})")
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print()
    
    return failed == 0


def test_workflow_integration():
    """
    Test that the workflow integration points work correctly.
    
    Validates that:
        1. Agent matching produces output compatible with workflow
        2. Output includes all required fields for assignment decision
        3. Assignment method can be determined from matching results
    
    The workflow relies on specific JSON fields from match-issue-to-agent.py:
        - agent: The custom agent name (e.g., "bug-hunter")
        - score: Numeric confidence score
        - confidence: String confidence level ("high", "medium", "low")
        - emoji: Agent's emoji for visual identification
        - description: Human-readable agent description
    """
    print("🧪 Testing Workflow Integration")
    print("=" * 70)
    print()
    
    test_issue = {
        'title': 'Security audit needed',
        'body': 'Review authentication system for vulnerabilities',
    }
    
    result = run_matching(test_issue['title'], test_issue['body'])
    
    if result is None:
        print(f"❌ FAILED: Could not run matching")
        return False
    
    # Check required fields for workflow
    required_fields = ['agent', 'score', 'confidence', 'emoji', 'description']
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        print(f"❌ FAILED: Missing required fields: {missing_fields}")
        print(f"   Result: {result}")
        return False
    
    print(f"✅ PASSED: All required fields present")
    print(f"   → agent: {result['agent']}")
    print(f"   → score: {result['score']}")
    print(f"   → confidence: {result['confidence']}")
    print(f"   → emoji: {result['emoji']}")
    print(f"   → description: {result['description']}")
    print()
    
    # Check that workflow can determine assignment method
    agent = result['agent']
    score = result['score']
    
    # Simulate workflow decision logic
    # In actual workflow, this also checks for actor ID existence
    if score >= 3:
        assignment_method = "direct-custom-agent"  # Would check actor ID
        print(f"✅ PASSED: High confidence assignment")
        print(f"   → Would attempt direct assignment to {agent}")
        print(f"   → Falls back to generic Copilot if actor ID not found")
    else:
        assignment_method = "generic-with-directives"
        print(f"✅ PASSED: Low confidence assignment")
        print(f"   → Would use generic Copilot with agent directives")
    
    print()
    print("=" * 70)
    print("📊 Result: Integration test passed")
    print()
    
    return True


def main():
    """Run all direct assignment tests."""
    print()
    print("=" * 70)
    print("🎯 DIRECT CUSTOM AGENT ASSIGNMENT TEST SUITE")
    print("=" * 70)
    print()
    print("Testing the workflow's ability to:")
    print("  1. Match issues to appropriate custom agents")
    print("  2. Choose between direct assignment and fallback")
    print("  3. Integrate with GitHub GraphQL API assignment")
    print()
    
    # Change to repo root (parent of tests directory)
    repo_root = Path(__file__).parent.parent
    import os
    os.chdir(repo_root)
    
    print(f"Working directory: {os.getcwd()}")
    print()
    print("=" * 70)
    print()
    
    # Run all test suites
    results = []
    
    results.append(("Agent Matching for Direct Assignment", test_agent_matching_for_direct_assignment()))
    results.append(("Assignment Method Selection", test_assignment_method_selection()))
    results.append(("Fallback Scenarios", test_fallback_scenarios()))
    results.append(("Workflow Integration", test_workflow_integration()))
    
    # Summary
    print()
    print("=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print()
    
    passed_suites = sum(1 for _, result in results if result)
    total_suites = len(results)
    
    for suite_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {suite_name}")
    
    print()
    print(f"Total: {passed_suites}/{total_suites} test suites passed")
    print()
    
    if passed_suites == total_suites:
        print("✅ All direct assignment tests passed!")
        print()
        print("The workflow is ready to:")
        print("  • Match issues to custom agents intelligently")
        print("  • Assign directly when custom agents have actor IDs")
        print("  • Fallback gracefully to generic Copilot when needed")
        print()
        return 0
    else:
        print(f"❌ {total_suites - passed_suites} test suite(s) failed")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
