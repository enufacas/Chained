#!/usr/bin/env python3
"""
Agent Scoring Accuracy Test

Tests the agent scoring system against historical data to verify:
1. Scores are accurately calculated from activity
2. PR attribution is working correctly
3. Scores differentiate agents appropriately
4. No unintended "capping" or convergence

This test is created by @assert-specialist to verify scoring accuracy.
"""

import json
import sys
from pathlib import Path
from collections import Counter

# Paths
METRICS_DIR = Path(".github/agent-system/metrics")
REGISTRY_FILE = Path(".github/agent-system/registry.json")


def load_all_agent_metrics():
    """Load metrics for all agents from historical data"""
    metrics_by_agent = {}
    
    if not METRICS_DIR.exists():
        print(f"❌ Metrics directory not found: {METRICS_DIR}")
        return metrics_by_agent
    
    for agent_dir in METRICS_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        
        agent_id = agent_dir.name
        latest_file = agent_dir / "latest.json"
        
        if latest_file.exists():
            try:
                with open(latest_file, 'r') as f:
                    metrics = json.load(f)
                    metrics_by_agent[agent_id] = metrics
            except Exception as e:
                print(f"⚠️  Warning: Could not load metrics for {agent_id}: {e}")
    
    return metrics_by_agent


def test_score_calculation_accuracy():
    """Test that overall scores are correctly calculated from component scores"""
    print("\n🧪 Testing Score Calculation Accuracy...")
    
    metrics = load_all_agent_metrics()
    
    if not metrics:
        print("❌ No metrics data found")
        return False
    
    errors = []
    
    for agent_id, data in metrics.items():
        scores = data.get('scores', {})
        metadata = data.get('metadata', {})
        weights = metadata.get('weights', {})
        
        # Manually calculate expected overall score
        expected = (
            scores.get('code_quality', 0) * weights.get('code_quality', 0.3) +
            scores.get('issue_resolution', 0) * weights.get('issue_resolution', 0.2) +
            scores.get('pr_success', 0) * weights.get('pr_success', 0.2) +
            scores.get('peer_review', 0) * weights.get('peer_review', 0.15) +
            scores.get('creativity', 0) * weights.get('creativity', 0.15)
        )
        
        actual = scores.get('overall', 0)
        
        # Allow small floating point differences
        if abs(expected - actual) > 0.0001:
            errors.append(f"{agent_id}: expected {expected:.4f}, got {actual:.4f}")
    
    if errors:
        print(f"   ❌ Found {len(errors)} calculation errors:")
        for error in errors[:5]:  # Show first 5
            print(f"      {error}")
        return False
    else:
        print(f"   ✅ All {len(metrics)} agents have correct overall scores")
        return True


def test_score_diversity():
    """Test that scores show appropriate diversity (not all agents have same score)"""
    print("\n🧪 Testing Score Diversity...")
    
    metrics = load_all_agent_metrics()
    
    if not metrics:
        print("❌ No metrics data found")
        return False
    
    # Collect all overall scores
    overall_scores = [m.get('scores', {}).get('overall', 0) for m in metrics.values()]
    
    # Round to 2 decimal places for grouping
    rounded_scores = [round(score, 2) for score in overall_scores]
    
    # Count occurrences
    score_counter = Counter(rounded_scores)
    
    # Find most common score
    most_common_score, count = score_counter.most_common(1)[0]
    
    total_agents = len(metrics)
    convergence_ratio = count / total_agents
    
    print(f"   📊 Total agents: {total_agents}")
    print(f"   📊 Unique scores: {len(score_counter)}")
    print(f"   📊 Most common score: {most_common_score:.2f} ({count} agents, {convergence_ratio:.1%})")
    
    # Warn if too many agents have the same score
    if convergence_ratio > 0.5:
        print(f"   ⚠️  WARNING: {convergence_ratio:.1%} of agents have the same score!")
        print(f"   This suggests limited score differentiation")
        
        # Show distribution of common scores
        print(f"\n   Score distribution:")
        for score, cnt in score_counter.most_common(5):
            print(f"      {score:.2f}: {cnt} agents ({cnt/total_agents:.1%})")
        
        return False
    else:
        print(f"   ✅ Good score diversity - agents are differentiated")
        return True


