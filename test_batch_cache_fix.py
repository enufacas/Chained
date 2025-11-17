#!/usr/bin/env python3
"""
Test to verify the batch cache fix works correctly for empty cache case.
This simulates the exact scenario from the issue.
"""

import sys
import importlib.util
from pathlib import Path

# Import agent-metrics-collector.py properly
spec = importlib.util.spec_from_file_location(
    "agent_metrics_collector",
    Path(__file__).parent / "tools" / "agent-metrics-collector.py"
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)
MetricsCollector = metrics_module.MetricsCollector

def test_empty_batch_cache_fix():
    """
    Test the specific bug: when batch_cache is empty dict {}, 
    it should still use batch optimization (not fall back to individual searches)
    """
    print("=" * 70)
    print("Testing Empty Batch Cache Fix")
    print("=" * 70)
    
    collector = MetricsCollector()
    
    # Simulate empty batch cache (common case when no issues exist)
    empty_batch_cache = {}
    
    print("\n1. Testing with EMPTY batch cache (dict {})...")
    print(f"   batch_cache = {empty_batch_cache}")
    print(f"   batch_cache is not None = {empty_batch_cache is not None}")
    print(f"   bool(batch_cache) = {bool(empty_batch_cache)}")
    
    # This is what the workflow does
    use_batch_cache_old = True if empty_batch_cache else False
    use_batch_cache_new = (empty_batch_cache is not None)
    
    print(f"\n   OLD logic: use_batch_cache = True if batch_cache else False")
    print(f"            = {use_batch_cache_old}")
    print(f"   NEW logic: use_batch_cache = (batch_cache is not None)")
    print(f"            = {use_batch_cache_new}")
    
    if use_batch_cache_old:
        print("\n   ❌ OLD LOGIC BUG: Would use batch cache (expected)")
    else:
        print("\n   ⚠️  OLD LOGIC BUG: Would fall back to individual search (WRONG!)")
    
    if use_batch_cache_new:
        print("   ✅ NEW LOGIC: Will use batch cache (correct!)")
    else:
        print("   ❌ NEW LOGIC: Would fall back (unexpected)")
    
    # Now test with the actual method
    print("\n2. Testing _find_issues_assigned_to_agent with empty batch cache...")
    
    try:
        from tools.registry_manager import RegistryManager
        registry = RegistryManager()
        active_agents = registry.list_agents(status='active')
        
        if len(active_agents) > 0:
            agent_id = active_agents[0]['id']
            print(f"   Testing with agent: {agent_id}")
            
            # Test NEW logic
            issues = collector._find_issues_assigned_to_agent(
                agent_id,
                since_days=7,
                use_batch_cache=True,  # NEW: Always True when batch_cache is not None
                batch_cache=empty_batch_cache
            )
            
            print(f"   Result: {len(issues)} issues found")
            print(f"   API calls made: {collector._api_call_count}")
            
            if collector._api_call_count == 0:
                print("\n   ✅ SUCCESS: No API calls made (used batch cache)")
            else:
                print(f"\n   ❌ FAILURE: {collector._api_call_count} API calls made (did not use batch cache)")
        else:
            print("   No agents to test")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 70)

def test_non_empty_batch_cache():
    """Test that non-empty batch cache also works"""
    print("\nTesting Non-Empty Batch Cache")
    print("=" * 70)
    
    collector = MetricsCollector()
    
    # Simulate non-empty batch cache
    mock_issue = {
        'number': 123,
        'title': 'Test issue',
        'state': 'open'
    }
    non_empty_cache = {
        'agent-123': [mock_issue]
    }
    
    print(f"\n1. batch_cache = {list(non_empty_cache.keys())}")
    print(f"   bool(batch_cache) = {bool(non_empty_cache)}")
    print(f"   batch_cache is not None = {non_empty_cache is not None}")
    
    # Test logic
    use_batch_cache_old = True if non_empty_cache else False
    use_batch_cache_new = (non_empty_cache is not None)
    
    print(f"\n   OLD logic result: {use_batch_cache_old}")
    print(f"   NEW logic result: {use_batch_cache_new}")
    
    if use_batch_cache_old and use_batch_cache_new:
        print("\n   ✅ BOTH work correctly for non-empty cache")
    
    print("=" * 70)

if __name__ == '__main__':
    test_empty_batch_cache_fix()
    test_non_empty_batch_cache()
    
    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("=" * 70)
    print("The bug was: 'True if batch_cache else False'")
    print("  - Evaluates to False when batch_cache is empty dict {}")
    print("  - Causes fallback to individual searches")
    print("  - Results in repeated API calls")
    print()
    print("The fix is: '(batch_cache is not None)'")
    print("  - Evaluates to True when batch_cache is empty dict {}")
    print("  - Uses batch optimization even with 0 issues")
    print("  - Avoids redundant API calls")
    print("=" * 70)
