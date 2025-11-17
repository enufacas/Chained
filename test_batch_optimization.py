#!/usr/bin/env python3
"""
Test script to verify batch optimization in agent-metrics-collector.py
This script simulates the workflow's usage pattern and tracks API calls.
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

def test_batch_optimization():
    """Test that batch optimization actually works"""
    print("=" * 70)
    print("Testing Batch Optimization")
    print("=" * 70)
    
    # Create collector
    collector = MetricsCollector()
    
    # Simulate workflow behavior
    print("\n1. Testing batch fetch...")
    batch_cache = collector._batch_fetch_all_agent_issues(since_days=7)
    print(f"   Batch cache contains {len(batch_cache)} agent entries")
    print(f"   API calls after batch: {collector._api_call_count}")
    
    initial_api_calls = collector._api_call_count
    
    # Now simulate evaluating multiple agents with batch cache
    print("\n2. Testing individual agent evaluation WITH batch cache...")
    
    # Get a sample agent ID if available
    try:
        from registry_manager import RegistryManager
        registry = RegistryManager()
        active_agents = registry.list_agents(status='active')
        
        if len(active_agents) >= 2:
            # Test with 2 agents
            for idx, agent in enumerate(active_agents[:2], 1):
                agent_id = agent['id']
                print(f"\n   Agent {idx}: {agent_id}")
                
                # This should use the batch cache
                assigned_issues = collector._find_issues_assigned_to_agent(
                    agent_id,
                    since_days=7,
                    use_batch_cache=True,
                    batch_cache=batch_cache
                )
                
                print(f"   Found {len(assigned_issues)} assigned issues")
                print(f"   API calls so far: {collector._api_call_count}")
        else:
            print("   Not enough agents to test (need at least 2)")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    api_calls_with_cache = collector._api_call_count - initial_api_calls
    
    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Initial API calls (batch fetch): {initial_api_calls}")
    print(f"  API calls for agent evaluation: {api_calls_with_cache}")
    print(f"  Total API calls: {collector._api_call_count}")
    
    if api_calls_with_cache == 0:
        print("\n✅ OPTIMIZATION WORKING: No additional API calls for agent evaluation!")
    else:
        print(f"\n⚠️  POTENTIAL ISSUE: {api_calls_with_cache} additional API calls made")
    
    print("=" * 70)

def test_without_batch_cache():
    """Test the old behavior without batch optimization"""
    print("\n" + "=" * 70)
    print("Testing WITHOUT Batch Optimization (old behavior)")
    print("=" * 70)
    
    collector = MetricsCollector()
    
    try:
        from registry_manager import RegistryManager
        registry = RegistryManager()
        active_agents = registry.list_agents(status='active')
        
        if len(active_agents) >= 2:
            for idx, agent in enumerate(active_agents[:2], 1):
                agent_id = agent['id']
                print(f"\n   Agent {idx}: {agent_id}")
                
                # This should NOT use batch cache - old behavior
                assigned_issues = collector._find_issues_assigned_to_agent(
                    agent_id,
                    since_days=7,
                    use_batch_cache=False,
                    batch_cache=None
                )
                
                print(f"   Found {len(assigned_issues)} assigned issues")
                print(f"   API calls so far: {collector._api_call_count}")
        else:
            print("   Not enough agents to test (need at least 2)")
    
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 70)
    print(f"Total API calls WITHOUT batch optimization: {collector._api_call_count}")
    print("=" * 70)

if __name__ == '__main__':
    # Test with batch optimization
    test_batch_optimization()
    
    # Test without batch optimization to compare
    test_without_batch_cache()
