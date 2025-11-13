#!/usr/bin/env python3
"""
Test script to validate the assert-specialist agent definition.
This test ensures the agent is properly configured and follows conventions.
"""

import sys
import yaml
from pathlib import Path

def print_test(name):
    """Print test name."""
    print(f"\n🧪 Testing: {name}")
    print("-" * 60)

def test_agent_file_exists():
    """Test that assert-specialist.md exists."""
    print_test("Assert Specialist Agent File Exists")
    
    agent_path = Path('.github/agents/assert-specialist.md')
    
    if not agent_path.exists():
        print("❌ FAILED: assert-specialist.md not found")
        return False
    
    print("✅ PASSED: assert-specialist.md exists")
    return True

def test_agent_yaml_frontmatter():
    """Test that agent has valid YAML frontmatter."""
    print_test("Assert Specialist YAML Frontmatter")
    
    agent_path = Path('.github/agents/assert-specialist.md')
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    if not content.startswith('---'):
        print("❌ FAILED: Missing YAML frontmatter")
        return False
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        print("❌ FAILED: Invalid YAML frontmatter structure")
        return False
    
    try:
        data = yaml.safe_load(parts[1])
        
        # Check required fields
        if 'name' not in data:
            print("❌ FAILED: Missing 'name' field")
            return False
        
        if data['name'] != 'assert-specialist':
            print(f"❌ FAILED: Name should be 'assert-specialist', got '{data['name']}'")
            return False
        
        if 'description' not in data:
            print("❌ FAILED: Missing 'description' field")
            return False
        
        # Check description mentions key aspects
        desc = data['description'].lower()
        if 'assert' not in desc and 'coverage' not in desc:
            print("❌ FAILED: Description should mention 'assert' or 'coverage'")
            return False
        
        if 'leslie lamport' not in desc:
            print("❌ FAILED: Description should mention 'Leslie Lamport'")
            return False
        
        if 'tools' not in data:
            print("⚠️  WARNING: No tools specified")
        elif not isinstance(data['tools'], list):
            print("❌ FAILED: 'tools' should be a list")
            return False
        
        print("✅ PASSED: YAML frontmatter is valid")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ FAILED: YAML parsing error: {e}")
        return False

def test_agent_markdown_content():
    """Test that agent has proper markdown content."""
    print_test("Assert Specialist Markdown Content")
    
    agent_path = Path('.github/agents/assert-specialist.md')
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        print("❌ FAILED: Missing markdown body")
        return False
    
    body = parts[2].strip()
    
    if not body:
        print("❌ FAILED: Markdown body is empty")
        return False
    
    # Check for key sections
    required_sections = [
        'Core Responsibilities',
        'Approach',
        'Code Quality Standards',
        'Performance Tracking'
    ]
    
    missing_sections = []
    for section in required_sections:
        if section.lower() not in body.lower():
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ FAILED: Missing sections: {', '.join(missing_sections)}")
        return False
    
    # Check for agent-specific content
    body_lower = body.lower()
    
    # Should mention assertions
    if 'assert' not in body_lower:
        print("❌ FAILED: Body should mention 'assert' or assertions")
        return False
    
    # Should mention testing/quality assurance
    if 'test' not in body_lower and 'quality' not in body_lower:
        print("❌ FAILED: Body should mention testing or quality assurance")
        return False
    
    # Should mention edge cases
    if 'edge case' not in body_lower:
        print("❌ FAILED: Body should mention edge cases")
        return False
    
    print("✅ PASSED: Markdown content is valid")
    return True

def test_agent_in_readme():
    """Test that agent is listed in README."""
    print_test("Assert Specialist in README")
    
    readme_path = Path('.github/agents/README.md')
    
    if not readme_path.exists():
        print("❌ FAILED: README.md not found")
        return False
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    if 'assert-specialist.md' not in content:
        print("❌ FAILED: assert-specialist.md not mentioned in README")
        return False
    
    if 'assert' not in content.lower() or 'specialist' not in content.lower():
        print("❌ FAILED: README doesn't describe assert-specialist")
        return False
    
    print("✅ PASSED: Agent is listed in README")
    return True

def test_leslie_lamport_inspiration():
    """Test that agent properly references Leslie Lamport inspiration."""
    print_test("Leslie Lamport Inspiration")
    
    agent_path = Path('.github/agents/assert-specialist.md')
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    content_lower = content.lower()
    
    if 'leslie lamport' not in content_lower:
        print("❌ FAILED: Should reference Leslie Lamport")
        return False
    
    # Check for specification-driven approach
    if 'specification' not in content_lower:
        print("⚠️  WARNING: Should mention specification-driven approach")
    
    # Check for systematic approach
    if 'systematic' not in content_lower:
        print("⚠️  WARNING: Should mention systematic approach")
    
    print("✅ PASSED: Leslie Lamport inspiration properly referenced")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing Assert Specialist Agent Definition")
    print("=" * 60)
    
    tests = [
        test_agent_file_exists,
        test_agent_yaml_frontmatter,
        test_agent_markdown_content,
        test_agent_in_readme,
        test_leslie_lamport_inspiration
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
