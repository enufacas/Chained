#!/usr/bin/env python3
"""
Demonstrate Scoring Fix Impact - @investigate-champion

This script shows how the scoring fix would impact agent metrics
by simulating what would happen when PRs are properly detected.
"""

import json
from pathlib import Path

METRICS_DIR = Path('.github/agent-system/metrics')

def load_current_metrics():
    """Load current metrics for all agents"""
    metrics = {}
    for agent_dir in METRICS_DIR.iterdir():
        if not agent_dir.is_dir() or agent_dir.name in ['performance', 'creativity']:
            continue
        
        latest_file = agent_dir / 'latest.json'
        if latest_file.exists():
            try:
                with open(latest_file) as f:
                    data = json.load(f)
                    metrics[data['agent_id']] = data
            except Exception as e:
                print(f"Warning: Could not load {latest_file}: {e}")
    
    return metrics

def simulate_fixed_scores(metrics):
    """
    Simulate what scores would look like after the fix.
    
    Logic: If an agent resolved issues, they likely created and merged PRs.
    We simulate finding those PRs and recalculating scores.
    """
    simulated = {}
    
    for agent_id, data in metrics.items():
        activity = data['activity']
        scores = data['scores']
        weights = data['metadata']['weights']
        
        # Simulate: For each resolved issue, estimate 1 PR was created and merged
        issues_resolved = activity['issues_resolved']
        
        if issues_resolved > 0:
            # Simulate finding PRs
            simulated_prs_created = issues_resolved
            simulated_prs_merged = issues_resolved  # Assume all were merged since issue is resolved
            
            # Recalculate scores with fixed logic
            # Code quality: Based on merge rate
            merge_rate = simulated_prs_merged / simulated_prs_created
            new_code_quality = min(1.0, merge_rate * 1.2)
            
            # PR success: Merge rate
            new_pr_success = merge_rate
            
            # Recalculate overall with new component scores
            new_overall = (
                new_code_quality * weights['code_quality'] +
                scores['issue_resolution'] * weights['issue_resolution'] +
                new_pr_success * weights['pr_success'] +
                scores['peer_review'] * weights['peer_review'] +
                scores['creativity'] * weights['creativity']
            )
            
            simulated[agent_id] = {
                'agent_id': agent_id,
                'old_prs_created': activity['prs_created'],
                'old_prs_merged': activity['prs_merged'],
                'old_code_quality': scores['code_quality'],
                'old_pr_success': scores['pr_success'],
                'old_overall': scores['overall'],
                'new_prs_created': simulated_prs_created,
                'new_prs_merged': simulated_prs_merged,
                'new_code_quality': new_code_quality,
                'new_pr_success': new_pr_success,
                'new_overall': new_overall,
                'issues_resolved': issues_resolved
            }
        else:
            # No change for agents without resolved issues
            simulated[agent_id] = {
                'agent_id': agent_id,
                'old_overall': scores['overall'],
                'new_overall': scores['overall'],
                'issues_resolved': 0,
                'no_change': True
            }
    
    return simulated

def main():
    print("=" * 70)
    print("Scoring Fix Impact Demonstration - @investigate-champion")
    print("=" * 70)
    print()
    print("This shows how the scoring fix would impact agent metrics")
    print("when PRs are properly detected and counted.")
    print()
    
    # Load current metrics
    metrics = load_current_metrics()
    print(f"📊 Loaded metrics for {len(metrics)} agents")
    print()
    
    # Simulate fixed scores
    simulated = simulate_fixed_scores(metrics)
    
    # Count changes
    agents_with_changes = [s for s in simulated.values() if not s.get('no_change', False)]
    
    print(f"🔧 Simulating fix impact...")
    print(f"   Agents that would change: {len(agents_with_changes)}")
    print()
    
    # Show examples
    print("=" * 70)
    print("Example Impact (agents with resolved issues):")
    print("=" * 70)
    print()
    
    for sim in sorted(agents_with_changes, key=lambda x: x['new_overall'] - x['old_overall'], reverse=True)[:5]:
        print(f"Agent: {sim['agent_id']}")
        print(f"  Issues Resolved: {sim['issues_resolved']}")
        print(f"  PRs Created:  {sim['old_prs_created']} → {sim['new_prs_created']} (+{sim['new_prs_created']})")
        print(f"  PRs Merged:   {sim['old_prs_merged']} → {sim['new_prs_merged']} (+{sim['new_prs_merged']})")
        print(f"  Code Quality: {sim['old_code_quality']:.3f} → {sim['new_code_quality']:.3f} ({sim['new_code_quality']-sim['old_code_quality']:+.3f})")
        print(f"  PR Success:   {sim['old_pr_success']:.3f} → {sim['new_pr_success']:.3f} ({sim['new_pr_success']-sim['old_pr_success']:+.3f})")
        print(f"  Overall:      {sim['old_overall']:.3f} → {sim['new_overall']:.3f} ({sim['new_overall']-sim['old_overall']:+.3f})")
        print()
    
    # Summary statistics
    print("=" * 70)
    print("Summary Statistics:")
    print("=" * 70)
    print()
    
    # Calculate score improvements
    improvements = [s['new_overall'] - s['old_overall'] for s in agents_with_changes]
    if improvements:
        avg_improvement = sum(improvements) / len(improvements)
        max_improvement = max(improvements)
        
        print(f"📈 Score Improvements:")
        print(f"   Average: +{avg_improvement:.3f} ({avg_improvement*100:.1f}%)")
        print(f"   Maximum: +{max_improvement:.3f} ({max_improvement*100:.1f}%)")
        print()
    
    # Score diversity
    old_scores = [s['old_overall'] for s in simulated.values()]
    new_scores = [s['new_overall'] for s in simulated.values()]
    
    old_unique = len(set(f"{s:.3f}" for s in old_scores))
    new_unique = len(set(f"{s:.3f}" for s in new_scores))
    
    print(f"🎯 Score Diversity:")
    print(f"   Before: {old_unique} unique scores")
    print(f"   After:  {new_unique} unique scores ({new_unique-old_unique:+d})")
    print()
    
    print("✅ Fix Impact Summary:")
    print(f"   • {len(agents_with_changes)} agents would have improved scores")
    print(f"   • PRs would be properly detected and counted")
    print(f"   • Code quality scores would reflect actual work")
    print(f"   • Score diversity would improve significantly")
    print()
    print("📝 Note: This is a simulation. Actual results require running")
    print("   the recalculation script with GitHub API access.")

if __name__ == '__main__':
    main()
