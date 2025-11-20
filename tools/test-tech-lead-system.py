#!/usr/bin/env python3
"""
Test script to verify the tech lead system components.

This script tests:
1. All tech lead agents can be loaded
2. No duplicate path patterns exist
3. Path pattern matching works correctly
4. All tech leads have required fields
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import from the match script
import importlib.util
spec = importlib.util.spec_from_file_location(
    "match_pr_to_tech_lead",
    Path(__file__).parent / "match-pr-to-tech-lead.py"
)
match_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(match_module)

load_tech_leads = match_module.load_tech_leads
match_file_to_tech_leads = match_module.match_file_to_tech_leads
parse_tech_lead_agent = match_module.parse_tech_lead_agent
AGENTS_DIR = match_module.AGENTS_DIR

def test_load_tech_leads():
    """Test that all tech leads can be loaded."""
    print("=" * 60)
    print("TEST 1: Loading Tech Lead Agents")
    print("=" * 60)
    
    tech_leads = load_tech_leads()
    
    if not tech_leads:
        print("❌ FAIL: No tech leads found!")
        return False
    
    print(f"✅ PASS: Found {len(tech_leads)} tech leads")
    for tl in tech_leads:
        print(f"  • {tl['name']}: {tl['specialization']}")
    
    return True

def test_required_fields():
    """Test that all tech leads have required fields."""
    print("\n" + "=" * 60)
    print("TEST 2: Required Fields")
    print("=" * 60)
    
    tech_leads = load_tech_leads()
    required_fields = ['name', 'description', 'paths', 'specialization']
    
    all_valid = True
    for tl in tech_leads:
        missing = [f for f in required_fields if not tl.get(f)]
        if missing:
            print(f"❌ FAIL: {tl.get('name', 'UNKNOWN')} missing fields: {missing}")
            all_valid = False
        else:
            print(f"✅ PASS: {tl['name']} has all required fields")
    
    return all_valid

def test_no_duplicate_paths():
    """Test that no tech leads have overlapping path patterns."""
    print("\n" + "=" * 60)
    print("TEST 3: No Duplicate Path Patterns")
    print("=" * 60)
    
    tech_leads = load_tech_leads()
    
    # Collect all patterns
    all_patterns = {}
    for tl in tech_leads:
        for pattern in tl['paths']:
            if pattern in all_patterns:
                print(f"⚠️  WARNING: Pattern '{pattern}' used by multiple tech leads:")
                print(f"    • {all_patterns[pattern]}")
                print(f"    • {tl['name']}")
            else:
                all_patterns[pattern] = tl['name']
    
    if len(all_patterns) == sum(len(tl['paths']) for tl in tech_leads):
        print(f"✅ PASS: All {len(all_patterns)} path patterns are unique")
        return True
    else:
        print(f"❌ FAIL: Some path patterns are duplicated")
        return False

def test_path_matching():
    """Test that path matching works correctly."""
    print("\n" + "=" * 60)
    print("TEST 4: Path Pattern Matching")
    print("=" * 60)
    
    tech_leads = load_tech_leads()
    
    test_cases = [
        (".github/workflows/test.yml", "workflows-tech-lead"),
        (".github/agents/test-agent.md", "agents-tech-lead"),
        ("docs/README.md", "docs-tech-lead"),
        ("docs/index.html", "github-pages-tech-lead"),
        ("tools/match-issue-to-agent.py", "agents-tech-lead"),
        ("README.md", "docs-tech-lead"),
        (".github/actions/setup/action.yml", "workflows-tech-lead"),
        ("docs/style.css", "github-pages-tech-lead"),
        ("docs/script.js", "github-pages-tech-lead"),
    ]
    
    all_pass = True
    for filepath, expected_tech_lead in test_cases:
        matched = match_file_to_tech_leads(filepath, tech_leads)
        matched_names = [m['name'] for m in matched]
        
        if expected_tech_lead in matched_names:
            print(f"✅ PASS: '{filepath}' → {matched_names}")
        else:
            print(f"❌ FAIL: '{filepath}' should match {expected_tech_lead}, got {matched_names}")
            all_pass = False
    
    return all_pass

def test_tech_lead_definitions():
    """Test that all tech lead definition files are valid."""
    print("\n" + "=" * 60)
    print("TEST 5: Tech Lead Definition Files")
    print("=" * 60)
    
    if not AGENTS_DIR.exists():
        print(f"❌ FAIL: Agents directory not found: {AGENTS_DIR}")
        return False
    
    tech_lead_files = list(AGENTS_DIR.glob("*tech-lead.md"))
    
    if not tech_lead_files:
        print(f"❌ FAIL: No tech lead files found in {AGENTS_DIR}")
        return False
    
    all_valid = True
    for filepath in tech_lead_files:
        agent_data = parse_tech_lead_agent(filepath)
        if agent_data:
            print(f"✅ PASS: {filepath.name} is valid")
        else:
            print(f"❌ FAIL: {filepath.name} failed to parse")
            all_valid = False
    
    return all_valid

def test_expected_tech_leads():
    """Test that all expected tech leads exist."""
    print("\n" + "=" * 60)
    print("TEST 6: Expected Tech Leads Present")
    print("=" * 60)
    
    expected = [
        "workflows-tech-lead",
        "agents-tech-lead",
        "docs-tech-lead",
        "github-pages-tech-lead"
    ]
    
    tech_leads = load_tech_leads()
    tech_lead_names = [tl['name'] for tl in tech_leads]
    
    all_found = True
    for expected_name in expected:
        if expected_name in tech_lead_names:
            print(f"✅ PASS: Found {expected_name}")
        else:
            print(f"❌ FAIL: Missing {expected_name}")
            all_found = False
    
    return all_found

def main():
    """Run all tests."""
    print("\n" + "🔬 Tech Lead System Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Load Tech Leads", test_load_tech_leads),
        ("Required Fields", test_required_fields),
        ("No Duplicate Paths", test_no_duplicate_paths),
        ("Path Matching", test_path_matching),
        ("Definition Files", test_tech_lead_definitions),
        ("Expected Tech Leads", test_expected_tech_leads),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
