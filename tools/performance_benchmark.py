#!/usr/bin/env python3
"""
Performance benchmark for Chained tools.
Measures execution time and memory usage of optimized components.
"""

import sys
import time
import json
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))


def benchmark_agent_matching():
    """Benchmark the agent matching system."""
    # Import here to ensure we're using the optimized version
    import importlib.util
    spec = importlib.util.spec_from_file_location("match_issue_to_agent", 
                                                   Path(__file__).parent / "match-issue-to-agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    match_issue_to_agent = module.match_issue_to_agent
    
    test_cases = [
        ("Fix crash in login module", "Users experiencing crashes when logging in"),
        ("Add user profile feature", "Implement user profile pages with avatars"),
        ("Update README", "The installation guide needs improvement"),
        ("Improve test coverage", "Add unit tests for auth module"),
        ("Slow page load", "The dashboard takes 5 seconds to load"),
        ("Security vulnerability", "Found XSS vulnerability in comments"),
        ("Refactor handlers", "Extract common logic into shared utilities"),
        ("Add Stripe integration", "Integrate Stripe for payments"),
        ("Optimize database queries", "Dashboard queries are slow"),
        ("Clean up code", "Improve code readability and style"),
    ]
    
    print("🚀 Benchmarking Agent Matching System")
    print("=" * 60)
    
    # Warmup run to populate caches
    for title, body in test_cases[:2]:
        match_issue_to_agent(title, body)
    
    # Timed runs
    iterations = 100
    start_time = time.time()
    
    for _ in range(iterations):
        for title, body in test_cases:
            match_issue_to_agent(title, body)
    
    end_time = time.time()
    elapsed = end_time - start_time
    avg_time = (elapsed / iterations / len(test_cases)) * 1000  # Convert to ms
    
    print(f"✅ Completed {iterations * len(test_cases)} matches in {elapsed:.3f}s")
    print(f"📊 Average time per match: {avg_time:.3f}ms")
    print(f"⚡ Throughput: {(iterations * len(test_cases)) / elapsed:.1f} matches/second")
    print()
    
    return {
        'total_time': elapsed,
        'avg_time_ms': avg_time,
        'throughput': (iterations * len(test_cases)) / elapsed
    }


def benchmark_code_analyzer():
    """Benchmark the code analyzer."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("code_analyzer", 
                                                   Path(__file__).parent / "code-analyzer.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    CodeAnalyzer = module.CodeAnalyzer
    
    print("🚀 Benchmarking Code Analyzer")
    print("=" * 60)
    
    # Use a real Python file for testing
    test_file = Path(__file__).parent / "match-issue-to-agent.py"
    
    if not test_file.exists():
        print("⚠️  Test file not found, skipping benchmark")
        return None
    
    analyzer = CodeAnalyzer()
    
    # Warmup run
    analyzer.analyze_python_file(str(test_file))
    
    # Timed runs
    iterations = 50
    start_time = time.time()
    
    for _ in range(iterations):
        analyzer.analyze_python_file(str(test_file))
    
    end_time = time.time()
    elapsed = end_time - start_time
    avg_time = (elapsed / iterations) * 1000  # Convert to ms
    
    print(f"✅ Completed {iterations} analyses in {elapsed:.3f}s")
    print(f"📊 Average time per analysis: {avg_time:.3f}ms")
    print(f"⚡ Throughput: {iterations / elapsed:.1f} analyses/second")
    print()
    
    return {
        'total_time': elapsed,
        'avg_time_ms': avg_time,
        'throughput': iterations / elapsed
    }


def benchmark_text_normalization():
    """Benchmark text normalization and sanitization."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("match_issue_to_agent", 
                                                   Path(__file__).parent / "match-issue-to-agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    normalize_text = module.normalize_text
    sanitize_input = module.sanitize_input
    
    print("🚀 Benchmarking Text Normalization")
    print("=" * 60)
    
    test_texts = [
        "Fix crash in login module",
        "Add user profile feature with avatars and settings",
        "Update README documentation and add more examples",
        "Improve test coverage for authentication module",
        "Slow page load performance issues need optimization",
        "Security vulnerability in user input validation",
        "Refactor event handlers to use common utilities",
        "Add Stripe payment integration for subscriptions",
        "Optimize database queries for better performance",
        "Clean up code style and improve readability",
    ]
    
    # Warmup
    for text in test_texts[:2]:
        normalize_text(text)
        sanitize_input(text)
    
    # Timed runs
    iterations = 1000
    start_time = time.time()
    
    for _ in range(iterations):
        for text in test_texts:
            normalize_text(text)
    
    end_time = time.time()
    elapsed = end_time - start_time
    avg_time = (elapsed / iterations / len(test_texts)) * 1_000_000  # Convert to µs
    
    print(f"✅ Completed {iterations * len(test_texts)} normalizations in {elapsed:.3f}s")
    print(f"📊 Average time per normalization: {avg_time:.2f}µs")
    print(f"⚡ Throughput: {(iterations * len(test_texts)) / elapsed:.1f} ops/second")
    print()
    
    return {
        'total_time': elapsed,
        'avg_time_us': avg_time,
        'throughput': (iterations * len(test_texts)) / elapsed
    }


def main():
    """Run all benchmarks."""
    print("=" * 60)
    print("⚡ Chained Performance Benchmarks")
    print("=" * 60)
    print()
    
    results = {}
    
    try:
        results['agent_matching'] = benchmark_agent_matching()
    except Exception as e:
        print(f"❌ Agent matching benchmark failed: {e}")
        results['agent_matching'] = None
    
    try:
        results['code_analyzer'] = benchmark_code_analyzer()
    except Exception as e:
        print(f"❌ Code analyzer benchmark failed: {e}")
        results['code_analyzer'] = None
    
    try:
        results['text_normalization'] = benchmark_text_normalization()
    except Exception as e:
        print(f"❌ Text normalization benchmark failed: {e}")
        results['text_normalization'] = None
    
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    for component, data in results.items():
        if data:
            print(f"\n{component.replace('_', ' ').title()}:")
            if 'avg_time_ms' in data:
                print(f"  Average time: {data['avg_time_ms']:.3f}ms")
            elif 'avg_time_us' in data:
                print(f"  Average time: {data['avg_time_us']:.2f}µs")
            print(f"  Throughput: {data['throughput']:.1f} ops/sec")
    
    print()
    print("✅ Benchmark completed!")
    print()
    
    # Save results to JSON
    output_file = Path(__file__).parent / "analysis" / "performance_benchmark.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }, f, indent=2)
    
    print(f"📝 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
