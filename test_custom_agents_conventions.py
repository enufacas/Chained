#!/usr/bin/env python3
"""
Test script to validate GitHub Copilot custom agents conventions.

This script verifies that all custom agents in .github/agents/ follow
the official GitHub Copilot conventions as defined at:
https://docs.github.com/en/copilot/reference/custom-agents-configuration

Requirements:
1. Agents must be in .github/agents/ directory
2. Each agent is a Markdown file with .md extension
3. Each file must have YAML frontmatter with:
   - Required: name (kebab-case identifier)
   - Required: description (clear purpose statement)
   - Optional: tools (list of tools agent can use)
   - Optional: mcp-servers (MCP server configuration)
4. Each file must have markdown content after frontmatter
5. Files must be committed to default branch
"""

import os
import re
import sys
import yaml
from pathlib import Path

# Convention constants from GitHub documentation
AGENT_DIRECTORY = '.github/agents'
FILE_EXTENSION = '.md'
REQUIRED_FIELDS = ['name', 'description']
OPTIONAL_FIELDS = ['tools', 'mcp-servers']
NAME_PATTERN = r'^[a-z][a-z0-9-]*$'  # kebab-case


class ConventionError(Exception):
    """Exception raised for convention violations."""
    pass


def test_directory_structure():
    """Test that .github/agents/ directory exists."""
    print("\n📋 Testing: Directory Structure")
    print("-" * 50)
    
    agent_dir = Path(AGENT_DIRECTORY)
    if not agent_dir.exists():
        raise ConventionError(f"Directory '{AGENT_DIRECTORY}' does not exist")
    
    if not agent_dir.is_dir():
        raise ConventionError(f"'{AGENT_DIRECTORY}' exists but is not a directory")
    
    print(f"✅ Directory '{AGENT_DIRECTORY}' exists")
    return True


def test_agent_files_exist():
    """Test that agent files exist and have correct extension."""
    print("\n📋 Testing: Agent Files")
    print("-" * 50)
    
    agent_dir = Path(AGENT_DIRECTORY)
    md_files = list(agent_dir.glob('*.md'))
    agent_files = [f for f in md_files if f.name != 'README.md']
    
    if not agent_files:
        raise ConventionError("No agent files found (excluding README.md)")
    
    print(f"✅ Found {len(agent_files)} agent file(s)")
    for f in agent_files:
        print(f"   • {f.name}")
    
    return agent_files


