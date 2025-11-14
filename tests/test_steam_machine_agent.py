#!/usr/bin/env python3
"""
Test Steam Machine Specialist Agent

Validates that the learning-based Steam Machine agent was correctly
created and integrated into the system.
"""

import json
import os
from pathlib import Path


def test_agent_definition_exists():
    """Test that the agent definition file exists."""
    agent_file = Path('.github/agents/steam-machine.md')
    assert agent_file.exists(), "Agent definition file not found"
    print("✅ Agent definition file exists")


def test_agent_definition_valid():
    """Test that the agent definition has correct structure."""
    agent_file = Path('.github/agents/steam-machine.md')
    content = agent_file.read_text()
    
    # Check frontmatter
    assert '---' in content, "Missing YAML frontmatter"
    assert 'name: steam-machine' in content, "Missing agent name"
    assert 'description:' in content, "Missing description"
    assert 'tools:' in content, "Missing tools list"
    
    # Check key content
    assert 'Steam Machine Specialist' in content, "Missing agent title"
    assert 'Grace Hopper' in content, "Missing inspiration"
    assert 'Learning-Based Origin' in content, "Missing learning origin section"
    assert 'gaming platform' in content.lower(), "Missing gaming focus"
    
    print("✅ Agent definition is valid")


def test_agent_registered():
    """Test that the agent is registered in the system."""
    registry_file = Path('.github/agent-system/registry.json')
    assert registry_file.exists(), "Registry file not found"
    
    with open(registry_file, 'r') as f:
        registry = json.load(f)
    
    # Find steam machine agent
    steam_agent = None
    for agent in registry['agents']:
        if agent['specialization'] == 'steam-machine':
            steam_agent = agent
            break
    
    assert steam_agent is not None, "Steam Machine agent not in registry"
    assert steam_agent['status'] == 'active', "Agent is not active"
    assert steam_agent['spawn_method'] == 'learning-based', "Wrong spawn method"
    assert steam_agent['inspiration_topic'] == 'Steam Machine', "Wrong topic"
    assert steam_agent['topic_score'] == 252.7, "Wrong topic score"
    
    print(f"✅ Agent registered: {steam_agent['name']}")
    print(f"   ID: {steam_agent['id']}")
    print(f"   Status: {steam_agent['status']}")


def test_agent_profile_exists():
    """Test that the agent profile was created."""
    profiles_dir = Path('.github/agent-system/profiles')
    
    # Find steam machine profile
    steam_profile = None
    for profile_file in profiles_dir.glob('*.md'):
        content = profile_file.read_text()
        if 'Steam Machine Specialist' in content:
            steam_profile = profile_file
            break
    
    assert steam_profile is not None, "Agent profile not found"
    
    content = steam_profile.read_text()
    assert 'Learning-Based Origin' in content, "Missing origin section"
    assert 'Grace Hopper' in content, "Missing inspiration"
    assert 'steam-machine' in content, "Missing specialization"
    
    print(f"✅ Agent profile exists: {steam_profile.name}")


def test_agent_in_readme():
    """Test that the agent is listed in the README."""
    readme_file = Path('.github/agents/README.md')
    content = readme_file.read_text()
    
    assert 'steam-machine.md' in content, "Agent not in README"
    assert '🎮' in content, "Missing gaming emoji"
    assert 'Learning-Based' in content, "Missing learning-based badge"
    
    print("✅ Agent listed in README")


def test_learning_based_attributes():
    """Test that learning-based attributes are correct."""
    registry_file = Path('.github/agent-system/registry.json')
    
    with open(registry_file, 'r') as f:
        registry = json.load(f)
    
    steam_agent = next(
        (a for a in registry['agents'] if a['specialization'] == 'steam-machine'),
        None
    )
    
    assert steam_agent is not None, "Agent not found"
    
    # Check learning-based specific attributes
    assert 'inspiration_topic' in steam_agent, "Missing inspiration topic"
    assert 'topic_score' in steam_agent, "Missing topic score"
    assert steam_agent['spawn_method'] == 'learning-based', "Not marked as learning-based"
    
    # Check personality traits
    assert 'personality' in steam_agent, "Missing personality"
    assert 'communication_style' in steam_agent, "Missing communication style"
    
    print("✅ Learning-based attributes are correct")


def test_agent_tools():
    """Test that the agent has appropriate tools."""
    agent_file = Path('.github/agents/steam-machine.md')
    content = agent_file.read_text()
    
    # Expected tools for gaming platform work
    expected_tools = ['view', 'edit', 'create', 'bash']
    
    for tool in expected_tools:
        assert f'- {tool}' in content, f"Missing tool: {tool}"
    
    print("✅ Agent has required tools")


def main():
    """Run all tests."""
    print("\n🧪 Testing Steam Machine Specialist Agent")
    print("=" * 60)
    
    tests = [
        test_agent_definition_exists,
        test_agent_definition_valid,
        test_agent_registered,
        test_agent_profile_exists,
        test_agent_in_readme,
        test_learning_based_attributes,
        test_agent_tools,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n📋 Testing: {test.__doc__.strip()}")
            print("-" * 60)
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Summary")
    print("=" * 60)
    print(f"\nPassed: {passed}/{passed + failed}")
    
    if failed > 0:
        print(f"\n❌ {failed} test(s) failed")
        return 1
    else:
        print("\n✅ 🎉 All tests passed!")
        return 0


if __name__ == '__main__':
    exit(main())
