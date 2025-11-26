#!/usr/bin/env python3
"""
Test suite runner for A2A integration testing.
Phase 2B: Testing & Integration

Runs all A2A tests in sequence and provides summary report.
"""

import subprocess
import sys
from pathlib import Path


def run_test_file(test_file: Path) -> tuple[bool, str]:
    """Run a test file and return success status and output."""
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 60 seconds"
    except Exception as e:
        return False, f"Test failed to run: {e}"


def main():
    """Run all A2A tests."""
    print("=" * 70)
    print("A2A Integration Test Suite - Phase 2B")
    print("=" * 70)
    
    tests_dir = Path(__file__).parent
    
    # Define test order
    test_files = [
        "test_a2a_agent_cards.py",
        "test_a2a_discovery.py",
        "test_a2a_tier1.py",
    ]
    
    results = {}
    
    for test_file_name in test_files:
        test_file = tests_dir / test_file_name
        
        if not test_file.exists():
            print(f"\n⚠️  Skipping {test_file_name} (not found)")
            continue
        
        print(f"\n{'=' * 70}")
        print(f"Running: {test_file_name}")
        print(f"{'=' * 70}\n")
        
        success, output = run_test_file(test_file)
        results[test_file_name] = success
        
        # Print output
        print(output)
        
        if not success:
            print(f"\n❌ {test_file_name} FAILED")
        else:
            print(f"\n✅ {test_file_name} PASSED")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUITE SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_file, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {test_file}")
    
    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{total} test files passed")
    print(f"{'=' * 70}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