def test_yaml_frontmatter(filepath):
    """Test that file has valid YAML frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for frontmatter delimiters
    if not content.startswith('---\n'):
        raise ConventionError(f"{filepath.name}: File must start with '---' for YAML frontmatter")
    
    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        raise ConventionError(f"{filepath.name}: Invalid YAML frontmatter structure")
    
    # Parse YAML
    try:
        frontmatter = yaml.safe_load(match.group(1))
        if frontmatter is None:
            frontmatter = {}
    except yaml.YAMLError as e:
        raise ConventionError(f"{filepath.name}: Invalid YAML syntax - {e}")
    
    return frontmatter, content[match.end():]


def test_required_fields(filepath, frontmatter):
    """Test that required fields are present and valid."""
    filename = filepath.name
    
    # Check required fields exist
    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            raise ConventionError(f"{filename}: Missing required field '{field}'")
        
        value = frontmatter[field]
        if not value:
            raise ConventionError(f"{filename}: Required field '{field}' is empty")
        
        if not isinstance(value, str):
            raise ConventionError(f"{filename}: Field '{field}' must be a string")
    
    # Validate name format (kebab-case)
    name = frontmatter['name']
    if not re.match(NAME_PATTERN, name):
        raise ConventionError(
            f"{filename}: Name '{name}' must be kebab-case (lowercase letters, numbers, hyphens only, start with letter)"
        )
    
    # Check name matches filename
    expected_name = filename[:-3]  # Remove .md extension
    if name != expected_name:
        print(f"   ⚠️  {filename}: Name '{name}' doesn't match filename (expected '{expected_name}')")
    
    # Validate description is meaningful
    description = frontmatter['description']
    if len(description) < 10:
        print(f"   ⚠️  {filename}: Description is very short ({len(description)} chars)")


def test_optional_fields(filepath, frontmatter):
    """Test that optional fields, if present, are valid."""
    filename = filepath.name
    
    # Validate tools field
    if 'tools' in frontmatter:
        tools = frontmatter['tools']
        if not isinstance(tools, (list, str)):
            raise ConventionError(f"{filename}: Field 'tools' must be a list or string")
        
        if isinstance(tools, list):
            for i, tool in enumerate(tools):
                if not isinstance(tool, str):
                    raise ConventionError(f"{filename}: Tool at index {i} must be a string")
    
    # Validate mcp-servers field
    if 'mcp-servers' in frontmatter:
        if not isinstance(frontmatter['mcp-servers'], dict):
            raise ConventionError(f"{filename}: Field 'mcp-servers' must be an object/mapping")


def test_markdown_body(filepath, body):
    """Test that file has content after frontmatter."""
    filename = filepath.name
    
    body = body.strip()
    if not body:
        raise ConventionError(f"{filename}: File has no content after YAML frontmatter")
    
    if len(body) < 100:
        print(f"   ⚠️  {filename}: Markdown body is very short ({len(body)} chars)")


def test_single_agent(filepath):
    """Run all tests for a single agent file."""
    # Test YAML frontmatter
    frontmatter, body = test_yaml_frontmatter(filepath)
    
    # Test required fields
    test_required_fields(filepath, frontmatter)
    
    # Test optional fields
    test_optional_fields(filepath, frontmatter)
    
    # Test markdown body
    test_markdown_body(filepath, body)
    
    return {
        'name': frontmatter.get('name', 'UNKNOWN'),
        'description': frontmatter.get('description', ''),
        'tools': len(frontmatter.get('tools', [])) if isinstance(frontmatter.get('tools'), list) else 'N/A',
        'body_length': len(body.strip())
    }


def test_all_agents():
    """Test all agent files for convention compliance."""
    print("\n📋 Testing: Agent File Conventions")
    print("-" * 50)
    
    agent_files = test_agent_files_exist()
    
    results = []
    errors = []
    
    for filepath in sorted(agent_files):
        try:
            result = test_single_agent(filepath)
            results.append({'file': filepath.name, **result})
            print(f"✅ {filepath.name}")
        except ConventionError as e:
            errors.append(str(e))
            print(f"❌ {filepath.name}: {e}")
    
    if errors:
        raise ConventionError(f"Found {len(errors)} convention violation(s)")
    
    return results


def test_agent_summary(results):
    """Print summary of all agents."""
    print("\n📋 Testing: Agent Summary")
    print("-" * 50)
    
    for result in results:
        print(f"\n{result['file']}:")
        print(f"  Name: {result['name']}")
        print(f"  Description: {result['description'][:60]}...")
        print(f"  Tools: {result['tools']}")
        print(f"  Body: {result['body_length']} chars")
    
    print(f"\n✅ All {len(results)} agents follow conventions")
    return True


def main():
    """Run all convention tests."""
    print("=" * 50)
    print("🧪 Testing GitHub Copilot Custom Agents Conventions")
    print("=" * 50)
    print(f"\nReference: https://docs.github.com/en/copilot/reference/custom-agents-configuration")
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("All Agent Files", test_all_agents),
    ]
    
    passed = 0
    failed = 0
    results = None
    
    for name, test_func in tests:
        try:
            result = test_func()
            if name == "All Agent Files":
                results = result
            passed += 1
        except ConventionError as e:
            print(f"\n❌ Test Failed: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ Test Failed: {name}")
            print(f"   Unexpected error: {e}")
            failed += 1
    
    # Show summary if we have results
    if results:
        try:
            test_agent_summary(results)
        except Exception as e:
            print(f"\n❌ Summary generation failed: {e}")
    
    # Print final summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"\nPassed: {passed}/{passed + failed}")
    
    if failed == 0:
        print("\n✅ All tests passed!")
        print("\n🎉 Custom agents follow GitHub Copilot conventions:")
        print(f"   • Located in {AGENT_DIRECTORY}/ directory")
        print("   • Markdown files with .md extension")
        print("   • Valid YAML frontmatter with required fields")
        print("   • Proper kebab-case naming")
        print("   • Custom instructions in markdown body")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        print("\n⚠️  Please fix convention violations before committing")
        return 1


if __name__ == '__main__':
    sys.exit(main())