def test_code_quality_defaults():
    """Test that code_quality defaults are appropriate"""
    print("\n🧪 Testing Code Quality Score Defaults...")
    
    metrics = load_all_agent_metrics()
    
    if not metrics:
        print("❌ No metrics data found")
        return False
    
    # Count agents with default code_quality (0.5)
    default_count = 0
    has_prs_count = 0
    
    for agent_id, data in metrics.items():
        activity = data.get('activity', {})
        scores = data.get('scores', {})
        
        prs_created = activity.get('prs_created', 0)
        code_quality = scores.get('code_quality', 0)
        
        if prs_created == 0 and code_quality == 0.5:
            default_count += 1
        elif prs_created > 0:
            has_prs_count += 1
    
    total = len(metrics)
    default_ratio = default_count / total
    
    print(f"   📊 Agents with no PRs (code_quality=0.5): {default_count}/{total} ({default_ratio:.1%})")
    print(f"   📊 Agents with PRs: {has_prs_count}/{total} ({has_prs_count/total:.1%})")
    
    if default_ratio > 0.7:
        print(f"   ⚠️  WARNING: {default_ratio:.1%} of agents have default code_quality")
        print(f"   This suggests PR attribution may not be working correctly")
        return False
    else:
        print(f"   ✅ Reasonable distribution of code quality scores")
        return True


def test_creativity_diversity():
    """Test that creativity scores show diversity"""
    print("\n🧪 Testing Creativity Score Diversity...")
    
    metrics = load_all_agent_metrics()
    
    if not metrics:
        print("❌ No metrics data found")
        return False
    
    # Collect creativity scores
    creativity_scores = [m.get('scores', {}).get('creativity', 0) for m in metrics.values()]
    
    # Round to 2 decimal places
    rounded = [round(score, 2) for score in creativity_scores]
    
    # Count occurrences
    creativity_counter = Counter(rounded)
    
    total = len(metrics)
    unique_scores = len(creativity_counter)
    
    print(f"   📊 Total agents: {total}")
    print(f"   📊 Unique creativity scores: {unique_scores}")
    
    # Show most common scores
    print(f"\n   Most common creativity scores:")
    for score, count in creativity_counter.most_common(5):
        print(f"      {score:.2f}: {count} agents ({count/total:.1%})")
    
    most_common_score, count = creativity_counter.most_common(1)[0]
    convergence = count / total
    
    if convergence > 0.5:
        print(f"\n   ⚠️  WARNING: {convergence:.1%} of agents have creativity={most_common_score:.2f}")
        print(f"   This suggests creativity calculation may have issues")
        return False
    else:
        print(f"\n   ✅ Acceptable creativity score diversity")
        return True


def test_activity_to_score_correlation():
    """Test that higher activity leads to higher scores"""
    print("\n🧪 Testing Activity-to-Score Correlation...")
    
    metrics = load_all_agent_metrics()
    
    if not metrics:
        print("❌ No metrics data found")
        return False
    
    # Group agents by activity level
    low_activity = []  # No activity
    medium_activity = []  # Some activity (1-2 issues or PRs)
    high_activity = []  # High activity (3+ issues or PRs)
    
    for agent_id, data in metrics.items():
        activity = data.get('activity', {})
        scores = data.get('scores', {})
        
        total_activity = (
            activity.get('issues_resolved', 0) +
            activity.get('prs_merged', 0)
        )
        
        overall_score = scores.get('overall', 0)
        
        if total_activity == 0:
            low_activity.append(overall_score)
        elif total_activity <= 2:
            medium_activity.append(overall_score)
        else:
            high_activity.append(overall_score)
    
    # Calculate averages
    avg_low = sum(low_activity) / len(low_activity) if low_activity else 0
    avg_medium = sum(medium_activity) / len(medium_activity) if medium_activity else 0
    avg_high = sum(high_activity) / len(high_activity) if high_activity else 0
    
    print(f"   📊 Low activity agents (0): {len(low_activity)} agents, avg score: {avg_low:.2%}")
    print(f"   📊 Medium activity agents (1-2): {len(medium_activity)} agents, avg score: {avg_medium:.2%}")
    print(f"   📊 High activity agents (3+): {len(high_activity)} agents, avg score: {avg_high:.2%}")
    
    # Check if scores correlate with activity
    if low_activity and medium_activity and avg_medium <= avg_low:
        print(f"   ⚠️  WARNING: Medium activity agents don't score higher than low activity!")
        return False
    
    if medium_activity and high_activity and avg_high <= avg_medium:
        print(f"   ⚠️  WARNING: High activity agents don't score higher than medium activity!")
        return False
    
    print(f"   ✅ Activity correlates positively with scores")
    return True


