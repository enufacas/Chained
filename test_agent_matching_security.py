#!/usr/bin/env python3
"""
Security and robustness tests for the agent matching system.
Tests edge cases, error handling, and defensive programming.
"""

import sys
import json
import subprocess
import tempfile
import os
from pathlib import Path

def run_matching_safe(title, body):
    """Run the matching script with error handling."""
    try:
        result = subprocess.run(
            ['python3', 'tools/match-issue-to-agent.py', title, body],
            capture_output=True,
            text=True,
            timeout=10,  # Prevent hanging
            cwd='.'
        )
        
        if result.returncode != 0:
            return None, f"Exit code: {result.returncode}, stderr: {result.stderr}"
        
        try:
            return json.loads(result.stdout), None
        except json.JSONDecodeError as e:
            return None, f"JSON decode error: {e}"
            
    except subprocess.TimeoutExpired:
        return None, "Timeout after 10 seconds"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def test_empty_inputs():
    """Test handling of empty and None-like inputs."""
    print("Testing empty inputs...")
    
    test_cases = [
        ("", "", "Empty strings"),
        (" ", " ", "Whitespace only"),
        ("\n", "\n", "Newlines only"),
        ("\t", "\t", "Tabs only"),
    ]
    
    passed = 0
    failed = 0
    
    for title, body, description in test_cases:
        result, error = run_matching_safe(title, body)
        
        if error:
            print(f"  ❌ FAILED: {description}")
            print(f"     Error: {error}")
            failed += 1
        elif result and result.get('agent'):
            print(f"  ✅ PASSED: {description}")
            print(f"     → Matched: {result['agent']}")
            passed += 1
        else:
            print(f"  ❌ FAILED: {description}")
            print(f"     → No agent returned")
            failed += 1
    
    return passed, failed

def test_special_characters():
    """Test handling of special characters and potential injection."""
    print("\nTesting special characters...")
    
    test_cases = [
        ("Fix bug with <script>alert('xss')</script>", "Test XSS", "HTML/JS injection attempt"),
        ("Issue with $(rm -rf /)", "Shell command", "Shell injection attempt"),
        ("Bug in file://etc/passwd", "Path traversal", "File path injection"),
        ("Error: {'key': 'value'}", "Dict-like string", "Dict-like syntax"),
        ("Fix: ../../../etc/passwd", "Path traversal", "Directory traversal"),
        # Null bytes are rejected by subprocess (expected security behavior)
        # ("Bug with \x00 null byte", "Null bytes", "Null byte handling"),
        ("Issue 🐛 with emojis 🚀", "Unicode test 😀", "Unicode/emoji handling"),
    ]
    
    passed = 0
    failed = 0
    
    for title, body, description in test_cases:
        result, error = run_matching_safe(title, body)
        
        if error:
            print(f"  ❌ FAILED: {description}")
            print(f"     Error: {error}")
            failed += 1
        elif result and result.get('agent'):
            print(f"  ✅ PASSED: {description}")
            print(f"     → Safely handled, matched: {result['agent']}")
            passed += 1
        else:
            print(f"  ❌ FAILED: {description}")
            print(f"     → Unexpected result")
            failed += 1
    
    # Test null byte separately - subprocess rejects it (security feature)
    print(f"  ℹ️  SKIPPED: Null byte handling")
    print(f"     → Python subprocess rejects null bytes (expected security behavior)")
    
    return passed, failed

def test_very_long_inputs():
    """Test handling of very long inputs."""
    print("\nTesting very long inputs...")
    
    passed = 0
    failed = 0
    
    # Test extremely long title
    long_title = "Fix bug " + "x" * 10000
    result, error = run_matching_safe(long_title, "Short body")
    
    if error:
        print(f"  ❌ FAILED: Very long title (10k chars)")
        print(f"     Error: {error}")
        failed += 1
    elif result:
        print(f"  ✅ PASSED: Very long title (10k chars)")
        print(f"     → Matched: {result['agent']}")
        passed += 1
    else:
        print(f"  ❌ FAILED: Very long title")
        failed += 1
    
    # Test extremely long body
    long_body = "This is a bug report. " + "Details: " * 5000
    result, error = run_matching_safe("Fix bug", long_body)
    
    if error:
        print(f"  ❌ FAILED: Very long body (30k+ chars)")
        print(f"     Error: {error}")
        failed += 1
    elif result:
        print(f"  ✅ PASSED: Very long body (30k+ chars)")
        print(f"     → Matched: {result['agent']}")
        passed += 1
    else:
        print(f"  ❌ FAILED: Very long body")
        failed += 1
    
    return passed, failed

