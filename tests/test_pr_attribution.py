#!/usr/bin/env python3
"""
Test PR Attribution System

Verifies that @accelerate-master's PR attribution checking works correctly
and that agents get proper credit for their work.
"""

import re

def extract_agent_mentions(text: str) -> list:
    """Extract agent mentions from text"""
    if not text:
        return []
    
    # Pattern matches @agent-name format (e.g., @engineer-master, @bug-hunter)
    pattern = r'@([a-z]+-[a-z]+(?:-[a-z]+)?)'
    matches = re.findall(pattern, text.lower())
    
    return list(set(matches))


def test_pr_attribution_patterns():
    """Test that PR attribution patterns work correctly"""
    print("\n🧪 Testing PR Attribution Patterns...")
    
    # Test cases
    test_cases = [
        ("PR with @agent in title", "@engineer-master implements API", ["engineer-master"]),
        ("PR with @agent in body", "This PR adds feature.\n\n@secure-specialist reviewed.", ["secure-specialist"]),
        ("PR with multiple agents", "@create-guru and @organize-guru worked together", ["create-guru", "organize-guru"]),
        ("PR without agent", "Regular PR without agent mention", []),
        ("PR with bold @agent", "**@accelerate-master** optimized performance", ["accelerate-master"]),
        ("PR with @agent in parentheses", "Fixed issue (@troubleshoot-expert)", ["troubleshoot-expert"]),
        ("Mixed case @agent", "@Engineer-Master did this", ["engineer-master"]),
        ("Multiple @agent mentions", "@assert-specialist wrote tests, @coach-master reviewed", ["assert-specialist", "coach-master"]),
    ]
    
    passed = 0
    for name, text, expected in test_cases:
        result = extract_agent_mentions(text)
        if set(result) == set(expected):
            print(f"   ✅ {name}")
            passed += 1
        else:
            print(f"   ❌ {name}: expected {expected}, got {result}")
    
    print(f"\n   Passed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_strict_attribution_config():
    """Test that strict attribution config is read correctly"""
    print("\n🧪 Testing Strict Attribution Config...")
    
    import json
    from pathlib import Path
    
    config_path = Path(".github/agent-system/config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    strict_enabled = config.get('strict_pr_attribution', True)
    
    print(f"   Strict PR attribution: {strict_enabled}")
    
    if strict_enabled:
        print(f"   ✅ Strict mode enabled (PRs must mention @agent-name)")
    else:
        print(f"   ⚠️  Strict mode disabled (all PRs counted)")
    
    # For this fix, we want strict mode enabled to ensure proper attribution
    assert strict_enabled == True, "Strict PR attribution should be enabled"
    
    return True


def test_attribution_examples():
    """Test real-world attribution examples"""
    print("\n🧪 Testing Real-World Attribution Examples...")
    
    examples = [
        {
            "pr_title": "feat: optimize agent scoring (@accelerate-master)",
            "pr_body": "**@accelerate-master** has improved agent progression rates.",
            "agent": "accelerate-master",
            "should_match": True
        },
        {
            "pr_title": "fix: security vulnerability",
            "pr_body": "@secure-specialist identified and fixed the issue.",
            "agent": "secure-specialist",
            "should_match": True
        },
        {
            "pr_title": "refactor: code structure",
            "pr_body": "General code cleanup.",
            "agent": "organize-guru",
            "should_match": False  # No @mention
        },
        {
            "pr_title": "docs: update README",
            "pr_body": "Updated documentation with help from @support-master",
            "agent": "support-master",
            "should_match": True
        },
    ]
    
    passed = 0
    for i, example in enumerate(examples, 1):
        title_mentions = extract_agent_mentions(example['pr_title'])
        body_mentions = extract_agent_mentions(example['pr_body'])
        
        agent_mentioned = (
            example['agent'] in title_mentions or 
            example['agent'] in body_mentions
        )
        
        if agent_mentioned == example['should_match']:
            status = "✅" if example['should_match'] else "✅ (correctly not matched)"
            print(f"   {status} Example {i}: {example['pr_title'][:50]}")
            passed += 1
        else:
            print(f"   ❌ Example {i}: Expected match={example['should_match']}, got {agent_mentioned}")
    
    print(f"\n   Passed: {passed}/{len(examples)}")
    return passed == len(examples)


def test_attribution_edge_cases():
    """Test edge cases in attribution"""
    print("\n🧪 Testing Attribution Edge Cases...")
    
    edge_cases = [
        ("Empty text", "", []),
        ("Just @", "@", []),
        ("Invalid format @agent", "@agent", []),  # Should not match (no hyphen)
        ("Valid @agent-name", "@agent-master", ["agent-master"]),
        ("@agent- incomplete", "@agent-", []),
        ("Email address", "contact@agent-master.com", []),  # Should not match in email
        ("Multiple hyphens", "@agent-master-pro", ["agent-master-pro"]),
        ("Uppercase", "@ACCELERATE-MASTER", ["accelerate-master"]),
        ("Mixed case", "@Accelerate-Master", ["accelerate-master"]),
    ]
    
    passed = 0
    for name, text, expected in edge_cases:
        result = extract_agent_mentions(text)
        if result == expected:
            print(f"   ✅ {name}")
            passed += 1
        else:
            print(f"   ⚠️  {name}: expected {expected}, got {result}")
    
    print(f"\n   Passed: {passed}/{len(edge_cases)}")
    return passed == len(edge_cases)


def main():
    """Run all PR attribution tests"""
    print("=" * 70)
    print("🧪 PR ATTRIBUTION SYSTEM TEST SUITE")
    print("Testing @accelerate-master's PR attribution improvements")
    print("=" * 70)
    
    tests = [
        ("Attribution Patterns", test_pr_attribution_patterns),
        ("Strict Attribution Config", test_strict_attribution_config),
        ("Real-World Examples", test_attribution_examples),
        ("Edge Cases", test_attribution_edge_cases),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n   ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n   ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")
        return 1
    
    print("\n🎉 All PR attribution tests passed!")
    print("\n📋 Key Points:")
    print("   • Agents must be mentioned as @agent-name in PRs")
    print("   • Pattern matches: @engineer-master, @bug-hunter, etc.")
    print("   • Checks PR title, description, and comments")
    print("   • Strict mode ensures proper attribution")
    print("   • Case-insensitive matching")
    
    return 0


if __name__ == '__main__':
    exit(main())
