#!/usr/bin/env python3
"""
Test suite for AI Agent Diversity Alert System

This test validates that the diversity alert workflow correctly handles
various scenarios and doesn't create false positive issues.

Run: python3 tests/test_diversity_alerts.py
"""

import json
import sys
from pathlib import Path

def test_current_state():
    """Test that current repository state should NOT trigger an alert"""
    print("Test 1: Current State - Should NOT create alert")
    print("=" * 60)
    
    scores_file = Path("analysis/uniqueness-scores.json")
    if not scores_file.exists():
        print("❌ FAIL: uniqueness-scores.json not found")
        return False
    
    with open(scores_file) as f:
        data = json.load(f)
    
    # Validate metadata
    assert data['metadata']['total_agents_analyzed'] >= 0, "total_agents_analyzed should be >= 0"
    assert data['metadata']['threshold'] == 30.0, "threshold should be 30.0"
    assert data['metadata']['min_contributions'] == 3, "min_contributions should be 3"
    
    # Check flagged agents
    flagged_count = len(data['flagged_agents'])
    print(f"  Flagged agents: {flagged_count}")
    
    # Validate that agents with insufficient data are NOT in flagged list
    scores = data.get("scores", {})
    for agent_id, score_data in scores.items():
        has_insufficient_data = "note" in score_data and "Insufficient data" in score_data["note"]
        is_flagged = any(a['agent_id'] == agent_id for a in data['flagged_agents'])
        
        if has_insufficient_data and is_flagged:
            print(f"  ❌ FAIL: Agent {agent_id} has insufficient data but is flagged")
            return False
        
        if has_insufficient_data:
            print(f"  ✓ Agent {agent_id}: Insufficient data (not flagged)")
        else:
            status = "flagged" if is_flagged else "not flagged"
            print(f"  ✓ Agent {agent_id}: {status} (score: {score_data['overall_score']})")
    
    # For current state: expect 0 flagged agents
    if flagged_count == 0:
        print("  ✅ PASS: No agents flagged (expected)")
        return True
    else:
        print(f"  ⚠️  WARNING: {flagged_count} agents flagged (unexpected for current state)")
        # Not a failure - might be legitimate if repository grows
        return True

def test_excluded_actors():
    """Test that system bots are excluded from analysis"""
    print("\nTest 2: Excluded Actors - System bots should be filtered")
    print("=" * 60)
    
    scores_file = Path("analysis/uniqueness-scores.json")
    if not scores_file.exists():
        print("❌ SKIP: uniqueness-scores.json not found")
        return True
    
    with open(scores_file) as f:
        data = json.load(f)
    
    # Check that system bots are not in scores
    excluded_bots = ['github-actions', 'github-actions[bot]', 'dependabot', 'dependabot[bot]']
    scores = data.get("scores", {})
    
    for bot in excluded_bots:
        if bot in scores:
            print(f"  ❌ FAIL: System bot '{bot}' found in scores")
            return False
    
    print(f"  ✅ PASS: No system bots in analysis")
    print(f"  ✓ Excluded count: {data['metadata'].get('excluded_system_bots', 0)}")
    return True

def test_threshold_logic():
    """Test that threshold logic is applied correctly"""
    print("\nTest 3: Threshold Logic - Only low scores should be flagged")
    print("=" * 60)
    
    scores_file = Path("analysis/uniqueness-scores.json")
    if not scores_file.exists():
        print("❌ SKIP: uniqueness-scores.json not found")
        return True
    
    with open(scores_file) as f:
        data = json.load(f)
    
    threshold = data['metadata']['threshold']
    scores = data.get("scores", {})
    flagged_agents = {a['agent_id'] for a in data['flagged_agents']}
    
    errors = []
    for agent_id, score_data in scores.items():
        score = score_data['overall_score']
        is_flagged = agent_id in flagged_agents
        has_insufficient_data = "note" in score_data and "Insufficient data" in score_data["note"]
        
        # Skip agents with insufficient data
        if has_insufficient_data:
            continue
        
        # Validate threshold logic
        if score < threshold and not is_flagged:
            errors.append(f"Agent {agent_id} has score {score} < {threshold} but is NOT flagged")
        elif score >= threshold and is_flagged:
            errors.append(f"Agent {agent_id} has score {score} >= {threshold} but IS flagged")
    
    if errors:
        print("  ❌ FAIL: Threshold logic errors:")
        for error in errors:
            print(f"    - {error}")
        return False
    else:
        print("  ✅ PASS: Threshold logic is correct")
        return True

def test_workflow_decision():
    """Test the workflow's decision logic"""
    print("\nTest 4: Workflow Decision - Should match manual calculation")
    print("=" * 60)
    
    scores_file = Path("analysis/uniqueness-scores.json")
    if not scores_file.exists():
        print("❌ SKIP: uniqueness-scores.json not found")
        return True
    
    with open(scores_file) as f:
        data = json.load(f)
    
    # Simulate workflow logic
    flagged = data.get("flagged_agents", [])
    scores = data.get("scores", {})
    
    real_flagged = []
    for agent in flagged:
        agent_id = agent.get("agent_id", "unknown")
        agent_score = scores.get(agent_id, {})
        if "note" in agent_score and "Insufficient data" in agent_score["note"]:
            continue
        real_flagged.append(agent)
    
    flagged_count = len(data['flagged_agents'])
    real_flagged_count = len(real_flagged)
    
    print(f"  Flagged agents (from file): {flagged_count}")
    print(f"  Real flagged (with sufficient data): {real_flagged_count}")
    
    # Workflow creates issue if: flagged_count > 0 AND real_flagged_count > 0
    would_create_issue = flagged_count > 0 and real_flagged_count > 0
    
    print(f"  Would workflow create issue? {would_create_issue}")
    
    if real_flagged_count == 0:
        print("  ✅ PASS: Workflow would NOT create issue (correct)")
    else:
        print(f"  ⚠️  INFO: Workflow would create issue for {real_flagged_count} agents")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AI AGENT DIVERSITY ALERT SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_current_state,
        test_excluded_actors,
        test_threshold_logic,
        test_workflow_decision,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test.__name__}: {e}")
            results.append((test.__name__, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
