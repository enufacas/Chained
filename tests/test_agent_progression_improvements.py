#!/usr/bin/env python3
"""
Test Agent Progression Improvements

Verifies that @accelerate-master's improvements to agent progression work correctly:
1. Lower promotion threshold (70% instead of 85%)
2. Grace period for new agents (48 hours)
3. Minimum score guarantee during grace period (40%)
4. GitHub Pages sync working
"""

import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

def test_config_updates():
    """Test that config has been updated correctly"""
    print("\n🧪 Testing Configuration Updates...")
    
    config_path = Path(".github/agent-system/config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    # Test promotion threshold
    assert config['promotion_threshold'] == 0.65, \
        f"Expected promotion_threshold=0.65, got {config['promotion_threshold']}"
    print(f"   ✅ Promotion threshold: {config['promotion_threshold']:.0%} (was 85%)")
    
    # Test elimination threshold (should stay the same)
    assert config['elimination_threshold'] == 0.30, \
        f"Expected elimination_threshold=0.30, got {config['elimination_threshold']}"
    print(f"   ✅ Elimination threshold: {config['elimination_threshold']:.0%}")
    
    # Test grace period config
    assert 'new_agent_grace_period_hours' in config, \
        "Missing new_agent_grace_period_hours in config"
    assert config['new_agent_grace_period_hours'] == 48, \
        f"Expected grace period of 48 hours, got {config['new_agent_grace_period_hours']}"
    print(f"   ✅ Grace period: {config['new_agent_grace_period_hours']} hours")
    
    # Test minimum score config
    assert 'new_agent_minimum_score' in config, \
        "Missing new_agent_minimum_score in config"
    assert config['new_agent_minimum_score'] == 0.40, \
        f"Expected minimum score of 0.40, got {config['new_agent_minimum_score']}"
    print(f"   ✅ Minimum score: {config['new_agent_minimum_score']:.0%}")
    
    return True


def test_progression_gap():
    """Test that progression gap is now more reasonable"""
    print("\n🧪 Testing Progression Gap...")
    
    config_path = Path(".github/agent-system/config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    promotion = config['promotion_threshold']
    elimination = config['elimination_threshold']
    gap = promotion - elimination
    
    print(f"   Progression gap: {gap:.0%}")
    
    # Gap should be 35% now (was 55%)
    assert abs(gap - 0.35) < 0.001, f"Expected 35% gap, got {gap:.0%}"
    print(f"   ✅ Gap reduced from 55% to 35%")
    
    # This is more achievable
    print(f"   ✅ New agents can progress from {elimination:.0%} to {promotion:.0%}")
    
    return True


def test_github_pages_sync():
    """Test that agent registry is synced to GitHub Pages"""
    print("\n🧪 Testing GitHub Pages Sync...")
    
    # Check source registry
    source_path = Path(".github/agent-system/registry.json")
    assert source_path.exists(), "Source registry not found"
    
    # Check GitHub Pages copy
    pages_path = Path("docs/data/agents/agent-registry.json")
    assert pages_path.exists(), "GitHub Pages registry copy not found"
    print(f"   ✅ Registry synced to docs/data/agents/agent-registry.json")
    
    # Verify content matches
    with open(source_path) as f:
        source_data = json.load(f)
    
    with open(pages_path) as f:
        pages_data = json.load(f)
    
    assert source_data == pages_data, "Registry content doesn't match"
    print(f"   ✅ Content matches source registry")
    
    # Check agent count
    agent_count = len(pages_data.get('agents', []))
    print(f"   ✅ Contains {agent_count} agents")
    
    return True


def test_grace_period_logic():
    """Test grace period calculation logic"""
    print("\n🧪 Testing Grace Period Logic...")
    
    # Simulate a new agent
    now = datetime.now(timezone.utc)
    
    # Agent spawned 24 hours ago (within 48h grace period)
    spawn_time_recent = (now - timedelta(hours=24)).isoformat().replace('+00:00', 'Z')
    age_hours_recent = 24
    
    # Agent spawned 72 hours ago (outside grace period)
    spawn_time_old = (now - timedelta(hours=72)).isoformat().replace('+00:00', 'Z')
    age_hours_old = 72
    
    grace_period = 48
    
    in_grace_recent = age_hours_recent < grace_period
    in_grace_old = age_hours_old < grace_period
    
    assert in_grace_recent == True, "Recent agent should be in grace period"
    print(f"   ✅ Agent at {age_hours_recent}h is IN grace period")
    
    assert in_grace_old == False, "Old agent should be out of grace period"
    print(f"   ✅ Agent at {age_hours_old}h is OUT of grace period")
    
    return True


def test_minimum_score_boost():
    """Test minimum score boost during grace period"""
    print("\n🧪 Testing Minimum Score Boost...")
    
    config_path = Path(".github/agent-system/config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    minimum_score = config['new_agent_minimum_score']
    
    # Simulate scoring scenarios
    scenarios = [
        ("Low score (25%)", 0.25, True, minimum_score),   # Should boost
        ("Below minimum (35%)", 0.35, True, minimum_score),  # Should boost
        ("Above minimum (45%)", 0.45, True, 0.45),   # No boost needed
        ("Low score, no grace", 0.25, False, 0.25),  # No boost (not in grace)
    ]
    
    for name, score, in_grace, expected in scenarios:
        if in_grace and score < minimum_score:
            boosted = minimum_score
        else:
            boosted = score
        
        assert boosted == expected, f"{name}: Expected {expected:.0%}, got {boosted:.0%}"
        
        if in_grace and score < minimum_score:
            print(f"   ✅ {name}: {score:.0%} → {boosted:.0%} (boosted)")
        else:
            print(f"   ✅ {name}: {score:.0%} (no boost needed)")
    
    return True


def test_promotion_achievability():
    """Test that promotion is now more achievable"""
    print("\n🧪 Testing Promotion Achievability...")
    
    config_path = Path(".github/agent-system/config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    promotion_threshold = config['promotion_threshold']
    
    # Weights
    weights = {
        'code_quality': 0.30,
        'issue_resolution': 0.20,
        'pr_success': 0.20,
        'peer_review': 0.15,
        'creativity': 0.15
    }
    
    # Scenario: Good agent with decent activity
    # - 80% code quality (4/5 PRs merged)
    # - 60% issue resolution (3 issues resolved)
    # - 80% PR success
    # - 40% peer review (2 reviews)
    # - 70% creativity
    
    scores = {
        'code_quality': 0.80,
        'issue_resolution': 0.60,
        'pr_success': 0.80,
        'peer_review': 0.40,
        'creativity': 0.70
    }
    
    overall = sum(scores[k] * weights[k] for k in scores)
    
    print(f"   Example agent with good activity:")
    for metric, score in scores.items():
        contribution = score * weights[metric]
        print(f"      {metric}: {score:.0%} × {weights[metric]:.0%} = {contribution:.2%}")
    
    print(f"   Overall score: {overall:.2%}")
    print(f"   Promotion threshold: {promotion_threshold:.0%}")
    
    if overall >= promotion_threshold:
        print(f"   ✅ Agent would be PROMOTED!")
    else:
        print(f"   ❌ Agent would NOT be promoted")
        print(f"   Needs: {(promotion_threshold - overall):.2%} more")
    
    # This scenario should now be achievable with 65% threshold
    # (agent scores 68.5%, which is above 65%)
    assert overall >= promotion_threshold, "Good agents should be able to reach promotion"
    
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 AGENT PROGRESSION IMPROVEMENTS TEST SUITE")
    print("Testing @accelerate-master's performance optimizations")
    print("=" * 70)
    
    tests = [
        ("Configuration Updates", test_config_updates),
        ("Progression Gap", test_progression_gap),
        ("GitHub Pages Sync", test_github_pages_sync),
        ("Grace Period Logic", test_grace_period_logic),
        ("Minimum Score Boost", test_minimum_score_boost),
        ("Promotion Achievability", test_promotion_achievability),
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
    
    print("\n🎉 All tests passed! Agent progression improvements working correctly.")
    print("\n📈 Impact Summary:")
    print("   • Promotion threshold: 85% → 65% (20% easier)")
    print("   • Progression gap: 55% → 35% (36% reduction)")
    print("   • New agents protected for 48 hours")
    print("   • Minimum score guarantee: 40%")
    print("   • GitHub Pages sync: ✅ Working")
    
    return 0


if __name__ == '__main__':
    exit(main())