def test_pr_attribution_logic():
    """Test that PR attribution is working by checking for agents with PRs"""
    print("\n🧪 Testing PR Attribution Logic...")
    
    metrics = load_all_agent_metrics()
    
    if not metrics:
        print("❌ No metrics data found")
        return False
    
    # Count agents with different PR statuses
    agents_with_prs_created = 0
    agents_with_prs_merged = 0
    agents_with_issues_but_no_prs = 0
    
    for agent_id, data in metrics.items():
        activity = data.get('activity', {})
        
        prs_created = activity.get('prs_created', 0)
        prs_merged = activity.get('prs_merged', 0)
        issues_resolved = activity.get('issues_resolved', 0)
        
        if prs_created > 0:
            agents_with_prs_created += 1
        
        if prs_merged > 0:
            agents_with_prs_merged += 1
        
        if issues_resolved > 0 and prs_created == 0:
            agents_with_issues_but_no_prs += 1
    
    total = len(metrics)
    
    print(f"   📊 Agents with PRs created: {agents_with_prs_created}/{total} ({agents_with_prs_created/total:.1%})")
    print(f"   📊 Agents with PRs merged: {agents_with_prs_merged}/{total} ({agents_with_prs_merged/total:.1%})")
    print(f"   📊 Agents with issues but no PRs: {agents_with_issues_but_no_prs}/{total} ({agents_with_issues_but_no_prs/total:.1%})")
    
    # If many agents have issues resolved but no PRs, attribution may be broken
    if agents_with_issues_but_no_prs > 5:
        print(f"\n   ⚠️  WARNING: {agents_with_issues_but_no_prs} agents resolved issues but have no PRs!")
        print(f"   This suggests PR attribution may not be working correctly")
        print(f"   Issues are typically resolved via PRs, so this is suspicious")
        
        # Show some examples
        print(f"\n   Example agents with issues but no PRs:")
        count = 0
        for agent_id, data in metrics.items():
            activity = data.get('activity', {})
            if activity.get('issues_resolved', 0) > 0 and activity.get('prs_created', 0) == 0:
                print(f"      {agent_id}: {activity.get('issues_resolved')} issues, 0 PRs")
                count += 1
                if count >= 3:
                    break
        
        return False
    else:
        print(f"   ✅ PR attribution appears to be working")
        return True


def main():
    """Run all scoring accuracy tests"""
    print("=" * 70)
    print("🧪 AGENT SCORING ACCURACY TEST SUITE - @assert-specialist")
    print("=" * 70)
    print("\nTesting agent scoring system against historical data...")
    
    tests = [
        ("Score Calculation Accuracy", test_score_calculation_accuracy),
        ("Score Diversity", test_score_diversity),
        ("Code Quality Defaults", test_code_quality_defaults),
        ("Creativity Diversity", test_creativity_diversity),
        ("Activity-to-Score Correlation", test_activity_to_score_correlation),
        ("PR Attribution Logic", test_pr_attribution_logic),
    ]
    
    passed = 0
    failed = 0
    warnings = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
                warnings.append(test_name)
        except Exception as e:
            failed += 1
            warnings.append(f"{test_name} (error: {e})")
            print(f"   ❌ {test_name} error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY - @assert-specialist")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if warnings:
        print(f"\n⚠️  ISSUES FOUND:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n@assert-specialist verifies: Agent scoring system is accurate")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("\n@assert-specialist found issues that need to be addressed:")
        print("- Score convergence/capping detected")
        print("- PR attribution may not be working correctly")
        print("- Limited score differentiation between agents")
        return 1


if __name__ == '__main__':
    sys.exit(main())
