#!/usr/bin/env python3
"""
Test PR Credit Fix

Verifies that agents get proper credit for PRs linked to their assigned issues.
"""

import sys
sys.path.insert(0, 'tools')

from registry_manager import RegistryManager


def test_agent_has_pr_credit():
    """Test that at least some agents have PR credit after the fix"""
    print("🧪 Testing PR Credit Fix...")
    print("=" * 70)
    
    registry = RegistryManager()
    agents = registry.list_agents(status='active')
    
    print(f"\n📊 Checking {len(agents)} active agents for PR credit...\n")
    
    agents_with_issues = 0
    agents_with_prs = 0
    agents_needing_fix = 0
    
    for agent in agents:
        issues_resolved = agent['metrics'].get('issues_resolved', 0)
        prs_merged = agent['metrics'].get('prs_merged', 0)
        
        if issues_resolved > 0:
            agents_with_issues += 1
            if prs_merged > 0:
                agents_with_prs += 1
                print(f"  ✅ {agent['name']}: {issues_resolved} issues, {prs_merged} PRs")
            else:
                agents_needing_fix += 1
                print(f"  ⚠️  {agent['name']}: {issues_resolved} issues, but 0 PRs (needs fix!)")
    
    print(f"\n📊 Summary:")
    print(f"  - Agents with resolved issues: {agents_with_issues}")
    print(f"  - Agents with PR credit: {agents_with_prs}")
    print(f"  - Agents needing fix: {agents_needing_fix}")
    
    if agents_needing_fix > 0:
        print(f"\n⚠️  {agents_needing_fix} agents have resolved issues but no PR credit!")
        print(f"   This indicates the PR attribution is still broken.")
        return False
    
    if agents_with_prs > 0:
        print(f"\n✅ Fix appears to be working - {agents_with_prs} agents have PR credit!")
        return True
    
    if agents_with_issues == 0:
        print(f"\n⚠️  No agents have resolved issues yet, cannot verify fix")
        print(f"   Need to wait for metrics collection to run")
        return None  # Inconclusive
    
    return False


def test_registry_structure():
    """Test that registry has expected structure"""
    print("\n🧪 Testing Registry Structure...")
    print("=" * 70)
    
    try:
        registry = RegistryManager()
        agents = registry.list_agents()
        
        print(f"  ✅ Registry loaded: {len(agents)} agents")
        
        # Check first agent has expected fields
        if agents:
            agent = agents[0]
            required_fields = ['id', 'name', 'specialization', 'status', 'metrics']
            missing = [f for f in required_fields if f not in agent]
            
            if missing:
                print(f"  ❌ Missing fields: {missing}")
                return False
            
            metrics_fields = ['issues_resolved', 'prs_merged', 'overall_score']
            metrics = agent.get('metrics', {})
            missing_metrics = [f for f in metrics_fields if f not in metrics]
            
            if missing_metrics:
                print(f"  ⚠️  Missing metrics: {missing_metrics}")
            else:
                print(f"  ✅ All required metrics fields present")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading registry: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 PR CREDIT FIX TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Registry Structure", test_registry_structure),
        ("Agent PR Credit", test_agent_has_pr_credit),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for name, result in results.items():
        if result is True:
            print(f"  ✅ {name}: PASSED")
        elif result is False:
            print(f"  ❌ {name}: FAILED")
        elif result is None:
            print(f"  ⚠️  {name}: INCONCLUSIVE")
    
    failed = sum(1 for r in results.values() if r is False)
    if failed > 0:
        print(f"\n❌ {failed} test(s) failed")
        return 1
    
    print(f"\n✅ All tests passed or inconclusive")
    return 0


if __name__ == '__main__':
    exit(main())
