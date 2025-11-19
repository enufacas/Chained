#!/usr/bin/env python3
"""
PR Attribution Debug Script - @assert-specialist

Tests PR attribution for a specific agent to diagnose why PRs aren't being counted.
"""

import json
import os
import sys
from pathlib import Path

# Add tools to path
tools_dir = Path(__file__).parent / 'tools'
sys.path.insert(0, str(tools_dir))

# Load the agent-metrics-collector module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_metrics_collector",
    tools_dir / "agent-metrics-collector.py"
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

MetricsCollector = metrics_module.MetricsCollector

def main():
    """Debug PR attribution for a specific agent"""
    
    # Use agent-1762928620 (coach-master) who has 2 issues resolved but 0 PRs
    agent_id = "agent-1762928620"
    
    print(f"🔍 Debugging PR attribution for {agent_id}")
    print("=" * 70)
    
    # Initialize collector
    collector = MetricsCollector()
    
    # Get agent specialization
    specialization = collector._get_agent_specialization(agent_id)
    print(f"Agent specialization: {specialization}")
    
    # Find assigned issues
    print(f"\n📋 Finding assigned issues...")
    assigned_issues = collector._find_issues_assigned_to_agent(agent_id, 7)
    
    print(f"\n✅ Found {len(assigned_issues)} assigned issues:")
    for issue in assigned_issues:
        print(f"   - Issue #{issue['number']}: {issue['title']}")
        print(f"     State: {issue['state']}")
    
    # Now manually check for PRs that close these issues
    print(f"\n🔍 Checking for PRs that close these issues...")
    
    for issue in assigned_issues:
        issue_number = issue['number']
        print(f"\n   Issue #{issue_number}:")
        
        # Try timeline API
        try:
            timeline = collector.github.get(
                f'/repos/{collector.repo}/issues/{issue_number}/timeline',
                headers={'Accept': 'application/vnd.github.mockingbird-preview+json'}
            )
            
            if timeline:
                print(f"      Timeline events: {len(timeline)}")
                for event in timeline[:10]:  # Show first 10 events
                    event_type = event.get('event')
                    print(f"         - {event_type}")
                    
                    if event_type == 'cross-referenced':
                        source = event.get('source', {})
                        print(f"           Source type: {source.get('type')}")
                        if source.get('type') == 'issue':
                            issue_data = source.get('issue', {})
                            if issue_data.get('pull_request'):
                                print(f"           ✅ Found PR #{issue_data.get('number')}")
        except Exception as e:
            print(f"      ❌ Timeline API error: {e}")
        
        # Try search API
        try:
            search_results = collector._search_issues(
                agent_id,
                'is:pr',
                f'in:body #{issue_number}'
            )
            
            if search_results:
                print(f"      Search found {len(search_results)} PRs:")
                for pr in search_results:
                    print(f"         - PR #{pr['number']}: {pr['title']}")
                    print(f"           State: {pr['state']}")
                    if pr.get('pull_request'):
                        merged = pr['pull_request'].get('merged_at')
                        print(f"           Merged: {bool(merged)}")
        except Exception as e:
            print(f"      ❌ Search API error: {e}")
    
    print("\n" + "=" * 70)
    print("@assert-specialist debug complete")


if __name__ == '__main__':
    main()
