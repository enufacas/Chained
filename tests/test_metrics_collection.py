#!/usr/bin/env python3
"""
Manual test of PR attribution fix

Tests the fixed metrics collector with a real agent that has resolved issues.
"""

import sys
import os
import importlib.util
from pathlib import Path

# Add tools to path
sys.path.insert(0, 'tools')

# Load registry manager
from registry_manager import RegistryManager

# Load metrics collector
spec = importlib.util.spec_from_file_location(
    "agent_metrics_collector",
    "tools/agent-metrics-collector.py"
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

MetricsCollector = metrics_module.MetricsCollector


def test_single_agent():
    """Test metrics collection for a single agent with resolved issues"""
    print("=" * 70)
    print("🧪 MANUAL TEST: PR Attribution Fix")
    print("=" * 70)
    
    # Get an agent with resolved issues
    registry = RegistryManager()
    agents = registry.list_agents(status='active')
    
    test_agent = None
    for agent in agents:
        if agent['metrics'].get('issues_resolved', 0) > 0:
            test_agent = agent
            break
    
    if not test_agent:
        print("⚠️  No agents with resolved issues found")
        print("   Cannot test PR attribution")
        return False
    
    print(f"\n📊 Testing agent: {test_agent['name']}")
    print(f"   ID: {test_agent['id']}")
    print(f"   Specialization: {test_agent['specialization']}")
    print(f"   Current stats:")
    print(f"     - Issues resolved: {test_agent['metrics'].get('issues_resolved', 0)}")
    print(f"     - PRs merged: {test_agent['metrics'].get('prs_merged', 0)}")
    
    print(f"\n🔄 Collecting fresh metrics from GitHub...")
    
    # Set GitHub token if available
    if 'GITHUB_TOKEN' not in os.environ and 'GH_TOKEN' not in os.environ:
        print("⚠️  Warning: No GitHub token found")
        print("   Set GITHUB_TOKEN or GH_TOKEN environment variable for API access")
        return False
    
    try:
        # Create collector and collect metrics
        collector = MetricsCollector()
        metrics = collector.collect_metrics(test_agent['id'], since_days=30)
        
        print(f"\n✅ Metrics collected successfully!")
        print(f"\n📊 Fresh metrics from GitHub:")
        print(f"   Activity:")
        print(f"     - Issues created: {metrics.activity.issues_created}")
        print(f"     - Issues resolved: {metrics.activity.issues_resolved}")
        print(f"     - PRs created: {metrics.activity.prs_created}")
        print(f"     - PRs merged: {metrics.activity.prs_merged}")
        print(f"     - Reviews given: {metrics.activity.reviews_given}")
        print(f"     - Comments made: {metrics.activity.comments_made}")
        
        print(f"\n   Scores:")
        print(f"     - Code quality: {metrics.scores.code_quality:.2%}")
        print(f"     - Issue resolution: {metrics.scores.issue_resolution:.2%}")
        print(f"     - PR success: {metrics.scores.pr_success:.2%}")
        print(f"     - Peer review: {metrics.scores.peer_review:.2%}")
        print(f"     - Creativity: {metrics.scores.creativity:.2%}")
        print(f"     - Overall: {metrics.scores.overall:.2%}")
        
        # Check if fix worked
        if metrics.activity.issues_resolved > 0 and metrics.activity.prs_merged > 0:
            print(f"\n✅ FIX VERIFIED!")
            print(f"   Agent has {metrics.activity.issues_resolved} resolved issues")
            print(f"   AND {metrics.activity.prs_merged} merged PRs")
            print(f"   PR attribution is now working correctly!")
            return True
        elif metrics.activity.issues_resolved > 0 and metrics.activity.prs_merged == 0:
            print(f"\n⚠️  FIX NOT WORKING")
            print(f"   Agent has {metrics.activity.issues_resolved} resolved issues")
            print(f"   BUT 0 merged PRs")
            print(f"   PR attribution still broken!")
            return False
        else:
            print(f"\n⚠️  Inconclusive")
            print(f"   Agent has no resolved issues")
            return None
            
    except Exception as e:
        print(f"\n❌ Error collecting metrics: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    result = test_single_agent()
    
    print("\n" + "=" * 70)
    if result is True:
        print("✅ TEST PASSED - PR attribution fix is working!")
        return 0
    elif result is False:
        print("❌ TEST FAILED - PR attribution still broken")
        return 1
    else:
        print("⚠️  TEST INCONCLUSIVE - Need agents with resolved issues")
        return 2


if __name__ == '__main__':
    exit(main())
