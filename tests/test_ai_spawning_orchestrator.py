#!/usr/bin/env python3
"""
Test AI Spawning Orchestrator - Verify functionality

Simple test to ensure the orchestrator works correctly.
Created by @create-botter
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

def test_orchestrator_import():
    """Test that orchestrator can be imported"""
    try:
        from ai_spawning_orchestrator import AISpawningOrchestrator
        print("✅ Orchestrator import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_orchestrator_initialization():
    """Test that orchestrator can be initialized"""
    try:
        from ai_spawning_orchestrator import AISpawningOrchestrator
        
        orchestrator = AISpawningOrchestrator(
            enable_learning=False,  # Disable for faster test
            enable_predictions=False
        )
        
        print("✅ Orchestrator initialization successful")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_dry_run():
    """Test dry-run mode"""
    try:
        from ai_spawning_orchestrator import AISpawningOrchestrator
        
        orchestrator = AISpawningOrchestrator(
            enable_learning=False,
            enable_predictions=False
        )
        
        results = orchestrator.orchestrate(
            max_spawns=1,
            dry_run=True
        )
        
        # Check results structure
        assert 'timestamp' in results
        assert 'dry_run' in results
        assert results['dry_run'] is True
        assert 'decisions' in results
        assert 'spawned_agents' in results
        assert 'summary' in results
        
        print("✅ Dry-run test successful")
        print(f"   Status: {results['summary'].get('status')}")
        print(f"   Decisions: {len(results['decisions'])}")
        print(f"   Spawned: {results['total_spawned']}")
        
        return True
    except Exception as e:
        print(f"❌ Dry-run test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test configuration loading"""
    try:
        from ai_spawning_orchestrator import AISpawningOrchestrator
        
        orchestrator = AISpawningOrchestrator()
        
        # Check config exists
        assert orchestrator.config is not None
        assert 'max_spawns_per_run' in orchestrator.config
        assert 'workload_threshold' in orchestrator.config
        
        print("✅ Configuration loading successful")
        print(f"   Max spawns: {orchestrator.config['max_spawns_per_run']}")
        print(f"   Workload threshold: {orchestrator.config['workload_threshold']}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AI Spawning Orchestrator - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Import", test_orchestrator_import),
        ("Initialization", test_orchestrator_initialization),
        ("Configuration", test_config_loading),
        ("Dry Run", test_dry_run),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 Testing: {name}")
        print("-" * 60)
        success = test_func()
        results.append((name, success))
        print()
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
