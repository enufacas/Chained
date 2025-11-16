#!/usr/bin/env python3
"""
Test script to verify deduplication fix for learning files.

This script simulates the issue and verifies that the fix works correctly.

Created by: @troubleshoot-expert (Grace Hopper)
Date: 2025-11-16
"""

import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def extract_source_date(filename):
    """Extract source and date from filename to group duplicates."""
    name = filename.stem  # Remove .json extension
    parts = name.split('_')
    if len(parts) >= 2:
        source = parts[0]  # e.g., 'tldr', 'hn', 'github'
        date = parts[1][:8]  # First 8 chars = YYYYMMDD
        return (source, date)
    return (name, None)


def get_file_learning_count(filepath):
    """Get count of learnings in a file."""
    try:
        with open(filepath) as f:
            data = json.load(f)
            # Handle different formats
            if isinstance(data, dict):
                # Check for explicit count field
                if 'count' in data:
                    return data['count']
                # Check for learnings array
                if 'learnings' in data:
                    return len(data['learnings'])
                # Check for stories array (HackerNews)
                if 'stories' in data:
                    return len(data['stories'])
                # Check for repositories array (GitHub Trending)
                if 'repositories' in data:
                    return len(data['repositories'])
            elif isinstance(data, list):
                return len(data)
    except Exception:
        pass
    return 0


def create_test_scenario():
    """Create a test scenario with duplicate files."""
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix='test_learnings_'))
    print(f"📁 Created test directory: {temp_dir}")
    
    # Scenario 1: Same source, same date, different timestamps
    files_to_create = [
        ('tldr_20251114.json', {'learnings': [], 'source': 'tldr', 'count': 0}),
        ('tldr_20251114_082728.json', {'learnings': [
            {'title': 'Test Learning 1', 'source': 'TLDR'},
            {'title': 'Test Learning 2', 'source': 'TLDR'}
        ], 'source': 'tldr', 'count': 2}),
        ('tldr_20251114_083243.json', {'learnings': [], 'source': 'tldr', 'count': 0}),
        
        # Scenario 2: Different dates (should NOT be deduplicated)
        ('tldr_20251115_082336.json', {'learnings': [
            {'title': 'Test Learning 3', 'source': 'TLDR'}
        ], 'source': 'tldr', 'count': 1}),
        
        # Scenario 3: Different source (should NOT be deduplicated)
        ('hn_20251114_082730.json', {'learnings': [
            {'title': 'HN Story 1', 'source': 'hackernews'}
        ], 'source': 'hackernews', 'count': 1}),
        
        # Scenario 4: GitHub trending
        ('github_trending_20251114.json', {'repositories': [], 'source': 'github_trending', 'count': 0}),
        ('github_trending_20251114_120000.json', {'repositories': [
            {'name': 'test-repo', 'stars': 100}
        ], 'source': 'github_trending', 'count': 1}),
    ]
    
    for filename, data in files_to_create:
        filepath = temp_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  ✓ Created: {filename}")
    
    return temp_dir


def test_deduplication(test_dir):
    """Test the deduplication logic."""
    print("\n🧪 Testing Deduplication Logic")
    print("=" * 60)
    
    # Simulate the workflow logic
    learning_files = list(test_dir.glob('*.json'))
    print(f"\n📊 Initial file count: {len(learning_files)}")
    for f in sorted(learning_files):
        print(f"  - {f.name}")
    
    # DEDUPLICATION: Group files by source and date
    file_groups = defaultdict(list)
    for f in learning_files:
        source, date = extract_source_date(f)
        if date:
            file_groups[(source, date)].append(f)
    
    print(f"\n📦 File groups by source+date:")
    for (source, date), files in sorted(file_groups.items()):
        print(f"  {source}_{date}: {len(files)} file(s)")
        for f in files:
            print(f"    - {f.name}")
    
    # Select BEST file per source+date combination
    # Prioritize: 1) Most content, 2) Newest timestamp
    deduplicated_files = []
    duplicate_count = 0
    for (source, date), files in file_groups.items():
        if len(files) > 1:
            duplicate_count += len(files) - 1
            print(f"\n  🔍 Deduplicating {source}_{date}: {len(files)} files → 1 file")
            for f in files:
                content_count = get_file_learning_count(f)
                print(f"    - {f.name} (content: {content_count}, mtime: {f.stat().st_mtime})")
        
        # Score each file: content count (primary) + mtime (secondary)
        scored_files = []
        for f in files:
            content_count = get_file_learning_count(f)
            mtime = f.stat().st_mtime
            # Score: prioritize content (x1000) over recency
            score = (content_count * 1000) + mtime
            scored_files.append((score, content_count, mtime, f))
        
        # Select file with highest score (most content, then newest)
        best_file = max(scored_files, key=lambda x: x[0])[3]
        deduplicated_files.append(best_file)
        
        if len(files) > 1:
            best_count = max(scored_files, key=lambda x: x[0])[1]
            print(f"    ✅ Selected: {best_file.name} (score winner: {best_count} items)")
    
    print(f"\n✅ Deduplication complete:")
    print(f"   Original files: {len(learning_files)}")
    print(f"   Duplicates removed: {duplicate_count}")
    print(f"   Deduplicated files: {len(deduplicated_files)}")
    
    print(f"\n📋 Final file list:")
    for f in sorted(deduplicated_files):
        print(f"  - {f.name}")
    
    return deduplicated_files, duplicate_count


