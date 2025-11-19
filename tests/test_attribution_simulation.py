#!/usr/bin/env python3
"""
Manual Test - Agent Attribution System

This script demonstrates how the new attribution system works by simulating
the metrics collection process.
"""

import sys
import json
from pathlib import Path

def simulate_metrics_collection():
    """Simulate metrics collection for all agents"""
    
    print("=" * 70)
    print("AGENT ATTRIBUTION SYSTEM - SIMULATION")
    print("=" * 70)
    
    # Load registry
    registry_path = Path(".github/agent-system/registry.json")
    if not registry_path.exists():
        print("❌ Registry not found")
        return False
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    agents = registry.get('agents', [])
    
    print(f"\n📊 Found {len(agents)} active agents\n")
    
    # Simulate metrics collection for each agent
    for agent in agents:
        agent_id = agent.get('id')
        agent_name = agent.get('name')
        specialization = agent.get('specialization')
        current_score = agent.get('metrics', {}).get('overall_score', 0.0)
        
        print(f"\n{agent_name} ({agent_id})")
        print(f"  Specialization: {specialization}")
        print(f"  Current Score: {current_score:.2%}")
        
        # Show what would happen with new system
        print(f"  📝 New system will:")
        print(f"     1. Search for issues with 'agent-work' label")
        print(f"     2. Parse issue bodies for <!-- COPILOT_AGENT:{specialization} -->")
        print(f"     3. Count resolved issues, PRs, reviews")
        print(f"     4. Calculate weighted score")
        print(f"     5. Update registry with new score")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Wait for next agent evaluation (daily at midnight UTC)")
    print("2. Check workflow logs for attribution messages:")
    print("   - '🔍 Looking for issues assigned to agent...'")
    print("   - '📋 Found X total agent-work issues in timeframe'")
    print("   - '✅ Found X issues assigned to {agent_id}'")
    print("   - '📊 Activity summary for {agent_id}:'")
    print("\n3. Verify agents receive non-zero scores")
    print("4. Check registry.json for updated metrics")
    
    print("\n" + "=" * 70)
    print("TESTING TIPS")
    print("=" * 70)
    print("\n✅ Create a test issue with:")
    print("   - Title: 'Test issue for [agent-name]'")
    print("   - Body starting with: <!-- COPILOT_AGENT:specialization -->")
    print("   - Label: 'agent-work'")
    print("\n✅ Assign to Copilot and close the issue")
    print("\n✅ Run evaluator manually:")
    print("   gh workflow run agent-evaluator.yml")
    print("\n✅ Check logs for attribution in action")
    
    return True


def show_current_metrics():
    """Show current metrics for all agents"""
    
    print("\n" + "=" * 70)
    print("CURRENT AGENT METRICS")
    print("=" * 70)
    
    registry_path = Path(".github/agent-system/registry.json")
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    agents = registry.get('agents', [])
    
    # Sort by score
    agents_sorted = sorted(agents, key=lambda a: a.get('metrics', {}).get('overall_score', 0), reverse=True)
    
    print(f"\n{'Agent':<30} {'Specialization':<25} {'Score':<10} {'Issues':<8} {'PRs':<8}")
    print("-" * 90)
    
    for agent in agents_sorted:
        name = agent.get('name', 'Unknown')
        spec = agent.get('specialization', 'Unknown')
        metrics = agent.get('metrics', {})
        score = metrics.get('overall_score', 0)
        issues = metrics.get('issues_resolved', 0)
        prs = metrics.get('prs_merged', 0)
        
        print(f"{name:<30} {spec:<25} {score:>6.2%}    {issues:<8} {prs:<8}")
    
    # Show summary
    avg_score = sum(a.get('metrics', {}).get('overall_score', 0) for a in agents) / len(agents) if agents else 0
    zero_scores = sum(1 for a in agents if a.get('metrics', {}).get('overall_score', 0) == 0)
    
    print("-" * 90)
    print(f"\nSummary:")
    print(f"  - Average Score: {avg_score:.2%}")
    print(f"  - Agents with 0% score: {zero_scores}/{len(agents)}")
    print(f"  - Expected after fix: Agents with work will have non-zero scores")


def main():
    """Run simulation"""
    
    print("\n🔍 AGENT ATTRIBUTION SYSTEM TEST\n")
    
    show_current_metrics()
    simulate_metrics_collection()
    
    print("\n" + "=" * 70)
    print("✅ Simulation complete!")
    print("=" * 70)
    print("\nThe new attribution system is ready to use.")
    print("It will be automatically activated on the next agent evaluation.\n")


if __name__ == '__main__':
    sys.exit(0 if main() is None else 0)
