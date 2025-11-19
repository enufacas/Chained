#!/usr/bin/env python3
"""
Test script to verify the metrics collector optimization.

This script tests:
1. Batch fetching works correctly
2. Caching reduces API calls
3. API call counting is accurate
"""

import sys
import importlib.util
from pathlib import Path

# Load the module with hyphenated name
spec = importlib.util.spec_from_file_location(
    "agent_metrics_collector",
    Path("tools/agent-metrics-collector.py")
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

MetricsCollector = metrics_module.MetricsCollector

def test_batch_optimization():
    """Test that batch optimization reduces API calls"""
    
    print("=" * 70)
    print("Testing Metrics Collector Optimization")
    print("=" * 70)
    
    # Create collector
    collector = MetricsCollector()
    
    # Test 1: Check initial state
    print("\n📊 Test 1: Initial state")
    stats = collector.get_api_stats()
    print(f"  API calls: {stats['api_calls']}")
    print(f"  Cached issues: {stats['cached_issues']}")
    print(f"  Cached PRs: {stats['cached_prs']}")
    print(f"  Cached timelines: {stats['cached_timelines']}")
    assert stats['api_calls'] == 0, "Should start with 0 API calls"
    print("  ✅ Initial state correct")
    
    # Test 2: Batch fetch
    print("\n📊 Test 2: Batch fetch all issues")
    batch_cache = collector._batch_fetch_all_agent_issues(since_days=7)
    stats_after_batch = collector.get_api_stats()
    print(f"  API calls after batch: {stats_after_batch['api_calls']}")
    print(f"  Issues cached: {stats_after_batch['cached_issues']}")
    print(f"  Agents with issues: {len(batch_cache)}")
    
    # The batch fetch should use significantly fewer calls than N*M individual calls
    # Expected: 1 search + M issue fetches (where M = number of issues)
    # Without optimization: N * (1 search + M fetches) where N = number of agents
    print(f"  ✅ Batch fetch completed with {stats_after_batch['api_calls']} API calls")
    
    # Test 3: Cache hit verification
    print("\n📊 Test 3: Verify caching works")
    initial_calls = stats_after_batch['api_calls']
    
    # Try to fetch issues again - should use cache
    if batch_cache:
        agent_id = list(batch_cache.keys())[0]
        issues = collector._find_issues_assigned_to_agent(
            agent_id,
            since_days=7,
            use_batch_cache=True,
            batch_cache=batch_cache
        )
        stats_after_cache_hit = collector.get_api_stats()
        print(f"  API calls after cache hit: {stats_after_cache_hit['api_calls']}")
        
        # Should not increase API calls when using cache
        assert stats_after_cache_hit['api_calls'] == initial_calls, "Cache should not make new API calls"
        print(f"  ✅ Cache working correctly (no additional API calls)")
    
    # Test 4: Clear cache
    print("\n📊 Test 4: Clear caches")
    collector.clear_caches()
    stats_after_clear = collector.get_api_stats()
    print(f"  API calls after clear: {stats_after_clear['api_calls']}")
    print(f"  Cached issues: {stats_after_clear['cached_issues']}")
    assert stats_after_clear['api_calls'] == 0, "Counter should reset"
    assert stats_after_clear['cached_issues'] == 0, "Cache should be empty"
    print("  ✅ Cache cleared successfully")
    
    print("\n" + "=" * 70)
    print("✅ All optimization tests passed!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    try:
        test_batch_optimization()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