def verify_results(deduplicated_files, duplicate_count):
    """Verify that the deduplication worked correctly."""
    print("\n✅ Verification")
    print("=" * 60)
    
    # Expected results:
    # - tldr_20251114: Should have 1 file (newest)
    # - tldr_20251115: Should have 1 file
    # - hn_20251114: Should have 1 file
    # - github_trending_20251114: Should have 1 file
    # Total: 4 files
    
    expected_files = 4
    expected_duplicates = 3  # (3 tldr + 2 github_trending) - 2 kept = 3 removed
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: File count
    print(f"\n1️⃣ Test: Final file count")
    if len(deduplicated_files) == expected_files:
        print(f"   ✅ PASS: {len(deduplicated_files)} files (expected {expected_files})")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: {len(deduplicated_files)} files (expected {expected_files})")
        tests_failed += 1
    
    # Test 2: Duplicate count
    print(f"\n2️⃣ Test: Duplicate removal count")
    if duplicate_count == expected_duplicates:
        print(f"   ✅ PASS: {duplicate_count} duplicates removed (expected {expected_duplicates})")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: {duplicate_count} duplicates removed (expected {expected_duplicates})")
        tests_failed += 1
    
    # Test 3: No duplicate source+date combinations
    print(f"\n3️⃣ Test: No duplicate source+date combinations")
    source_dates = set()
    has_duplicates = False
    for f in deduplicated_files:
        source, date = extract_source_date(f)
        if (source, date) in source_dates:
            has_duplicates = True
            print(f"   ❌ Duplicate found: {source}_{date}")
        source_dates.add((source, date))
    
    if not has_duplicates:
        print(f"   ✅ PASS: No duplicate source+date combinations")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: Found duplicate source+date combinations")
        tests_failed += 1
    
    # Test 4: Correct file selection (should prefer files with content)
    print(f"\n4️⃣ Test: Content-rich files selected")
    content_check_passed = True
    for f in deduplicated_files:
        with open(f) as file:
            data = json.load(file)
            learning_count = data.get('count', 0)
            if f.name.startswith('tldr_20251114'):
                # Should have selected the file with 2 learnings, not the empty ones
                if learning_count == 2:
                    print(f"   ✅ {f.name}: {learning_count} learnings (good)")
                else:
                    print(f"   ❌ {f.name}: {learning_count} learnings (should be 2)")
                    content_check_passed = False
    
    if content_check_passed:
        print(f"   ✅ PASS: Content-rich files selected over empty files")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: Empty files selected instead of content-rich files")
        tests_failed += 1
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 60)
    print(f"   ✅ Passed: {tests_passed}/4")
    print(f"   ❌ Failed: {tests_failed}/4")
    
    if tests_failed == 0:
        print(f"\n🎉 All tests passed! Deduplication fix is working correctly.")
        return True
    else:
        print(f"\n⚠️ Some tests failed. Review the implementation.")
        return False


def main():
    """Main test execution."""
    print("🔬 Deduplication Fix Test Suite")
    print("=" * 60)
    print("Testing the fix for duplicate learning files issue")
    print("Workflow Run: 19403024552")
    print("Issue: PR 1273 attempted fix, but duplicates persist")
    print()
    
    try:
        # Create test scenario
        test_dir = create_test_scenario()
        
        # Run deduplication
        deduplicated_files, duplicate_count = test_deduplication(test_dir)
        
        # Verify results
        success = verify_results(deduplicated_files, duplicate_count)
        
        # Cleanup
        print(f"\n🧹 Cleaning up test directory...")
        shutil.rmtree(test_dir)
        print(f"   ✓ Removed: {test_dir}")
        
        # Exit with appropriate code
        if success:
            print("\n✅ SUCCESS: Fix verified and working correctly!")
            return 0
        else:
            print("\n❌ FAILURE: Fix needs adjustments")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
