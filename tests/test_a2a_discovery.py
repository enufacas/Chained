#!/usr/bin/env python3
"""
Test A2A discovery service functionality.
Phase 2B: Testing & Integration
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.a2a import get_discovery_service, generate_agent_card


async def test_discovery_registration():
    """Test agent registration in discovery service."""
    print("=" * 60)
    print("Testing Discovery Service Registration")
    print("=" * 60)
    
    # Create discovery service with temp registry
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Initialize with empty registry
        import json
        json.dump({"agents": {}, "last_updated": ""}, f)
        temp_registry = Path(f.name)
    
    try:
        discovery = get_discovery_service(registry_file=temp_registry)
        
        # Register a few test agents
        test_agents = ["engineer-master", "secure-specialist", "organize-guru"]
        print(f"\n📊 Registering {len(test_agents)} test agents\n")
        
        for agent_name in test_agents:
            card = generate_agent_card(agent_name)
            await discovery.register_agent(card)
            print(f"✅ Registered: {agent_name}")
        
        # Verify they're registered
        for agent_name in test_agents:
            card = await discovery.get_agent(agent_name)
            assert card is not None, f"Agent {agent_name} not found"
            assert card.name == agent_name, f"Name mismatch for {agent_name}"
        
        print(f"\n✅ All {len(test_agents)} agents registered and retrieved successfully")
        return True
        
    finally:
        # Cleanup
        Path(temp_registry).unlink(missing_ok=True)


async def test_discovery_skill_search():
    """Test skill-based agent discovery."""
    print("\n" + "=" * 60)
    print("Testing Skill-Based Discovery")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Initialize with empty registry
        import json
        json.dump({"agents": {}, "last_updated": ""}, f)
        temp_registry = Path(f.name)
    
    try:
        discovery = get_discovery_service(registry_file=temp_registry)
        
        # Register agents with known skills
        test_agents = [
            "engineer-master",      # Engineering APIs
            "secure-specialist",    # Security
            "troubleshoot-expert",  # Troubleshooting
        ]
        
        print(f"\n📊 Registering {len(test_agents)} agents\n")
        for agent_name in test_agents:
            card = generate_agent_card(agent_name)
            await discovery.register_agent(card)
            print(f"✅ Registered: {agent_name} - {len(card.skills)} skill(s)")
        
        # Test discovery by skill patterns
        print("\n🔍 Testing skill-based queries:\n")
        
        # Query for engineering
        engineers = await discovery.discover_agents(skill="engineer")
        print(f"  'engineer' → {len(engineers)} match(es)")
        assert len(engineers) > 0, "Should find engineering agents"
        
        # Query for security
        security = await discovery.discover_agents(skill="secure")
        print(f"  'secure' → {len(security)} match(es)")
        assert len(security) > 0, "Should find security agents"
        
        # Query for troubleshooting
        trouble = await discovery.discover_agents(skill="troubleshoot")
        print(f"  'troubleshoot' → {len(trouble)} match(es)")
        assert len(trouble) > 0, "Should find troubleshooting agents"
        
        print(f"\n✅ Skill-based discovery working correctly")
        return True
        
    finally:
        Path(temp_registry).unlink(missing_ok=True)


async def test_discovery_auto_register():
    """Test auto-registration of all agents."""
    print("\n" + "=" * 60)
    print("Testing Auto-Registration")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Initialize with empty registry
        import json
        json.dump({"agents": {}, "last_updated": ""}, f)
        temp_registry = Path(f.name)
    
    try:
        discovery = get_discovery_service(registry_file=temp_registry)
        
        print("\n📊 Auto-registering all agents...\n")
        count = await discovery.auto_register_all_agents()
        
        print(f"✅ Auto-registered {count} agents")
        assert count > 0, "Should register at least one agent"
        
        # Verify some agents are accessible
        test_samples = ["engineer-master", "secure-specialist", "organize-guru"]
        for agent_name in test_samples:
            card = await discovery.get_agent(agent_name)
            if card:
                print(f"  ✓ Verified: {agent_name}")
        
        print(f"\n✅ Auto-registration successful")
        return True
        
    finally:
        Path(temp_registry).unlink(missing_ok=True)


async def test_discovery_persistence():
    """Test that registry persists between service instances."""
    print("\n" + "=" * 60)
    print("Testing Registry Persistence")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        # Initialize with empty registry
        import json
        json.dump({"agents": {}, "last_updated": ""}, f)
        temp_registry = Path(f.name)
    
    try:
        # First instance - register agents
        discovery1 = get_discovery_service(registry_file=temp_registry)
        card = generate_agent_card("engineer-master")
        await discovery1.register_agent(card)
        print("\n✅ Instance 1: Registered engineer-master")
        
        # Second instance - should load from disk
        discovery2 = get_discovery_service(registry_file=temp_registry)
        loaded_card = await discovery2.get_agent("engineer-master")
        
        assert loaded_card is not None, "Agent not persisted"
        assert loaded_card.name == "engineer-master", "Wrong agent loaded"
        
        print("✅ Instance 2: Loaded engineer-master from disk")
        print("\n✅ Registry persistence working correctly")
        return True
        
    finally:
        Path(temp_registry).unlink(missing_ok=True)


async def run_all_tests():
    """Run all discovery tests."""
    print("\n🧪 A2A Discovery Service Tests - Phase 2B\n")
    
    all_passed = True
    
    try:
        all_passed &= await test_discovery_registration()
        all_passed &= await test_discovery_skill_search()
        all_passed &= await test_discovery_auto_register()
        all_passed &= await test_discovery_persistence()
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
