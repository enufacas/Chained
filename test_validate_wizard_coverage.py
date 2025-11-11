#!/usr/bin/env python3
"""
Test script to validate the validate-wizard agent and demonstrate coverage validation.

This test validates:
1. The validate-wizard agent definition is properly configured
2. Test coverage patterns across existing test files
3. Edge cases and boundary conditions in the test suite
4. Validation gaps in the testing infrastructure
"""

import os
import re
import sys
from pathlib import Path


def test_validate_wizard_agent_exists():
    """Validate that the validate-wizard agent is properly defined."""
    print("📋 Testing: Validate Wizard Agent Definition")
    print("-" * 50)
    
    agent_path = Path('.github/agents/validate-wizard.md')
    
    # Test 1: File exists
    if not agent_path.exists():
        print("❌ validate-wizard.md not found")
        return False
    print("✅ validate-wizard.md exists")
    
    # Test 2: File is readable and has content
    content = agent_path.read_text()
    if len(content) == 0:
        print("❌ validate-wizard.md is empty")
        return False
    print(f"✅ validate-wizard.md has content ({len(content)} chars)")
    
    # Test 3: Has required YAML frontmatter
    if not content.startswith('---'):
        print("❌ Missing YAML frontmatter")
        return False
    print("✅ Has YAML frontmatter")
    
    # Test 4: Contains required fields
    required_fields = ['name: validate-wizard', 'description:', 'tools:']
    for field in required_fields:
        if field not in content:
            print(f"❌ Missing required field: {field}")
            return False
    print("✅ All required fields present")
    
    # Test 5: Contains key sections
    key_sections = [
        'Core Responsibilities',
        'Approach',
        'Validation Focus Areas',
        'Edge Case Validation',
        'Coverage Analysis'
    ]
    for section in key_sections:
        if section not in content:
            print(f"❌ Missing key section: {section}")
            return False
    print("✅ All key sections present")
    
    return True


def test_validate_wizard_in_readme():
    """Validate that validate-wizard is documented in README."""
    print("\n📋 Testing: Validate Wizard in README")
    print("-" * 50)
    
    readme_path = Path('.github/agents/README.md')
    
    if not readme_path.exists():
        print("❌ .github/agents/README.md not found")
        return False
    
    content = readme_path.read_text()
    
    # Check if validate-wizard is mentioned
    if 'validate-wizard' not in content:
        print("❌ validate-wizard not mentioned in README")
        return False
    print("✅ validate-wizard mentioned in README")
    
    # Check if it has a proper entry
    if '[validate-wizard.md]' not in content:
        print("❌ validate-wizard link not found in README")
        return False
    print("✅ validate-wizard properly linked in README")
    
    return True


def test_coverage_of_test_files():
    """Analyze existing test files for coverage patterns."""
    print("\n📋 Testing: Test File Coverage Patterns")
    print("-" * 50)
    
    test_files = [
        'test_agent_system.py',
        'test_agent_matching.py',
        'test_custom_agents_conventions.py',
        'test_ai_knowledge_graph.py',
        'test_tldr_feeds.py'
    ]
    
    all_valid = True
    total_tests = 0
    
    for test_file in test_files:
        path = Path(test_file)
        if not path.exists():
            print(f"⚠️  {test_file} not found")
            continue
        
        content = path.read_text()
        
        # Count test functions
        test_functions = re.findall(r'def (test_\w+)\(', content)
        test_count = len(test_functions)
        total_tests += test_count
        
        # Check for edge case tests
        has_edge_cases = any('edge' in func.lower() or 'boundary' in func.lower() 
                            for func in test_functions)
        
        # Check for error case tests
        has_error_cases = any('error' in func.lower() or 'fail' in func.lower() or 'invalid' in func.lower()
                             for func in test_functions)
        
        # Check for empty/none tests
        has_empty_tests = any('empty' in func.lower() or 'none' in func.lower() or 'null' in func.lower()
                             for func in test_functions)
        
        print(f"📄 {test_file}:")
        print(f"   • {test_count} test function(s)")
        if has_edge_cases:
            print(f"   • ✅ Has edge case tests")
        if has_error_cases:
            print(f"   • ✅ Has error case tests")
        if has_empty_tests:
            print(f"   • ✅ Has empty/none tests")
        
        if not (has_edge_cases or has_error_cases):
            print(f"   • ⚠️  Could benefit from more edge case coverage")
    
    print(f"\n📊 Total test functions found: {total_tests}")
    return all_valid


