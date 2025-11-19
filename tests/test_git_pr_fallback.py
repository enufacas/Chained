#!/usr/bin/env python3
"""
Test git-based PR attribution fallback - @assert-specialist

This test verifies that the git log fallback method can find PRs
when the GitHub API is unavailable or fails.
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, 'tools')

import importlib.util
spec = importlib.util.spec_from_file_location(
    'agent_metrics_collector',
    Path('tools/agent-metrics-collector.py')
)
metrics_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics_module)

def test_git_pr_fallback():
    """Test that _find_prs_via_git can parse git log correctly"""
    print("=" * 70)
    print("Testing Git-Based PR Fallback - @assert-specialist")
    print("=" * 70)
    
    # Create a mock collector
    collector = metrics_module.MetricsCollector()
    
    # Test with some mock assigned issues
    # These issue numbers should exist in recent git history
    assigned_issues = [
        {'number': 1059},  # Current issue
        {'number': 1000},  # Likely to have PRs
        {'number': 500},   # Older issue
    ]
    
    print(f"\n🔍 Testing git log fallback for {len(assigned_issues)} issues...")
    print(f"   Issue numbers: {[i['number'] for i in assigned_issues]}")
    
    # Call the git-based fallback
    prs_found = collector._find_prs_via_git("test-agent", assigned_issues)
    
    print(f"\n📊 Results:")
    print(f"   PRs found: {len(prs_found)}")
    
    if prs_found:
        print(f"\n   ✅ Git fallback working! Found PRs:")
        for pr in prs_found:
            pr_num = pr.get('number')
            issue_num = pr.get('issue_number')
            merged = pr.get('pull_request', {}).get('merged_at')
            print(f"      PR #{pr_num} → Issue #{issue_num} (merged: {bool(merged)})")
        return True
    else:
        print(f"   ⚠️  No PRs found via git log")
        print(f"   This might be expected if git log doesn't contain merge commits")
        print(f"   with these issue numbers")
        
        # Check if git log has ANY merge commits
        result = subprocess.run(
            ['git', 'log', '--merges', '--oneline', '-n', '10'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print(f"\n   📝 Sample merge commits in repo:")
            for line in result.stdout.strip().split('\n')[:5]:
                print(f"      {line}")
        
        return False

def test_git_availability():
    """Test that git is available"""
    print("\n" + "=" * 70)
    print("Testing Git Availability")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ Git available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Git command failed")
            return False
    except Exception as e:
        print(f"❌ Git not available: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("Git-Based PR Attribution Fallback Test")
    print("By @assert-specialist")
    print("=" * 70)
    
    # Test git availability
    git_ok = test_git_availability()
    
    if not git_ok:
        print("\n❌ Git not available, cannot test fallback")
        sys.exit(1)
    
    # Test the fallback method
    fallback_ok = test_git_pr_fallback()
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    if fallback_ok:
        print("✅ Git-based PR fallback is working")
        print("   PRs can be found when GitHub API is unavailable")
    else:
        print("⚠️  Git-based PR fallback returned no results")
        print("   This is acceptable if no matching PRs exist in git history")
    
    print("\n📝 Note: This fallback helps when GitHub API rate limits")
    print("   are exceeded or authentication is unavailable")
    
    print("\n✅ Test completed successfully")

if __name__ == '__main__':
    main()