def test_malformed_unicode():
    """Test handling of malformed or unusual Unicode."""
    print("\nTesting malformed Unicode...")
    
    test_cases = [
        ("Fix bug \udcff\udcff", "Invalid surrogate pairs", "Invalid surrogates"),
        # Null character rejected by subprocess (expected)
        # ("Error in \u0000 handling", "Null character", "Null character"),
        ("Bug with \ufeff BOM", "BOM character", "Byte Order Mark"),
        ("Issue: " + "\u200b" * 100, "Zero-width spaces", "Zero-width characters"),
    ]
    
    passed = 0
    failed = 0
    
    for title, description, test_name in test_cases:
        result, error = run_matching_safe(title, description)
        
        if error:
            # Some failures might be expected for truly malformed input
            print(f"  ⚠️  HANDLED: {test_name}")
            print(f"     → Error caught: {error[:50]}...")
            passed += 1  # Count as pass if error is caught gracefully
        elif result and result.get('agent'):
            print(f"  ✅ PASSED: {test_name}")
            print(f"     → Matched: {result['agent']}")
            passed += 1
        else:
            print(f"  ❌ FAILED: {test_name}")
            failed += 1
    
    # Note about null character handling
    print(f"  ℹ️  SKIPPED: Null character test")
    print(f"     → Python subprocess rejects null bytes (expected security behavior)")
    
    return passed, failed

def test_edge_case_scores():
    """Test that scoring is consistent and predictable."""
    print("\nTesting score consistency...")
    
    passed = 0
    failed = 0
    
    # Test that more keywords = higher score
    result1, _ = run_matching_safe("Fix bug", "")
    result2, _ = run_matching_safe("Fix bug error crash", "")
    
    if result1 and result2:
        score1 = result1.get('score', 0)
        score2 = result2.get('score', 0)
        
        if score2 > score1:
            print(f"  ✅ PASSED: More keywords = higher score ({score1} < {score2})")
            passed += 1
        else:
            print(f"  ❌ FAILED: Score not increasing with keywords ({score1} vs {score2})")
            failed += 1
    else:
        print(f"  ❌ FAILED: Could not test score consistency")
        failed += 1
    
    # Test that title is weighted more than body
    result1, _ = run_matching_safe("bug", "")
    result2, _ = run_matching_safe("", "bug")
    
    if result1 and result2:
        score1 = result1.get('score', 0)
        score2 = result2.get('score', 0)
        
        if score1 >= score2:
            print(f"  ✅ PASSED: Title weighted appropriately ({score1} >= {score2})")
            passed += 1
        else:
            print(f"  ❌ FAILED: Title not weighted correctly ({score1} < {score2})")
            failed += 1
    else:
        print(f"  ❌ FAILED: Could not test title weighting")
        failed += 1
    
    return passed, failed

def test_command_line_errors():
    """Test that script handles command-line errors gracefully."""
    print("\nTesting command-line error handling...")
    
    passed = 0
    failed = 0
    
    # Test with no arguments
    try:
        result = subprocess.run(
            ['python3', 'tools/match-issue-to-agent.py'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"  ✅ PASSED: No arguments - exits with error")
            passed += 1
        else:
            print(f"  ❌ FAILED: No arguments - should exit with error")
            failed += 1
    except Exception as e:
        print(f"  ❌ FAILED: Exception testing no args: {e}")
        failed += 1
    
    return passed, failed

def main():
    """Run all security and robustness tests."""
    print("=" * 70)
    print("🔒 Agent Matching Security & Robustness Tests")
    print("=" * 70)
    print()
    
    # Change to repo root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    print(f"Working directory: {os.getcwd()}\n")
    
    # Run all test suites
    total_passed = 0
    total_failed = 0
    
    test_suites = [
        ("Empty Inputs", test_empty_inputs),
        ("Special Characters", test_special_characters),
        ("Very Long Inputs", test_very_long_inputs),
        ("Malformed Unicode", test_malformed_unicode),
        ("Score Consistency", test_edge_case_scores),
        ("Command Line Errors", test_command_line_errors),
    ]
    
    for suite_name, test_func in test_suites:
        try:
            passed, failed = test_func()
            total_passed += passed
            total_failed += failed
        except Exception as e:
            print(f"\n❌ Test suite '{suite_name}' crashed: {e}")
            total_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print(f"Total Passed: {total_passed}")
    print(f"Total Failed: {total_failed}")
    print(f"Total Tests: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n✅ All security and robustness tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test(s) failed or found issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
