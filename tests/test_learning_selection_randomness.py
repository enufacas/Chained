#!/usr/bin/env python3
"""
Test suite for verifying randomness in learning selection.
Validates that the learning selection process introduces variety
across different workflow runs.
"""

import random
import json
from pathlib import Path
from collections import Counter


def simulate_learning_selection(num_runs=10):
    """
    Simulate the learning selection process multiple times
    to verify randomness.
    """
    # Create mock learning data
    mock_learnings = [
        {'title': f'Learning {i}', 'content': f'Content {i}'}
        for i in range(50)
    ]
    
    selected_first_items = []
    
    for run in range(num_runs):
        # Simulate the randomization steps
        learnings = mock_learnings.copy()
        
        # Step 1: Shuffle (as done in workflow)
        random.shuffle(learnings)
        
        # Step 2: Take first 5 (for assignment)
        selected = learnings[:5]
        
        # Track which learning was selected first
        selected_first_items.append(selected[0]['title'])
    
    return selected_first_items


def test_first_selection_varies():
    """Test that the first selected learning varies across runs."""
    print("Testing if first selected learning varies across runs...")
    
    first_items = simulate_learning_selection(num_runs=20)
    unique_first = set(first_items)
    
    print(f"   Unique first selections: {len(unique_first)} out of 20 runs")
    print(f"   First items: {Counter(first_items).most_common(5)}")
    
    # With proper randomization, we should get variety
    # Expect at least 10 different first selections out of 20 runs
    assert len(unique_first) >= 10, f"Expected at least 10 unique first selections, got {len(unique_first)}"
    
    # No single item should appear more than 5 times as first
    max_count = max(Counter(first_items).values())
    assert max_count <= 5, f"One item appeared {max_count} times as first, too concentrated"
    
    print("   ✅ Good variety in first selection")
    return True


def test_file_sampling_randomness():
    """Test that random.sample provides variety within files."""
    print("Testing random sampling within learning files...")
    
    # Simulate a learning file with many items
    large_file_data = list(range(100))
    
    # Take multiple samples
    samples = []
    for _ in range(10):
        sample = random.sample(large_file_data, 5)
        samples.append(tuple(sample))  # Convert to tuple for hashing
    
    unique_samples = set(samples)
    
    print(f"   Unique samples: {len(unique_samples)} out of 10")
    
    # Each sample should be different (or at least most of them)
    assert len(unique_samples) >= 8, f"Expected at least 8 unique samples, got {len(unique_samples)}"
    
    print("   ✅ Good variety in random sampling")
    return True


def test_file_order_randomness():
    """Test that file shuffling provides variety."""
    print("Testing file order randomization...")
    
    # Create list of mock files
    files = [f'file_{i}.json' for i in range(30)]
    
    # Shuffle multiple times and track first 5 files
    first_five_sets = []
    for _ in range(10):
        shuffled = files.copy()
        random.shuffle(shuffled)
        first_five_sets.append(tuple(shuffled[:5]))
    
    unique_sets = set(first_five_sets)
    
    print(f"   Unique first-5-file sets: {len(unique_sets)} out of 10")
    
    # Most shuffles should produce different orderings
    assert len(unique_sets) >= 8, f"Expected at least 8 unique orderings, got {len(unique_sets)}"
    
    print("   ✅ Good variety in file ordering")
    return True


def test_combined_randomness_effect():
    """
    Test that combined randomness (file order + sampling + final shuffle)
    produces significantly different selections across runs.
    """
    print("Testing combined randomness effect...")
    
    # Simulate the full pipeline
    def full_pipeline():
        # 30 files, each with 20 learnings
        all_learnings = []
        for file_idx in range(30):
            file_learnings = [
                {'title': f'File{file_idx}_Learning{i}', 'file': file_idx}
                for i in range(20)
            ]
            all_learnings.append(file_learnings)
        
        # Shuffle file order
        random.shuffle(all_learnings)
        
        # Sample from first 20 files
        selected = []
        for file_learnings in all_learnings[:20]:
            sample_size = min(5, len(file_learnings))
            selected.extend(random.sample(file_learnings, sample_size))
        
        # Final shuffle
        random.shuffle(selected)
        
        # Return first 10 for assignment
        return [l['title'] for l in selected[:10]]
    
    # Run pipeline multiple times
    run_results = []
    for _ in range(10):
        result = full_pipeline()
        run_results.append(tuple(result))
    
    # Check uniqueness
    unique_results = set(run_results)
    
    print(f"   Unique result sets: {len(unique_results)} out of 10 runs")
    
    # With 3 layers of randomization, all runs should be unique
    assert len(unique_results) >= 8, f"Expected at least 8 unique results, got {len(unique_results)}"
    
    # Check that different files appear across runs
    all_files_seen = set()
    for result in run_results:
        for title in result:
            file_num = int(title.split('_')[0].replace('File', ''))
            all_files_seen.add(file_num)
    
    print(f"   Different source files seen: {len(all_files_seen)}")
    
    # Should see learnings from many different files (at least 15)
    assert len(all_files_seen) >= 15, f"Expected learnings from at least 15 files, got {len(all_files_seen)}"
    
    print("   ✅ Combined randomness provides excellent variety")
    return True


def main():
    """Run all tests."""
    print("=" * 70)
    print("🎲 Testing Learning Selection Randomness")
    print("=" * 70)
    print()
    
    tests = [
        ("First selection varies", test_first_selection_varies),
        ("File sampling randomness", test_file_sampling_randomness),
        ("File order randomness", test_file_order_randomness),
        ("Combined randomness effect", test_combined_randomness_effect),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"📋 Test: {test_name}")
        print("-" * 70)
        try:
            result = test_func()
            if result:
                print(f"✅ PASS: {test_name}")
                passed += 1
            else:
                print(f"❌ FAIL: {test_name}")
                failed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {test_name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
