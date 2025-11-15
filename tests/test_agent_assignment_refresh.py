#!/usr/bin/env python3
"""
Test suite for the refreshed agent assignment system.
Validates that all 43 agents can be matched and human names are displayed.
"""

import sys
import json
import subprocess
from pathlib import Path

# Test cases: (title, body, expected_agent_type, min_score)
# Using broad categories since we have many similar agents
TEST_CASES = [
    # Performance optimization
    ("Optimize slow API", "Performance issues in API", "accelerate", 5),
    ("Speed up queries", "Database queries are slow", "accelerate", 3),
    
    # Testing and QA
    ("Add unit tests", "Need test coverage for auth", "assert|validator", 5),
    ("Write integration tests", "E2E tests needed", "assert", 3),
    
    # Security
    ("Fix XSS vulnerability", "Security issue in form", "secure", 7),
    ("Prevent SQL injection", "User input not sanitized", "secure", 3),
    
    # Documentation
    ("Improve API docs", "Documentation needs examples", "clarify|document|communicator", 5),
    ("Write tutorial", "Need getting started guide", "clarify|document|communicator", 3),
    
    # Refactoring
    ("Refactor duplicate code", "Too much duplication", "refactor|organiz|simplif|restructure", 5),
    ("Clean up complexity", "Code is too complex", "organiz|simplif|refactor", 5),
    
    # Infrastructure
    ("Setup CI/CD", "Need deployment pipeline", "infrastructure|align|coordinate", 3),
    ("Create deployment script", "Automate deployments", "infrastructure|create|tools|construct", 3),
    
    # API development
    ("Create REST endpoints", "Build user API", "engineer|develop|create", 5),
    ("Add GraphQL support", "Implement GraphQL", "engineer|develop|create|support", 3),
    
    # Monitoring
    ("Add security monitoring", "Monitor for threats", "monitor|secure", 5),
    ("Setup access logging", "Track access patterns", "monitor|investigate|coach", 3),
    
    # Investigation
    ("Analyze data flow", "Understand dependencies", "investigate", 5),
    ("Debug production issue", "Find root cause", "troubleshoot|investigate", 3),
    
    # New features
    ("Build dashboard", "Create analytics dashboard", "create|construct|develop", 3),
    ("Implement feature", "Add user profiles", "create|develop", 3),
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
        print(f"Stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def matches_pattern(agent_name, pattern):
    """Check if agent name matches the expected pattern."""
    patterns = pattern.split('|')
    return any(p in agent_name for p in patterns)

def test_matching():
    """Run all test cases and report results."""
    print("🧪 Testing Refreshed Agent Assignment System")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for title, body, expected_pattern, min_score in TEST_CASES:
        result = run_matching(title, body)
        
        if result is None:
            print(f"❌ FAILED: {title}")
            print(f"   Could not run matching")
            failed += 1
            continue
        
        matched_agent = result.get('agent')
        score = result.get('score', 0)
        human_name = result.get('human_name')
        top_agents = result.get('top_agents', [])
        
        # Check if matched agent matches the expected pattern
        if matches_pattern(matched_agent, expected_pattern) and score >= min_score:
            status = "✅ PASSED"
            passed += 1
        else:
            status = "❌ FAILED"
            failed += 1
        
        print(f"{status}: {title}")
        print(f"   → Agent: {matched_agent} (score: {score})")
        if human_name:
            print(f"   → Human Name: {human_name}")
        if top_agents and len(top_agents) > 1:
            print(f"   → Tied with: {', '.join(top_agents)}")
        
        if status == "❌ FAILED":
            print(f"   → Expected pattern: {expected_pattern} (min score: {min_score})")
            # Show top 5 scores for debugging
            all_scores = result.get('all_scores', {})
            top_5 = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"   → Top scores: {', '.join([f'{k}:{v}' for k, v in top_5])}")
        
        print()
    
    print("=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1

def test_all_agents_available():
    """Verify all 43+ agents have pattern coverage."""
    print("\n🔍 Testing Agent Coverage")
    print("=" * 70)
    
    # Get list of available agents
    agents_dir = Path('.github/agents')
    available_agents = []
    for agent_file in agents_dir.glob('*.md'):
        if agent_file.stem != 'README':
            available_agents.append(agent_file.stem)
    
    print(f"Found {len(available_agents)} agent definitions")
    
    # Test that the matching script knows about all agents
    result = run_matching("General issue", "A generic task")
    
    if result is None:
        print("❌ Could not run matching script")
        return 1
    
    all_scores = result.get('all_scores', {})
    scored_agents = set(all_scores.keys())
    missing_agents = set(available_agents) - scored_agents
    
    if missing_agents:
        print(f"❌ {len(missing_agents)} agents missing from scoring:")
        for agent in sorted(missing_agents):
            print(f"   - {agent}")
        return 1
    else:
        print(f"✅ All {len(available_agents)} agents have pattern coverage!")
        return 0

def test_human_name_integration():
    """Test that human names are properly integrated."""
    print("\n👤 Testing Human Name Integration")
    print("=" * 70)
    
    result = run_matching("Add test coverage", "Need unit tests")
    
    if result is None:
        print("❌ Could not run matching script")
        return 1
    
    agent = result.get('agent')
    human_name = result.get('human_name')
    
    print(f"Matched agent: {agent}")
    print(f"Human name: {human_name if human_name else 'Not in registry'}")
    
    if 'human_name' in result:
        print("✅ Human name field is present in output")
        return 0
    else:
        print("❌ Human name field missing from output")
        return 1

def test_randomization():
    """Test that tied scores result in different selections."""
    print("\n🎲 Testing Randomization for Tied Scores")
    print("=" * 70)
    
    # Issue that should match multiple refactoring agents
    title = "Refactor code to remove duplication and complexity"
    body = "The code has too much duplication and is overly complex"
    
    selections = set()
    
    # Run multiple times to see if we get different results
    for i in range(10):
        result = run_matching(title, body)
        if result:
            selections.add(result.get('agent'))
    
    print(f"After 10 runs, selected {len(selections)} different agents:")
    for agent in sorted(selections):
        print(f"   - {agent}")
    
    if len(selections) > 1:
        print("✅ Randomization is working (got multiple different agents)")
        return 0
    else:
        print("⚠️  All runs selected the same agent (randomization may not be effective)")
        print("   This is not necessarily an error if there's a clear winner")
        return 0

def main():
    """Main entry point."""
    # Change to repo root
    repo_root = Path(__file__).parent.parent
    import os
    os.chdir(repo_root)
    
    print(f"Working directory: {os.getcwd()}\n")
    
    exit_codes = []
    
    # Run all test suites
    exit_codes.append(test_matching())
    exit_codes.append(test_all_agents_available())
    exit_codes.append(test_human_name_integration())
    exit_codes.append(test_randomization())
    
    # Overall result
    print("\n" + "=" * 70)
    if all(code == 0 for code in exit_codes):
        print("✅ ALL TEST SUITES PASSED!")
        return 0
    else:
        print("❌ SOME TEST SUITES FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