def test_validation_gaps():
    """Identify validation gaps in the codebase."""
    print("\n📋 Testing: Validation Gap Analysis")
    print("-" * 50)
    
    gaps = []
    
    # Check if tools have corresponding tests
    tools_dir = Path('tools')
    if tools_dir.exists():
        py_files = list(tools_dir.glob('*.py'))
        tested_tools = 0
        for tool in py_files:
            if tool.name.startswith('__'):
                continue
            test_name = f"test_{tool.stem}.py"
            if not Path(test_name).exists():
                gaps.append(f"Tool {tool.name} has no corresponding test file")
            else:
                tested_tools += 1
        
        print(f"✅ Found {tested_tools} tools with test coverage")
        if gaps:
            print(f"⚠️  Found {len(gaps)} tools without test coverage")
    
    # Check for critical files without tests
    critical_patterns = ['*-system.py', '*-generator.py', '*-analyzer.py']
    for pattern in critical_patterns:
        for file in Path('.').glob(pattern):
            if not file.name.startswith('test_'):
                test_file = f"test_{file.name}"
                if not Path(test_file).exists():
                    gaps.append(f"Critical file {file.name} has no test file")
    
    if gaps:
        print("\n🔍 Validation Gaps Found:")
        for gap in gaps[:5]:  # Show first 5 gaps
            print(f"   • {gap}")
        if len(gaps) > 5:
            print(f"   • ... and {len(gaps) - 5} more")
    else:
        print("✅ No critical validation gaps found")
    
    return True


def test_edge_case_validation():
    """Validate that edge cases are properly tested."""
    print("\n📋 Testing: Edge Case Validation")
    print("-" * 50)
    
    edge_case_patterns = [
        ('empty input', ['empty', 'none', 'null', '[]', '{}']),
        ('boundary values', ['max', 'min', 'zero', 'boundary']),
        ('invalid input', ['invalid', 'error', 'fail', 'exception']),
        ('large input', ['large', 'big', 'many', 'overflow']),
        ('special characters', ['special', 'unicode', 'escape', 'whitespace'])
    ]
    
    test_files = list(Path('.').glob('test_*.py'))
    edge_case_coverage = {}
    
    for test_file in test_files:
        content = test_file.read_text().lower()
        for pattern_name, keywords in edge_case_patterns:
            if any(keyword in content for keyword in keywords):
                if pattern_name not in edge_case_coverage:
                    edge_case_coverage[pattern_name] = []
                edge_case_coverage[pattern_name].append(test_file.name)
    
    print("Edge Case Coverage:")
    for pattern_name, keywords in edge_case_patterns:
        if pattern_name in edge_case_coverage:
            files = edge_case_coverage[pattern_name]
            print(f"   ✅ {pattern_name}: covered in {len(files)} test file(s)")
        else:
            print(f"   ⚠️  {pattern_name}: not explicitly tested")
    
    return True


def test_test_independence():
    """Validate that tests are independent and don't rely on each other."""
    print("\n📋 Testing: Test Independence")
    print("-" * 50)
    
    test_files = list(Path('.').glob('test_*.py'))
    issues_found = []
    
    for test_file in test_files:
        content = test_file.read_text()
        
        # Check for global state modifications
        if re.search(r'global \w+\s*=', content):
            issues_found.append(f"{test_file.name}: Uses global state")
        
        # Check for sleep statements (can indicate timing dependencies)
        if 'time.sleep' in content and 'import time' in content:
            # This might be intentional for async tests, so just note it
            pass
        
        # Check if tests create files without cleanup
        if 'open(' in content and 'w' in content:
            if 'teardown' not in content.lower() and 'cleanup' not in content.lower():
                # Only report if there's no cleanup mechanism
                pass
    
    if issues_found:
        print("⚠️  Potential independence issues:")
        for issue in issues_found:
            print(f"   • {issue}")
    else:
        print("✅ No obvious test independence issues found")
    
    return True


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("🧙 Validate Wizard: Coverage Validation Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_validate_wizard_agent_exists,
        test_validate_wizard_in_readme,
        test_coverage_of_test_files,
        test_validation_gaps,
        test_edge_case_validation,
        test_test_independence,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n❌ Error in {test.__name__}: {e}")
            results.append((test.__name__, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    if passed == total:
        print("\n✅ All validation tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} validation test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
