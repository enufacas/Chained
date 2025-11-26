#!/usr/bin/env python3
"""
Test A2A agent card generation for all Chained agents.
Phase 2B: Testing & Integration
"""

import sys
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.a2a import generate_agent_card, generate_all_agent_cards


def test_agent_card_generation():
    """Test that all agents can generate valid A2A cards."""
    print("=" * 60)
    print("Testing A2A Agent Card Generation")
    print("=" * 60)
    
    all_cards = generate_all_agent_cards()
    agents = list(all_cards.keys())
    total = len(agents)
    print(f"\n📊 Found {total} agents to test\n")
    
    success_count = 0
    failed_agents = []
    
    for i, agent_name in enumerate(agents, 1):
        try:
            card = generate_agent_card(agent_name)
            
            # Validate card structure
            assert card.name == agent_name, f"Card name mismatch: {card.name} != {agent_name}"
            assert card.url, "Card missing URL"
            assert card.url.startswith("http://localhost:"), f"Invalid URL: {card.url}"
            assert card.skills, f"Agent {agent_name} has no skills"
            assert len(card.skills) > 0, f"Agent {agent_name} has empty skills list"
            
            # Validate skills structure
            for skill in card.skills:
                assert skill.id, f"Skill missing ID for agent {agent_name}"
                assert skill.name, f"Skill missing name for agent {agent_name}"
                assert skill.description, f"Skill missing description for agent {agent_name}"
            
            success_count += 1
            if i % 10 == 0:
                print(f"✅ Tested {i}/{total} agents...")
        except Exception as e:
            failed_agents.append((agent_name, str(e)))
            print(f"❌ Failed: {agent_name} - {e}")
    
    print(f"\n{'=' * 60}")
    print(f"📊 Results: {success_count}/{total} agents passed")
    
    if failed_agents:
        print(f"\n❌ {len(failed_agents)} agents failed:")
        for agent, error in failed_agents:
            print(f"  - {agent}: {error}")
        return False
    
    print(f"\n✅ All {total} agent cards generated successfully!")
    return True


def test_agent_card_consistency():
    """Test that agent cards have consistent port assignments."""
    print("\n" + "=" * 60)
    print("Testing Agent Card Port Consistency")
    print("=" * 60)
    
    all_cards = generate_all_agent_cards()
    agents = list(all_cards.keys())[:20]  # Test subset for speed
    print(f"\n📊 Testing {len(agents)} agents for consistency\n")
    
    # Generate cards twice and verify ports are the same
    first_run = {}
    second_run = {}
    
    for agent_name in agents:
        card1 = generate_agent_card(agent_name)
        card2 = generate_agent_card(agent_name)
        
        first_run[agent_name] = card1.url
        second_run[agent_name] = card2.url
        
        assert card1.url == card2.url, f"Port inconsistent for {agent_name}"
    
    print("✅ All agents have consistent port assignments")
    print(f"\nExample port assignments:")
    for agent, url in list(first_run.items())[:5]:
        print(f"  {agent:25} → {url}")
    
    return True


def test_agent_card_uniqueness():
    """Test that agent cards have unique ports."""
    print("\n" + "=" * 60)
    print("Testing Agent Card Port Uniqueness")
    print("=" * 60)
    
    all_cards = generate_all_agent_cards()
    agents = list(all_cards.keys())
    print(f"\n📊 Testing {len(agents)} agents for unique ports\n")
    
    port_map = {}
    duplicates = []
    
    for agent_name in agents:
        card = generate_agent_card(agent_name)
        port = card.url.split(":")[-1].rstrip("/")
        
        if port in port_map:
            duplicates.append((agent_name, port_map[port], port))
        else:
            port_map[port] = agent_name
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} port collisions:")
        for agent, original, port in duplicates[:5]:
            print(f"  Port {port}: {original} and {agent}")
        return False
    
    print(f"✅ All {len(agents)} agents have unique ports")
    print(f"   Port range: {min(port_map.keys())} - {max(port_map.keys())}")
    
    return True


if __name__ == "__main__":
    print("\n🧪 A2A Agent Card Tests - Phase 2B\n")
    
    all_passed = True
    
    # Run all tests
    all_passed &= test_agent_card_generation()
    all_passed &= test_agent_card_consistency()
    all_passed &= test_agent_card_uniqueness()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
