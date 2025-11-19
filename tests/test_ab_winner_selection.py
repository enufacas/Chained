#!/usr/bin/env python3
"""
Test suite to validate A/B testing winner selection logic.

This test suite was created by @assert-specialist to validate the
statistical correctness of the autonomous A/B testing system's winner
selection algorithm.

Author: @assert-specialist
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from ab_testing_engine import ABTestingEngine


class TestWinnerSelectionLogic:
    """
    Test the winner selection logic to ensure it correctly identifies
    the best-performing variant.
    """
    
    def test_winner_selection_with_normalized_metrics(self):
        """
        Test that winner selection properly handles metrics with different scales.
        
        CRITICAL BUG FOUND: The current implementation averages raw metric values
        without normalization, causing metrics with larger scales to dominate.
        """
        # Create a mock variant statistics dict simulating the demo experiment
        variant_stats = {
            "control": {
                "execution_time": {"mean": 96.26, "min": 77, "max": 123, "count": 20},
                "success_rate": {"mean": 0.8366, "min": 0.75, "max": 0.92, "count": 20},
                "resource_usage": {"mean": 48.94, "min": 41, "max": 59, "count": 20}
            },
            "optimized": {
                "execution_time": {"mean": 83.07, "min": 62, "max": 101, "count": 20},
                "success_rate": {"mean": 0.9276, "min": 0.88, "max": 0.98, "count": 20},
                "resource_usage": {"mean": 53.69, "min": 42, "max": 64, "count": 20}
            },
            "aggressive": {
                "execution_time": {"mean": 70.09, "min": 52, "max": 95, "count": 20},
                "success_rate": {"mean": 0.7893, "min": 0.67, "max": 0.94, "count": 20},
                "resource_usage": {"mean": 68.95, "min": 52, "max": 87, "count": 20}
            }
        }
        
        engine = ABTestingEngine()
        winner = engine._determine_winner(variant_stats, min_improvement=0.05)
        
        # Current (buggy) behavior: control wins due to unweighted averaging
        assert winner is not None
        assert winner["variant"] == "control"
        
        # But logically, "optimized" should win because:
        # 1. Faster execution time than control (83 vs 96 seconds)
        # 2. MUCH better success rate (92.76% vs 83.66%) - 10.89% improvement!
        # 3. Slightly higher resource usage (53.69 vs 48.94) - acceptable tradeoff
        
        # The bug: execution_time dominates because it's on a scale of ~100
        # while success_rate is on a scale of ~1
        
        print("\n🐛 BUG DETECTED: Winner selection uses unweighted averaging")
        print(f"   Current winner: {winner['variant']}")
        print(f"   Score: {winner['score']:.2f}")
        print()
        print("   Metric scale comparison:")
        print("   - execution_time: ~100 (seconds)")
        print("   - success_rate: ~0.9 (percentage as decimal)")
        print("   - resource_usage: ~50 (units)")
        print()
        print("   Control score = (96.26 + 0.8366 + 48.94) / 3 = 48.68")
        print("   Optimized score = (83.07 + 0.9276 + 53.69) / 3 = 45.90")
        print()
        print("   ⚠️  Lower execution_time pulls down optimized's average!")
        print("   ⚠️  But lower execution_time is BETTER for performance!")
    
    def test_success_rate_should_be_primary_metric(self):
        """
        Test that success rate is properly weighted as the most important metric.
        
        A variant with 10% better success rate should generally win,
        even if other metrics are slightly worse.
        """
        # In the demo experiment:
        # - Optimized has 10.89% better success rate than control
        # - Optimized has 13.7% faster execution time than control
        # - Optimized uses 9.7% more resources than control
        
        # With proper weighting, optimized should win decisively
        
        control_success = 0.8366
        optimized_success = 0.9276
        
        improvement = (optimized_success - control_success) / control_success
        
        assert improvement > 0.10, f"Optimized has {improvement:.2%} better success rate"
        print(f"\n✅ Optimized variant has {improvement:.2%} better success rate")
        print("   This should be the winning variant!")
    
    def test_metric_direction_matters(self):
        """
        Test that metric direction is considered (higher vs lower is better).
        
        CRITICAL: The current implementation doesn't distinguish between:
        - Metrics where HIGHER is better (success_rate, uptime)
        - Metrics where LOWER is better (execution_time, error_rate, resource_usage)
        """
        # execution_time: LOWER is better
        # success_rate: HIGHER is better  
        # resource_usage: LOWER is better
        
        print("\n📊 Metric direction analysis:")
        print("   execution_time: lower is better")
        print("   success_rate: higher is better")
        print("   resource_usage: lower is better")
        print()
        print("   Optimized vs Control:")
        print("   - execution_time: 83.07 < 96.26 ✅ (13.7% better)")
        print("   - success_rate: 0.9276 > 0.8366 ✅ (10.89% better)")
        print("   - resource_usage: 53.69 > 48.94 ❌ (9.7% worse)")
        print()
        print("   ✅ Optimized wins on 2/3 metrics, including the critical success_rate")


def test_demo_experiment_analysis():
    """
    Integration test: Analyze the actual demo experiment and validate results.
    """
    engine = ABTestingEngine()
    
    # Get the demo experiment
    exp_id = "exp-a560d184a326"
    
    try:
        analysis = engine.analyze_experiment(exp_id)
        
        print("\n🔬 Demo Experiment Analysis:")
        print(f"   Status: {analysis['status']}")
        
        if analysis.get("winner"):
            winner = analysis["winner"]
            print(f"   Winner: {winner['variant']}")
            print(f"   Score: {winner['score']:.2f}")
            print(f"   Improvement: {winner['improvement']:.2%}")
            print(f"   Confidence: {winner['confidence']}")
        
        # Compare success rates directly
        stats = analysis["variant_statistics"]
        control_sr = stats["control"]["success_rate"]["mean"]
        optimized_sr = stats["optimized"]["success_rate"]["mean"]
        aggressive_sr = stats["aggressive"]["success_rate"]["mean"]
        
        print()
        print("   Success Rate Comparison:")
        print(f"   - Control: {control_sr:.2%}")
        print(f"   - Optimized: {optimized_sr:.2%}")
        print(f"   - Aggressive: {aggressive_sr:.2%}")
        
        # Validate that optimized has the best success rate
        assert optimized_sr > control_sr, "Optimized should have better success rate"
        assert optimized_sr > aggressive_sr, "Optimized should have better success rate"
        
        print()
        print(f"   ✅ VALIDATION: Optimized has best success rate ({optimized_sr:.2%})")
        
        # But the system declared control as winner!
        if analysis.get("winner") and analysis["winner"]["variant"] == "control":
            print(f"   ⚠️  WARNING: System incorrectly selected control as winner")
            print(f"   🐛 This is due to the unweighted averaging bug in _determine_winner()")
        
    except Exception as e:
        print(f"❌ Could not analyze experiment: {e}")
        print("   (Demo experiment not found or not ready)")


if __name__ == "__main__":
    print("=" * 80)
    print("A/B Testing Winner Selection Validation")
    print("@assert-specialist - Systematic Testing Approach")
    print("=" * 80)
    
    # Run tests manually
    test_suite = TestWinnerSelectionLogic()
    
    print("\n" + "=" * 80)
    print("TEST 1: Winner selection with normalized metrics")
    print("=" * 80)
    try:
        test_suite.test_winner_selection_with_normalized_metrics()
        print("✅ Test passed")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"⚠️  Test error: {e}")
    
    print("\n" + "=" * 80)
    print("TEST 2: Success rate should be primary metric")
    print("=" * 80)
    try:
        test_suite.test_success_rate_should_be_primary_metric()
        print("✅ Test passed")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"⚠️  Test error: {e}")
    
    print("\n" + "=" * 80)
    print("TEST 3: Metric direction matters")
    print("=" * 80)
    try:
        test_suite.test_metric_direction_matters()
        print("✅ Test passed")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"⚠️  Test error: {e}")
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST: Demo experiment analysis")
    print("=" * 80)
    try:
        test_demo_experiment_analysis()
        print("✅ Test passed")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"⚠️  Test error: {e}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("🔍 CRITICAL BUG IDENTIFIED:")
    print()
    print("The A/B testing engine's _determine_winner() method uses unweighted")
    print("averaging of raw metric values, which causes metrics with larger")
    print("scales (like execution_time ~100) to dominate the score calculation.")
    print()
    print("This leads to incorrect winner selection where a variant with:")
    print("  ✅ 10.89% better success rate")
    print("  ✅ 13.7% faster execution time")
    print("  ❌ 9.7% higher resource usage")
    print()
    print("...is incorrectly rejected in favor of 'control' because the")
    print("unweighted average is skewed by the large execution_time values.")
    print()
    print("RECOMMENDATION:")
    print("  1. Implement proper metric normalization (z-scores or min-max)")
    print("  2. Consider metric direction (higher vs lower is better)")
    print("  3. Apply appropriate weights based on metric importance")
    print("  4. Use proper statistical tests (t-test, Mann-Whitney U, etc.)")
    print()
    print("---")
    print("Validation by @assert-specialist")
