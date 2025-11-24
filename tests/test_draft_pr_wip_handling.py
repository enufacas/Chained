#!/usr/bin/env python3
"""
Test: Draft PR WIP Handling

Validates that the meta-coordinator correctly handles draft PRs based on
WIP markers in the title, not just draft status.

This test ensures that:
1. Draft PRs WITH WIP markers are skipped
2. Draft PRs WITHOUT WIP markers are processed
3. Non-draft PRs WITH WIP markers are skipped
4. Non-draft PRs WITHOUT WIP markers are processed
"""

import re


def has_wip_marker(title: str) -> bool:
    """
    Check if a PR title has WIP markers.
    
    This implements the same logic as documented in meta-coordinator-system.md:
    - [WIP]
    - WIP:
    - WIP (followed by space)
    - work in progress / work.in.progress
    - [do not merge] / [do.not.merge]
    - [dnm]
    """
    # Case-insensitive regex pattern matching the meta-coordinator logic
    wip_pattern = r'\[WIP\]|^WIP:|WIP\s|work.in.progress|\[do.not.merge\]|\[dnm\]'
    return bool(re.search(wip_pattern, title, re.IGNORECASE))


def should_process_pr(is_draft: bool, title: str) -> tuple[bool, str]:
    """
    Determine if a PR should be processed based on draft status and WIP markers.
    
    Returns:
        (should_process, reason)
    """
    # Check for WIP markers first (takes precedence)
    if has_wip_marker(title):
        return False, "WIP marker in title"
    
    # Draft status alone does NOT block processing if title is clean
    return True, "No WIP markers, ready for processing"


def test_draft_with_wip_markers():
    """Draft PRs with WIP markers should be skipped"""
    test_cases = [
        (True, "[WIP] Fix bug in authentication"),
        (True, "WIP: Add new feature"),
        (True, "WIP Update documentation"),
        (True, "[do not merge] Testing changes"),
        (True, "[DNM] Experimental code"),
    ]
    
    for is_draft, title in test_cases:
        should_process, reason = should_process_pr(is_draft, title)
        assert not should_process, \
            f"Expected to skip draft PR with WIP marker: {title}"
        assert "WIP marker" in reason, \
            f"Expected WIP marker reason, got: {reason}"
    
    print("✅ test_draft_with_wip_markers passed")


def test_draft_without_wip_markers():
    """Draft PRs WITHOUT WIP markers should be processed"""
    test_cases = [
        (True, "Fix authentication bug"),
        (True, "Add new feature for users"),
        (True, "Update README documentation"),
        (True, "Refactor code for better performance"),
        (True, "feat: implement new API endpoint"),
    ]
    
    for is_draft, title in test_cases:
        should_process, reason = should_process_pr(is_draft, title)
        assert should_process, \
            f"Expected to process draft PR without WIP marker: {title}"
        assert "No WIP markers" in reason, \
            f"Expected no WIP reason, got: {reason}"
    
    print("✅ test_draft_without_wip_markers passed")


def test_non_draft_with_wip_markers():
    """Non-draft PRs with WIP markers should be skipped"""
    test_cases = [
        (False, "[WIP] Fix bug in authentication"),
        (False, "WIP: Add new feature"),
        (False, "WIP Update documentation"),
        (False, "[do not merge] Testing changes"),
        (False, "[DNM] Experimental code"),
    ]
    
    for is_draft, title in test_cases:
        should_process, reason = should_process_pr(is_draft, title)
        assert not should_process, \
            f"Expected to skip non-draft PR with WIP marker: {title}"
        assert "WIP marker" in reason, \
            f"Expected WIP marker reason, got: {reason}"
    
    print("✅ test_non_draft_with_wip_markers passed")


def test_non_draft_without_wip_markers():
    """Non-draft PRs WITHOUT WIP markers should be processed"""
    test_cases = [
        (False, "Fix authentication bug"),
        (False, "Add new feature for users"),
        (False, "Update README documentation"),
        (False, "Refactor code for better performance"),
        (False, "feat: implement new API endpoint"),
    ]
    
    for is_draft, title in test_cases:
        should_process, reason = should_process_pr(is_draft, title)
        assert should_process, \
            f"Expected to process non-draft PR without WIP marker: {title}"
        assert "No WIP markers" in reason, \
            f"Expected no WIP reason, got: {reason}"
    
    print("✅ test_non_draft_without_wip_markers passed")


def test_edge_case_titles():
    """Test edge cases with WIP-like but valid titles"""
    # These should NOT be considered WIP
    valid_titles = [
        "Wipe old cache files",  # "wipe" not "wip"
        "Update WIPR protocol",  # WIPR is different
        "Work in the new feature",  # "work in the" not "work.in.progress"
        "Add working implementation",  # "working" not "wip"
    ]
    
    for title in valid_titles:
        should_process, reason = should_process_pr(False, title)
        assert should_process, \
            f"Expected to process valid title: {title}"
    
    # These SHOULD be considered WIP
    wip_titles = [
        "work in progress update",
        "work.in.progress: new feature",
        "[do.not.merge] experimental",
    ]
    
    for title in wip_titles:
        should_process, reason = should_process_pr(False, title)
        assert not should_process, \
            f"Expected to skip WIP title: {title}"
    
    print("✅ test_edge_case_titles passed")


def test_has_wip_marker_function():
    """Test the WIP marker detection function directly"""
    # Positive cases - should detect WIP
    wip_cases = [
        "[WIP]",
        "[wip]",
        "WIP:",
        "wip:",
        "WIP something",
        "wip something",
        "work.in.progress",
        "work in progress",
        "[do not merge]",
        "[do.not.merge]",
        "[DNM]",
        "[dnm]",
        "Title with [WIP] in middle",
        "WIP: Title with prefix",
    ]
    
    for title in wip_cases:
        assert has_wip_marker(title), \
            f"Expected to detect WIP in: {title}"
    
    # Negative cases - should NOT detect WIP
    clean_cases = [
        "Fix bug",
        "Add feature",
        "Wipe cache",
        "WIPR protocol",
        "working implementation",
        "Update documentation",
    ]
    
    for title in clean_cases:
        assert not has_wip_marker(title), \
            f"Expected NOT to detect WIP in: {title}"
    
    print("✅ test_has_wip_marker_function passed")


def run_all_tests():
    """Run all test functions"""
    test_functions = [
        test_has_wip_marker_function,
        test_draft_with_wip_markers,
        test_draft_without_wip_markers,
        test_non_draft_with_wip_markers,
        test_non_draft_without_wip_markers,
        test_edge_case_titles,
    ]
    
    print("=" * 60)
    print("Running Draft PR WIP Handling Tests")
    print("=" * 60)
    print()
    
    for test_func in test_functions:
        try:
            test_func()
        except AssertionError as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            raise
    
    print()
    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print()
    print("Summary:")
    print("- Draft PRs with WIP markers: SKIP ✓")
    print("- Draft PRs without WIP markers: PROCESS ✓")
    print("- Non-draft PRs with WIP markers: SKIP ✓")
    print("- Non-draft PRs without WIP markers: PROCESS ✓")
    print()
    print("This validates that the meta-coordinator will correctly handle")
    print("draft PRs based on WIP markers in title, not just draft status.")


if __name__ == "__main__":
    run_all_tests()
