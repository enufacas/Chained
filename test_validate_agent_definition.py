#!/usr/bin/env python3
"""
Tests for validate-agent-definition.py tool
"""

import sys
import os
import subprocess
from pathlib import Path
import tempfile
import shutil

def print_test(name):
    """Print test name."""
    print(f"\n🧪 Testing: {name}")
    print("-" * 60)

def test_valid_directory():
    """Test validation of all agent definitions."""
    print_test("Valid agent directory")
    
    result = subprocess.run(
        ['python3', 'tools/validate-agent-definition.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ PASSED: All agents validated successfully")
        return True
    else:
        print("❌ FAILED: Agent validation failed")
        print(result.stdout)
        print(result.stderr)
        return False

def test_single_file():
    """Test validation of a single agent file."""
    print_test("Single file validation")
    
    result = subprocess.run(
        ['python3', 'tools/validate-agent-definition.py', '-f', '.github/agents/create-guru.md'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ PASSED: Single file validated successfully")
        return True
    else:
        print("❌ FAILED: Single file validation failed")
        print(result.stdout)
        print(result.stderr)
        return False

def test_invalid_file():
    """Test validation of an invalid agent file."""
    print_test("Invalid file detection")
    
    # Create temporary invalid agent file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Agent without frontmatter\nThis is invalid.")
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python3', 'tools/validate-agent-definition.py', '-f', temp_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("✅ PASSED: Invalid file correctly detected")
            return True
        else:
            print("❌ FAILED: Invalid file not detected")
            return False
    finally:
        os.unlink(temp_file)

def test_help():
    """Test help flag."""
    print_test("Help flag")
    
    result = subprocess.run(
        ['python3', 'tools/validate-agent-definition.py', '--help'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and 'usage:' in result.stdout:
        print("✅ PASSED: Help message displayed correctly")
        return True
    else:
        print("❌ FAILED: Help message not displayed")
        return False

def test_agent_count():
    """Test that correct number of agents are found."""
    print_test("Agent count verification")
    
    result = subprocess.run(
        ['python3', 'tools/validate-agent-definition.py'],
        capture_output=True,
        text=True
    )
    
    # Check that output includes expected number of agents (at least 15)
    if 'Found 15 agent definition(s)' in result.stdout or 'Total agents: 15' in result.stdout:
        print("✅ PASSED: Correct number of agents found (15)")
        return True
    else:
        print("❌ FAILED: Unexpected number of agents")
        print(result.stdout)
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing validate-agent-definition.py Tool")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    
    tests = [
        test_valid_directory,
        test_single_file,
        test_invalid_file,
        test_help,
        test_agent_count
    ]
    
    results = [test() for test in tests]
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"\nPassed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {len(results) - sum(results)} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
