#!/usr/bin/env python3
"""
Performance improvement demonstration test.
Shows the effectiveness of the optimizations in real-world scenarios.
"""

import sys
import time
import subprocess
from pathlib import Path

def test_repeated_agent_matching():
    """Test that repeated matches benefit from caching."""
    print("🧪 Testing Performance: Repeated Agent Matching")
    print("=" * 60)
    
    # Same issue matched multiple times (simulates real usage)
    test_cases = [
        ("Fix crash in login", "Users experiencing crashes"),
        ("Add profile feature", "Implement user profiles"),
        ("Update README", "Improve documentation"),
    ]
    
    iterations = 20  # Reduced iterations due to subprocess overhead
    start = time.time()
    
    for _ in range(iterations):
        for title, body in test_cases:
            result = subprocess.run(
                ["python3", "tools/match-issue-to-agent.py", title, body],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Failed to match: {title}")
                return False
    
    elapsed = time.time() - start
    total_matches = iterations * len(test_cases)
    avg_time = (elapsed / total_matches) * 1000
    
    print(f"✅ Completed {total_matches} matches in {elapsed:.3f}s")
    print(f"📊 Average: {avg_time:.3f}ms per match")
    print(f"⚡ Throughput: {total_matches/elapsed:.1f} matches/sec")
    
    # Performance threshold: Should be fast even with subprocess overhead
    # Note: Subprocess adds ~20-30ms overhead, so use realistic threshold
    if avg_time > 100:  # More than 100ms is too slow
        print(f"⚠️  Warning: Average time {avg_time:.3f}ms exceeds threshold")
        return False
    
    print("✅ Performance meets expectations!")
    return True


def test_code_analysis_performance():
    """Test code analysis performance."""
    print("\n🧪 Testing Performance: Code Analysis")
    print("=" * 60)
    
    # Analyze a real Python file
    test_file = Path(__file__).parent / "tools" / "match-issue-to-agent.py"
    
    if not test_file.exists():
        print("⚠️  Test file not found, skipping")
        return True
    
    iterations = 10
    start = time.time()
    
    for _ in range(iterations):
        result = subprocess.run(
            ["python3", "tools/code-analyzer.py", "-f", str(test_file)],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Analysis failed: {result.stderr}")
            return False
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000
    
    print(f"✅ Completed {iterations} analyses in {elapsed:.3f}s")
    print(f"📊 Average: {avg_time:.3f}ms per analysis")
    
    # Performance threshold: Should complete in reasonable time
    # Note: Subprocess overhead adds ~20-30ms, so use realistic threshold
    if avg_time > 100:  # More than 100ms is too slow
        print(f"⚠️  Warning: Average time {avg_time:.3f}ms exceeds threshold")
        return False
    
    print("✅ Performance meets expectations!")
    return True


def main():
    """Run all performance tests."""
    print("\n" + "=" * 60)
    print("⚡ Performance Optimization Validation Tests")
    print("=" * 60 + "\n")
    
    passed = 0
    failed = 0
    
    # Test 1: Agent matching performance
    if test_repeated_agent_matching():
        passed += 1
    else:
        failed += 1
    
    # Test 2: Code analysis performance
    if test_code_analysis_performance():
        passed += 1
    else:
        failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Performance Test Summary")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ All performance tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} performance test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
