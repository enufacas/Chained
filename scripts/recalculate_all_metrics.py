#!/usr/bin/env python3
"""
Recalculate All Agent Metrics - @investigate-champion

This script recalculates metrics for all agents using the fixed scoring logic.
It will update all historical data with correct PR attribution and merge counts.
"""

import json
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, 'tools')

# Import with exec to handle hyphenated module name
import importlib.util
spec = importlib.util.spec_from_file_location("agent_metrics_collector", "tools/agent-metrics-collector.py")
agent_metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_metrics_module)
MetricsCollector = agent_metrics_module.MetricsCollector

REGISTRY_FILE = Path('.github/agent-system/registry.json')
METRICS_DIR = Path('.github/agent-system/metrics')


def load_agents():
    """Load all agents from the registry"""
    if not REGISTRY_FILE.exists():
        print(f"❌ Registry file not found: {REGISTRY_FILE}")
        return []
    
    with open(REGISTRY_FILE, 'r') as f:
        registry = json.load(f)
    
    agents = registry.get('agents', [])
    print(f"📋 Found {len(agents)} agents in registry")
    return agents


def recalculate_metrics_for_agent(agent_id: str, agent_name: str):
    """Recalculate metrics for a single agent"""
    print(f"\n{'='*70}")
    print(f"Recalculating metrics for: {agent_name} ({agent_id})")
    print(f"{'='*70}")
    
    try:
        collector = MetricsCollector(repo='enufacas/Chained')
        metrics = collector.collect_metrics(agent_id, since_days=7)
        
        print(f"\n✅ Updated metrics for {agent_name}:")
        print(f"   Issues resolved: {metrics.activity.issues_resolved}")
        print(f"   PRs created: {metrics.activity.prs_created}")
        print(f"   PRs merged: {metrics.activity.prs_merged}")
        print(f"   Code quality: {metrics.scores.code_quality:.3f}")
        print(f"   PR success: {metrics.scores.pr_success:.3f}")
        print(f"   Overall score: {metrics.scores.overall:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recalculating metrics for {agent_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print(f"{'='*70}")
    print("Recalculate All Agent Metrics - @investigate-champion")
    print(f"{'='*70}")
    print("\nThis will recalculate metrics for all agents using the fixed scoring logic.")
    print("The fix addresses the PR merge detection bug that caused score convergence.\n")
    
    # Load agents
    agents = load_agents()
    if not agents:
        print("❌ No agents found to process")
        return 1
    
    # Recalculate for each agent
    success_count = 0
    failure_count = 0
    
    for agent in agents:
        agent_id = agent.get('id')
        agent_name = agent.get('specialization', agent_id)
        
        if recalculate_metrics_for_agent(agent_id, agent_name):
            success_count += 1
        else:
            failure_count += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"✅ Successfully recalculated: {success_count} agents")
    if failure_count > 0:
        print(f"❌ Failed: {failure_count} agents")
    print(f"\n📊 Total agents processed: {len(agents)}")
    
    # Verify improvements
    print(f"\n🔍 Verification:")
    print(f"   Check .github/agent-system/metrics/*/latest.json")
    print(f"   Verify that prs_created and prs_merged are now > 0 for agents with resolved issues")
    
    return 0 if failure_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
